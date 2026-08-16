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
from aiarena.core.models.trophy import TrophyCondition


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


class Command(BaseCommand):
    help = (
        "Conservatively derive competition AwardSets from existing "
        "competition participation trophies and their condition-to-icon mappings."
    )

    # Historical Trophy.condition values that are equivalent to current
    # canonical conditions.
    #
    # We only normalize aliases where the meaning is unambiguous.
    CONDITION_ALIASES = {
        # Historical podium aliases.
        "top_1": TrophyCondition.FIRST_PLACE,
        "top_2": TrophyCondition.SECOND_PLACE,
        "top_3": TrophyCondition.THIRD_PLACE,
        # Previous race-condition naming.
        "top_zerg": TrophyCondition.BEST_ZERG,
        "top_protoss": TrophyCondition.BEST_PROTOSS,
        "top_terran": TrophyCondition.BEST_TERRAN,
        "top_random": TrophyCondition.BEST_RANDOM,
        # Current canonical values map to themselves for clarity.
        "best_zerg": TrophyCondition.BEST_ZERG,
        "best_protoss": TrophyCondition.BEST_PROTOSS,
        "best_terran": TrophyCondition.BEST_TERRAN,
        "best_random": TrophyCondition.BEST_RANDOM,
    }

    # Conditions from which it is safe to derive an automatically managed
    # AwardSet.
    #
    # CUSTOM is deliberately excluded. A custom trophy's semantics cannot
    # be inferred from historical Trophy rows alone.
    DERIVABLE_CONDITIONS = {
        TrophyCondition.FIRST_PLACE,
        TrophyCondition.SECOND_PLACE,
        TrophyCondition.THIRD_PLACE,
        TrophyCondition.TOP_5,
        TrophyCondition.TOP_10,
        TrophyCondition.TOP_15,
        TrophyCondition.TOP_20,
        TrophyCondition.BEST_ZERG,
        TrophyCondition.BEST_PROTOSS,
        TrophyCondition.BEST_TERRAN,
        TrophyCondition.BEST_RANDOM,
        TrophyCondition.PARTICIPANT,
    }

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help=("Save changes. Without this option, the command performs a dry run."),
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
        competition_ids = options["competition_ids"]

        competitions = Competition.objects.select_related("award_set").order_by("id")

        if competition_ids:
            competitions = competitions.filter(id__in=competition_ids)

            found_ids = set(
                competitions.values_list(
                    "id",
                    flat=True,
                )
            )

            missing_ids = set(competition_ids) - found_ids

            if missing_ids:
                raise CommandError(f"Competition IDs do not exist: {sorted(missing_ids)}")

        competitions = list(competitions)

        trophies = (
            Trophy.objects.filter(
                competition_participation__competition__in=competitions,
            )
            .select_related(
                "competition_participation",
                "competition_participation__competition",
                "competition_participation__bot",
                "icon",
            )
            .order_by(
                "competition_participation__competition_id",
                "condition",
                "id",
            )
        )

        trophies_by_competition = defaultdict(list)

        for trophy in trophies:
            trophies_by_competition[trophy.competition_participation.competition_id].append(trophy)

        existing_sets_by_signature = self.get_existing_award_sets_by_signature()

        # Sets planned/created during this command. This allows identical
        # mappings to reuse one AwardSet.
        derived_sets_by_signature = {}

        counters = Counter()

        clear_mappings = []
        conflicts = []
        unsafe_competitions = []
        competitions_without_trophies = []

        with transaction.atomic():
            for competition in competitions:
                counters["competitions_scanned"] += 1

                # Never replace an award set that has already been assigned.
                if competition.award_set_id:
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

                if not competition_trophies:
                    counters["without_trophies"] += 1

                    competitions_without_trophies.append(competition)

                    continue

                (
                    condition_icons,
                    condition_trophies,
                    problems,
                ) = self.analyze_trophies(competition_trophies)

                # Be conservative: any uncertainty prevents deriving an
                # AwardSet for the entire competition.
                if problems:
                    counters["unsafe_competitions"] += 1

                    unsafe_competitions.append(
                        (
                            competition,
                            problems,
                        )
                    )

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

                if not signature:
                    counters["without_usable_trophies"] += 1
                    continue

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

                if apply_changes:
                    competition.award_set = award_set
                    competition.save(update_fields=["award_set"])

                counters["competitions_would_update"] += 1

            if not apply_changes:
                transaction.set_rollback(True)

        self.render_results(
            apply_changes=apply_changes,
            counters=counters,
            clear_mappings=clear_mappings,
            conflicts=conflicts,
            unsafe_competitions=unsafe_competitions,
            competitions_without_trophies=(competitions_without_trophies),
        )

    def analyze_trophies(
        self,
        trophies,
    ):
        """
        Analyze all trophies belonging to participations in one competition.

        This function deliberately rejects the entire competition if any
        linked trophy cannot be interpreted safely.
        """
        condition_icons = defaultdict(set)

        condition_trophies = defaultdict(lambda: defaultdict(list))

        problems = []

        for trophy in trophies:
            if not trophy.condition:
                problems.append(f'Trophy {trophy.id} "{trophy.name}" has no condition.')
                continue

            if trophy.icon_id is None:
                problems.append(f'Trophy {trophy.id} "{trophy.name}" has no icon.')
                continue

            condition = self.normalize_condition(trophy.condition)

            if condition not in self.DERIVABLE_CONDITIONS:
                problems.append(
                    f"Trophy {trophy.id} \"{trophy.name}\" uses unsupported condition '{trophy.condition}'."
                )
                continue

            condition_icons[condition].add(trophy.icon_id)

            condition_trophies[condition][trophy.icon_id].append(trophy)

        return (
            condition_icons,
            condition_trophies,
            problems,
        )

    @classmethod
    def normalize_condition(
        cls,
        condition,
    ):
        """
        Normalize known historical condition aliases.

        Examples:

            top_1       -> first_place
            top_2       -> second_place
            top_3       -> third_place

            top_zerg    -> best_zerg
            top_protoss -> best_protoss
            top_terran  -> best_terran
            top_random  -> best_random
        """
        return cls.CONDITION_ALIASES.get(
            condition,
            condition,
        )

    def get_existing_award_sets_by_signature(
        self,
    ):
        award_sets = AwardSet.objects.prefetch_related(
            "items",
            "items__trophy_icon",
        )

        result = {}

        for award_set in award_sets:
            conditions = []

            unsafe = False

            for item in award_set.items.all():
                condition = self.normalize_condition(item.condition)

                if condition not in self.DERIVABLE_CONDITIONS:
                    unsafe = True
                    break

                conditions.append(
                    (
                        condition,
                        item.trophy_icon_id,
                    )
                )

            if unsafe:
                continue

            signature = tuple(sorted(set(conditions)))

            if signature:
                result.setdefault(
                    signature,
                    award_set,
                )

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

        # create_unique_award_set() can return an existing set.
        # Only create items when this AwardSet currently has none.
        if not award_set.items.exists():
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
                return AwardSet.objects.create(name=name)

            existing_signature = tuple(
                sorted(
                    set(
                        (
                            self.normalize_condition(item.condition),
                            item.trophy_icon_id,
                        )
                        for item in existing.items.all()
                    )
                )
            )

            if existing_signature == signature:
                return existing

            suffix += 1

            suffix_text = f" {suffix}"

            name = f"{base_name[: 64 - len(suffix_text)]}{suffix_text}"

    @staticmethod
    def signature_digest(
        signature,
    ):
        serialized = "|".join(f"{condition}:{icon_id}" for condition, icon_id in signature)

        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:8]

    @staticmethod
    def get_award_set_name(
        award_set,
    ):
        if isinstance(
            award_set,
            str,
        ):
            return f'"{award_set}"'

        return f'"{award_set.name}"'

    @staticmethod
    def render_signature(
        signature,
    ):
        icon_names = {
            icon.id: icon.name
            for icon in TrophyIcon.objects.filter(
                id__in=[
                    icon_id
                    for (
                        _condition,
                        icon_id,
                    ) in signature
                ]
            )
        }

        return ", ".join(
            (
                f"{condition}="
                f"{
                    icon_names.get(
                        icon_id,
                        icon_id,
                    )
                }"
            )
            for (
                condition,
                icon_id,
            ) in signature
        )

    def render_results(
        self,
        *,
        apply_changes,
        counters,
        clear_mappings,
        conflicts,
        unsafe_competitions,
        competitions_without_trophies,
    ):
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

        self.stdout.write(
            "Award sets "
            + ("created: " if apply_changes else "that would be created: ")
            + f"{counters['award_sets_created']}"
        )

        self.stdout.write(
            "Award set items "
            + ("created: " if apply_changes else "that would be created: ")
            + f"{counters['award_set_items_created']}"
        )

        self.stdout.write(f"Existing award sets reused: {counters['existing_award_sets_reused']}")

        self.stdout.write(f"Newly derived award sets reused: {counters['derived_award_sets_reused']}")

        self.stdout.write(f"Competitions without trophies: {counters['without_trophies']}")

        self.stdout.write(f"Unsafe competitions skipped: {counters['unsafe_competitions']}")

        self.stdout.write(f"Competitions with conflicting mappings: {counters['conflicting_competitions']}")

        if conflicts:
            self.stdout.write("")

            self.stdout.write(self.style.ERROR("Conflicting condition-to-icon mappings (would not apply):"))

            for (
                competition,
                conditions,
                condition_trophies,
            ) in conflicts:
                self.stdout.write(f'  Competition {competition.id}: "{competition.name}"')

                for (
                    condition,
                    icon_ids,
                ) in sorted(conditions.items()):
                    self.stdout.write(f"    {condition}:")

                    for icon_id in sorted(icon_ids):
                        trophies_for_icon = condition_trophies[condition][icon_id]

                        icon_name = (
                            trophies_for_icon[0].icon.name if trophies_for_icon[0].icon else f"icon_id={icon_id}"
                        )

                        trophy_ids = ", ".join(str(trophy.id) for trophy in trophies_for_icon)

                        self.stdout.write(f"      {icon_name}: trophy IDs {trophy_ids}")

        if unsafe_competitions:
            self.stdout.write("")

            self.stdout.write(self.style.WARNING("Unsafe competitions skipped (would not apply):"))

            for (
                competition,
                problems,
            ) in unsafe_competitions:
                self.stdout.write(f'  Competition {competition.id}: "{competition.name}"')

                for problem in problems:
                    self.stdout.write(f"    - {problem}")

        if competitions_without_trophies:
            self.stdout.write("")

            self.stdout.write(self.style.WARNING("Competitions without trophies:"))

            for competition in competitions_without_trophies:
                self.stdout.write(f'  {competition.id}: "{competition.name}"')

        if not apply_changes:
            self.stdout.write("")

            self.stdout.write(
                self.style.WARNING("No records were changed. Run again with --apply to save the displayed updates.")
            )
