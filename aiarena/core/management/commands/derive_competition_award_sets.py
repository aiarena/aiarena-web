import hashlib
from collections import Counter, defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import (
    AwardSet,
    AwardSetItem,
    Competition,
    Trophy,
    TrophyIcon,
)


# Usage:
#
# Dry run:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py \
#     derive_competition_award_sets
#
# Apply changes:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py \
#     derive_competition_award_sets --apply
#
# Process one competition:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py \
#     derive_competition_award_sets --competition-id 3
#
# Process multiple competitions:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py \
#     derive_competition_award_sets \
#     --competition-id 3 \
#     --competition-id 8
#
# Replace an existing competition award set:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py \
#     derive_competition_award_sets --apply --overwrite
#
# Also mark competitions as having already received their awards:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py \
#     derive_competition_award_sets \
#     --apply \
#     --mark-awards-given


class Command(BaseCommand):
    help = "Derive competition AwardSets from existing competition trophies and their condition-to-icon mappings."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help=("Save changes. Without this option, the command performs a dry run."),
        )
        parser.add_argument(
            "--overwrite",
            action="store_true",
            help=("Replace Competition award_set values that are already populated."),
        )
        parser.add_argument(
            "--mark-awards-given",
            action="store_true",
            help=("Set awards_given=True for competitions assigned an award set."),
        )
        parser.add_argument(
            "--competition-id",
            type=int,
            action="append",
            dest="competition_ids",
            help=("Only process a specific competition ID. May be supplied multiple times."),
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        overwrite = options["overwrite"]
        mark_awards_given = options["mark_awards_given"]
        competition_ids = options["competition_ids"]

        competitions = Competition.objects.select_related(
            "award_set",
        ).order_by("id")

        if competition_ids:
            competitions = competitions.filter(id__in=competition_ids)

            found_ids = set(competitions.values_list("id", flat=True))
            missing_ids = set(competition_ids) - found_ids

            if missing_ids:
                raise CommandError(f"Competition IDs do not exist: {sorted(missing_ids)}")

        competitions = list(competitions)

        trophies = (
            Trophy.objects.filter(
                competition__in=competitions,
            )
            .select_related(
                "competition",
                "icon",
            )
            .order_by(
                "competition_id",
                "condition",
                "id",
            )
        )

        trophies_by_competition = defaultdict(list)

        for trophy in trophies:
            trophies_by_competition[trophy.competition_id].append(trophy)

        existing_sets_by_signature = self.get_existing_award_sets_by_signature()

        # Tracks sets planned or created during this command, allowing
        # identical mappings to reuse the same set.
        derived_sets_by_signature = {}

        counters = Counter()
        clear_mappings = []
        conflicts = []
        competitions_without_usable_trophies = []
        incomplete_trophies = []

        with transaction.atomic():
            for competition in competitions:
                counters["competitions_scanned"] += 1

                if competition.award_set_id and not overwrite:
                    counters["existing_award_set_skipped"] += 1

                    self.stdout.write(
                        f"Competition {competition.id}: "
                        f'"{competition.name}" already uses '
                        f'award set "{competition.award_set}".'
                    )
                    continue

                competition_trophies = trophies_by_competition.get(
                    competition.id,
                    [],
                )

                condition_icons = defaultdict(set)
                condition_trophies = defaultdict(lambda: defaultdict(list))

                for trophy in competition_trophies:
                    if not trophy.condition or trophy.icon_id is None:
                        incomplete_trophies.append(trophy)
                        counters["incomplete_trophies"] += 1
                        continue

                    condition_icons[trophy.condition].add(trophy.icon_id)

                    condition_trophies[trophy.condition][trophy.icon_id].append(trophy)

                if not condition_icons:
                    counters["without_usable_trophies"] += 1

                    competitions_without_usable_trophies.append(competition)
                    continue

                conflicting_conditions = {
                    condition: icon_ids for condition, icon_ids in condition_icons.items() if len(icon_ids) > 1
                }

                if conflicting_conditions:
                    counters["conflicting_competitions"] += 1

                    conflicts.append(
                        (
                            competition,
                            conflicting_conditions,
                            condition_trophies,
                        )
                    )
                    continue

                signature = tuple(
                    sorted(
                        (
                            condition,
                            next(iter(icon_ids)),
                        )
                        for condition, icon_ids in condition_icons.items()
                    )
                )

                award_set = existing_sets_by_signature.get(signature)

                source = "existing"

                if award_set is None:
                    award_set = derived_sets_by_signature.get(signature)
                    source = "derived"

                if award_set is None:
                    award_set = self.create_or_plan_award_set(
                        signature=signature,
                        apply_changes=apply_changes,
                    )

                    derived_sets_by_signature[signature] = award_set

                    source = "created"

                    counters["award_sets_created"] += 1
                    counters["award_set_items_created"] += len(signature)

                elif source == "existing":
                    counters["existing_award_sets_reused"] += 1

                else:
                    counters["derived_award_sets_reused"] += 1

                rendered_mapping = self.render_signature(signature)

                clear_mappings.append(
                    (
                        competition,
                        award_set,
                        rendered_mapping,
                    )
                )

                update_fields = []

                if apply_changes:
                    if competition.award_set_id != award_set.id:
                        competition.award_set = award_set
                        update_fields.append("award_set")

                    if mark_awards_given and not competition.awards_given:
                        competition.awards_given = True
                        update_fields.append("awards_given")

                    if update_fields:
                        competition.save(update_fields=update_fields)

                else:
                    # During a dry run, planned award sets are
                    # strings rather than saved model instances.
                    if competition.award_set_id is None or overwrite:
                        update_fields.append("award_set")

                    if mark_awards_given and not competition.awards_given:
                        update_fields.append("awards_given")

                if update_fields:
                    counters["competitions_would_update"] += 1
                else:
                    counters["competitions_unchanged"] += 1

            if not apply_changes:
                transaction.set_rollback(True)

        if clear_mappings:
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS("Competitions with clear trophies to map (add with --apply):"))

            for (
                competition,
                award_set,
                rendered_mapping,
            ) in clear_mappings:
                self.stdout.write(
                    f"  Competition {competition.id}: "
                    f'"{competition.name}" -> '
                    f"{self.get_award_set_name(award_set)} "
                    f"[{rendered_mapping}]"
                )

        mode = "APPLIED" if apply_changes else "DRY RUN"

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{mode} complete"))
        self.stdout.write(f"Competitions scanned: {counters['competitions_scanned']}")

        if apply_changes:
            self.stdout.write(f"Competitions updated: {counters['competitions_would_update']}")
        else:
            self.stdout.write(f"Competitions that would update: {counters['competitions_would_update']}")

        self.stdout.write(f"Competitions unchanged: {counters['competitions_unchanged']}")
        self.stdout.write(f"Existing award sets skipped: {counters['existing_award_set_skipped']}")

        if apply_changes:
            self.stdout.write(f"Award sets created: {counters['award_sets_created']}")
            self.stdout.write(f"Award set items created: {counters['award_set_items_created']}")
        else:
            self.stdout.write(f"Award sets that would be created: {counters['award_sets_created']}")
            self.stdout.write(f"Award set items that would be created: {counters['award_set_items_created']}")

        self.stdout.write(f"Existing award sets reused: {counters['existing_award_sets_reused']}")
        self.stdout.write(f"Newly derived award sets reused: {counters['derived_award_sets_reused']}")
        self.stdout.write(f"Competitions without usable trophies: {counters['without_usable_trophies']}")
        self.stdout.write(f"Competitions with conflicting mappings: {counters['conflicting_competitions']}")
        self.stdout.write(f"Incomplete trophies ignored: {counters['incomplete_trophies']}")

        if conflicts:
            self.stdout.write("")
            self.stdout.write(self.style.ERROR("Conflicting condition-to-icon mappings (would not apply):"))

            for (
                competition,
                conditions,
                condition_trophies,
            ) in conflicts:
                self.stdout.write(f'  Competition {competition.id}: "{competition.name}"')

                for condition, icon_ids in sorted(conditions.items()):
                    self.stdout.write(f"    {condition}:")

                    for icon_id in sorted(icon_ids):
                        trophies_for_icon = condition_trophies[condition][icon_id]

                        icon_name = (
                            trophies_for_icon[0].icon.name if trophies_for_icon[0].icon else f"icon_id={icon_id}"
                        )

                        trophy_ids = ", ".join(str(trophy.id) for trophy in trophies_for_icon)

                        self.stdout.write(f"      {icon_name}: trophy IDs {trophy_ids}")

        if competitions_without_usable_trophies:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Competitions without usable trophies:"))

            for competition in competitions_without_usable_trophies:
                self.stdout.write(f'  {competition.id}: "{competition.name}"')

        if incomplete_trophies:
            self.stdout.write("")
            self.stdout.write(self.style.WARNING("Ignored trophies missing a condition or icon:"))

            for trophy in incomplete_trophies:
                missing = []

                if not trophy.condition:
                    missing.append("condition")

                if trophy.icon_id is None:
                    missing.append("icon")

                self.stdout.write(f'  Trophy {trophy.id}: "{trophy.name}" missing {", ".join(missing)}')

        if not apply_changes:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("No records were changed. Run again with --apply to save the displayed updates.")
            )

    def get_existing_award_sets_by_signature(self):
        award_sets = AwardSet.objects.prefetch_related(
            "items",
            "items__trophy_icon",
        )

        result = {}

        for award_set in award_sets:
            signature = tuple(
                sorted(
                    (
                        item.condition,
                        item.trophy_icon_id,
                    )
                    for item in award_set.items.all()
                )
            )

            if signature:
                result.setdefault(signature, award_set)

        return result

    def create_or_plan_award_set(
        self,
        signature,
        apply_changes,
    ):
        digest = self.signature_digest(signature)
        base_name = f"Derived Competition Awards {digest}"

        if not apply_changes:
            return base_name

        award_set = self.create_unique_award_set(
            base_name=base_name,
            signature=signature,
        )

        AwardSetItem.objects.bulk_create(
            [
                AwardSetItem(
                    award_set=award_set,
                    condition=condition,
                    trophy_icon_id=icon_id,
                )
                for condition, icon_id in signature
            ]
        )

        return award_set

    def create_unique_award_set(
        self,
        base_name,
        signature,
    ):
        name = base_name
        suffix = 1

        while True:
            existing = (
                AwardSet.objects.prefetch_related(
                    "items",
                )
                .filter(
                    name=name,
                )
                .first()
            )

            if existing is None:
                return AwardSet.objects.create(
                    name=name,
                )

            existing_signature = tuple(
                sorted(
                    (
                        item.condition,
                        item.trophy_icon_id,
                    )
                    for item in existing.items.all()
                )
            )

            if existing_signature == signature:
                return existing

            suffix += 1
            suffix_text = f" {suffix}"
            name = f"{base_name[: 64 - len(suffix_text)]}{suffix_text}"

    @staticmethod
    def signature_digest(signature):
        serialized = "|".join(f"{condition}:{icon_id}" for condition, icon_id in signature)

        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:8]

    @staticmethod
    def get_award_set_name(award_set):
        if isinstance(award_set, str):
            return f'"{award_set}"'

        return f'"{award_set.name}"'

    @staticmethod
    def render_signature(signature):
        icon_names = {
            icon.id: icon.name
            for icon in TrophyIcon.objects.filter(id__in=[icon_id for _condition, icon_id in signature])
        }

        return ", ".join(f"{condition}={icon_names.get(icon_id, icon_id)}" for condition, icon_id in signature)
