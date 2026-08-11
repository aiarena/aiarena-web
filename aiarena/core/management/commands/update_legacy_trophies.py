import re
from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from aiarena.core.models import Competition, Trophy


# Usage:
#
# Test without applying changes:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py update_legacy_trophies
#
# Apply the displayed changes:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py update_legacy_trophies --apply
#
# Test one trophy:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py update_legacy_trophies --trophy-id 34
#
# Test multiple trophies:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py update_legacy_trophies \
#     --trophy-id 34 \
#     --trophy-id 35
#
# Overwrite already-populated values:
# DJANGO_ENVIRONMENT=DEVELOPMENT uv run manage.py update_legacy_trophies \
#     --apply \
#     --overwrite


class Command(BaseCommand):
    help = "Parse legacy trophy names, assign trophy conditions, and link trophies to confidently matched competitions."

    # Historical trophy names that differ from Competition.name.
    #
    # Do not add tournaments, challenges, or external events here unless they
    # actually correspond to a Competition row.
    COMPETITION_ALIASES = {
        "ai arena melee season 1": "AI Arena - Season 1",
        "arena melee ladder season 1": "AI Arena - Season 1",
        "ai arena melee season 2": "AI Arena - Season 2",
        "arena melee ladder season 2": "AI Arena - Season 2",
        "ai arena season 1": "AI Arena - Season 1",
        "ai arena season 2": "AI Arena - Season 2",
        # Legacy trophy name -> current competition name.
        "sc2 ai arena micro ladder season 1": ("Sc2 AI Arena Micro Ladder"),
        "sc2 ai arena season 1": "Sc2 AI Arena Season 1",
    }

    # Legacy trophy names -> canonical Trophy.condition.
    #
    # Historical trophy text may say either "Best" or "Top", but race-specific
    # conditions are stored using the canonical best_* values.
    #
    # Examples:
    #
    #     Best Zerg    -> best_zerg
    #     Top Zerg     -> best_zerg
    #
    #     Best Protoss -> best_protoss
    #     Top Protoss  -> best_protoss
    #
    #     Best Terran  -> best_terran
    #     Top Terran   -> best_terran
    #
    #     Best Random  -> best_random
    #     Top Random   -> best_random
    CONDITION_PATTERNS = (
        (
            re.compile(
                r"\b1st\s+place\b",
                re.IGNORECASE,
            ),
            ("first_place",),
        ),
        (
            re.compile(
                r"\b2nd\s+place\b",
                re.IGNORECASE,
            ),
            ("second_place",),
        ),
        (
            re.compile(
                r"\b3rd\s+place\b",
                re.IGNORECASE,
            ),
            ("third_place",),
        ),
        (
            re.compile(
                r"\btop\s*20\b",
                re.IGNORECASE,
            ),
            ("top_20",),
        ),
        (
            re.compile(
                r"\btop\s*15\b",
                re.IGNORECASE,
            ),
            ("top_15",),
        ),
        (
            re.compile(
                r"\btop\s*10\b",
                re.IGNORECASE,
            ),
            ("top_10",),
        ),
        (
            re.compile(
                r"\btop\s*5\b",
                re.IGNORECASE,
            ),
            ("top_5",),
        ),
        # Race-specific awards.
        (
            re.compile(
                r"\b(?:best|top)\s+zerg\b",
                re.IGNORECASE,
            ),
            ("best_zerg",),
        ),
        (
            re.compile(
                r"\b(?:best|top)\s+protoss\b",
                re.IGNORECASE,
            ),
            ("best_protoss",),
        ),
        (
            re.compile(
                r"\b(?:best|top)\s+terran\b",
                re.IGNORECASE,
            ),
            ("best_terran",),
        ),
        (
            re.compile(
                r"\b(?:best|top)\s+random\b",
                re.IGNORECASE,
            ),
            ("best_random",),
        ),
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help=("Save changes. Without this option, the command performs a dry run."),
        )

        parser.add_argument(
            "--overwrite",
            action="store_true",
            help=("Replace existing condition and competition values."),
        )

        parser.add_argument(
            "--trophy-id",
            type=int,
            action="append",
            dest="trophy_ids",
            help=("Only process a specific trophy ID. May be supplied multiple times."),
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        overwrite = options["overwrite"]
        trophy_ids = options["trophy_ids"]

        queryset = Trophy.objects.select_related(
            "competition",
            "icon",
            "bot",
        ).order_by("id")

        if trophy_ids:
            queryset = queryset.filter(id__in=trophy_ids)

            found_ids = set(
                queryset.values_list(
                    "id",
                    flat=True,
                )
            )

            missing_ids = set(trophy_ids) - found_ids

            if missing_ids:
                raise CommandError(f"Trophy IDs do not exist: {sorted(missing_ids)}")

        competitions = list(Competition.objects.all())

        competitions_by_normalized_name = {
            self.normalize_name(competition.name): competition for competition in competitions
        }

        allowed_conditions = {value for value, _label in Trophy._meta.get_field("condition").choices}

        counters = Counter()

        condition_unmatched = []
        competition_unmatched = []

        with transaction.atomic():
            for trophy in queryset.iterator():
                changes = {}

                parsed_condition = self.parse_condition(
                    trophy.name,
                    allowed_conditions,
                )

                if parsed_condition:
                    counters["condition_matched"] += 1
                else:
                    counters["condition_unmatched"] += 1

                    condition_unmatched.append(trophy)

                if parsed_condition and (overwrite or not trophy.condition):
                    if trophy.condition != parsed_condition:
                        changes["condition"] = parsed_condition

                parsed_source_name = self.parse_source_name(trophy.name)

                competition = self.find_competition(
                    parsed_source_name,
                    competitions_by_normalized_name,
                )

                if competition:
                    counters["competition_matched"] += 1
                else:
                    counters["competition_unmatched"] += 1

                    competition_unmatched.append(trophy)

                if competition and (overwrite or trophy.competition_id is None):
                    if trophy.competition_id != competition.id:
                        changes["competition"] = competition

                if not changes:
                    counters["unchanged"] += 1
                    continue

                rendered_changes = ", ".join(
                    (f"{field}={getattr(value, 'name', value)!r}") for field, value in changes.items()
                )

                self.stdout.write(f'Trophy {trophy.id}: "{trophy.name}" -> {rendered_changes}')

                for field, value in changes.items():
                    setattr(
                        trophy,
                        field,
                        value,
                    )

                if apply_changes:
                    trophy.save(update_fields=list(changes))

                counters["would_update"] += 1

            if not apply_changes:
                transaction.set_rollback(True)

        mode = "APPLIED" if apply_changes else "DRY RUN"

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{mode} complete"))

        if apply_changes:
            self.stdout.write(f"Updated: {counters['would_update']}")
        else:
            self.stdout.write(f"Would update: {counters['would_update']}")

        self.stdout.write(f"Unchanged: {counters['unchanged']}")

        self.stdout.write(f"Condition matched: {counters['condition_matched']}")

        self.stdout.write(f"Condition unmatched: {counters['condition_unmatched']}")

        self.stdout.write(f"Competition matched: {counters['competition_matched']}")

        self.stdout.write(f"Competition unmatched: {counters['competition_unmatched']}")

        if condition_unmatched:
            self.stdout.write("")

            self.stdout.write(self.style.WARNING("Trophies with unmatched conditions:"))

            for trophy in condition_unmatched:
                self.stdout.write(f'  {trophy.id}: "{trophy.name}"')

        if competition_unmatched:
            self.stdout.write("")

            self.stdout.write(self.style.WARNING("Trophies with unmatched competitions:"))

            for trophy in competition_unmatched:
                self.stdout.write(f'  {trophy.id}: "{trophy.name}"')

        if not apply_changes:
            self.stdout.write("")

            self.stdout.write(
                self.style.WARNING("No records were changed. Run again with --apply to save the displayed updates.")
            )

    @classmethod
    def parse_condition(
        cls,
        trophy_name,
        allowed_conditions,
    ):
        """
        Parse a historical trophy name into a canonical
        Trophy.condition value.

        Historical aliases such as "Top Zerg" and "Best Zerg"
        are normalized to the current best_* condition names.

        Only conditions currently defined by the Trophy model
        are returned.
        """
        for (
            pattern,
            candidate_values,
        ) in cls.CONDITION_PATTERNS:
            if not pattern.search(trophy_name):
                continue

            for candidate in candidate_values:
                if candidate in allowed_conditions:
                    return candidate

        return None

    @staticmethod
    def parse_source_name(
        trophy_name,
    ):
        """
        Extract the event/competition name from historical
        trophy-name formats.

        Examples:

            1st Place - Sc2 AI Arena Season 2

            Top 10 - Arena Melee Ladder Season 2

            Sc2 AI Arena Season 2 - Top 10

            Best Zerg - Sc2 AI Arena Micro Ladder Season 1
            Top Zerg - Sc2 AI Arena 2022 Season 1

            Best Protoss - Sc2 AI Arena Micro Ladder Season 1

            Best Terran - Competition Name

            Best Random - Sc2 AI Arena Micro Ladder Season 1
        """
        name = trophy_name.strip()

        place_prefix = re.match(
            (
                r"^(?:1st|2nd|3rd)"
                r"\s+place\s*-\s*(.+)$"
            ),
            name,
            flags=re.IGNORECASE,
        )

        if place_prefix:
            return place_prefix.group(1).strip()

        top_prefix = re.match(
            r"^top\s*\d+\s*-\s*(.+)$",
            name,
            flags=re.IGNORECASE,
        )

        if top_prefix:
            return top_prefix.group(1).strip()

        top_suffix = re.match(
            r"^(.+?)\s*-\s*top\s*\d+$",
            name,
            flags=re.IGNORECASE,
        )

        if top_suffix:
            return top_suffix.group(1).strip()

        # Race-specific historical awards.
        #
        # Both "Best" and "Top" historical names identify
        # the same source competition.
        #
        # Supported:
        #
        #     Best Zerg    / Top Zerg
        #     Best Protoss / Top Protoss
        #     Best Terran  / Top Terran
        #     Best Random  / Top Random
        race_award_prefix = re.match(
            (
                r"^(?:best|top)\s+"
                r"(?:zerg|protoss|terran|random)"
                r"\s*-\s*(.+)$"
            ),
            name,
            flags=re.IGNORECASE,
        )

        if race_award_prefix:
            return race_award_prefix.group(1).strip()

        return None

    def find_competition(
        self,
        parsed_source_name,
        competitions_by_normalized_name,
    ):
        if not parsed_source_name:
            return None

        normalized_source = self.normalize_name(parsed_source_name)

        # Prefer an exact normalized match.
        competition = competitions_by_normalized_name.get(normalized_source)

        if competition:
            return competition

        # Fall back to explicitly configured aliases.
        alias_target = self.COMPETITION_ALIASES.get(normalized_source)

        if not alias_target:
            return None

        return competitions_by_normalized_name.get(self.normalize_name(alias_target))

    @staticmethod
    def normalize_name(value):
        value = value.casefold()

        value = re.sub(
            r"[^a-z0-9]+",
            " ",
            value,
        )

        return " ".join(value.split())
