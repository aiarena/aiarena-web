from collections import defaultdict
from dataclasses import dataclass, field

from aiarena.core.models import Competition, Trophy
from aiarena.core.services import ladders
from dataclasses import dataclass, field

from django.db import transaction

from aiarena.core.models import Competition, Trophy

EXACT_PLACE_CONDITIONS = {
    1: "first_place",
    2: "second_place",
    3: "third_place",
}

TOP_CONDITION_LIMITS = {
    "top_5": 5,
    "top_10": 10,
    "top_15": 15,
    "top_20": 20,
}

SUPPORTED_AUTOMATIC_CONDITIONS = {
    "first_place",
    "second_place",
    "third_place",
    "top_5",
    "top_10",
    "top_15",
    "top_20",
    "participant",
}


@dataclass(frozen=True)
class ExpectedTrophy:
    bot_id: int
    bot_name: str
    rank: int
    condition: str
    icon_id: int
    icon_name: str


@dataclass(frozen=True)
class IncorrectTrophy:
    id: int
    name: str

    bot_id: int
    bot_name: str

    condition: str
    condition_display: str

    icon_id: int | None
    icon_name: str | None
    icon_image: str | None

    competition_id: int
    competition_name: str

    participated: bool
    placement: int | None


@dataclass
class CompetitionTrophyCheckReport:
    status: str
    message: str

    expected_trophies: list[ExpectedTrophy] = field(default_factory=list)
    missing_trophies: list[ExpectedTrophy] = field(default_factory=list)
    incorrect_trophies: list[IncorrectTrophy] = field(default_factory=list)

    issues: list[str] = field(default_factory=list)
    existing_trophy_count: int = 0

    @property
    def expected_trophy_count(self):
        return len(self.expected_trophies)

    @property
    def missing_trophy_count(self):
        return len(self.missing_trophies)

    @property
    def incorrect_trophy_count(self):
        return len(self.incorrect_trophies)

    @property
    def incorrect_trophy_ids(self):
        return [trophy.id for trophy in self.incorrect_trophies]


def get_condition_for_rank(
    rank: int,
    configured_conditions: set[str],
) -> str | None:
    """
    Return one trophy condition for a ranked bot.

    Exact podium conditions take priority. After that, the smallest
    configured Top-N condition containing the rank is selected.
    """
    exact_condition = EXACT_PLACE_CONDITIONS.get(rank)

    if exact_condition in configured_conditions:
        return exact_condition

    matching_top_conditions = [
        (limit, condition)
        for condition, limit in TOP_CONDITION_LIMITS.items()
        if (condition in configured_conditions and rank <= limit)
    ]

    if matching_top_conditions:
        _limit, condition = min(matching_top_conditions)
        return condition

    if "participant" in configured_conditions:
        return "participant"

    return None


def get_ranked_participations(
    competition: Competition,
):
    """
    Use the same full ranking calculation as the public
    competition view.
    """
    rankings = ladders.get_competition_display_full_rankings(competition).calculate_trend(competition)

    return list(rankings)


def build_rank_map(
    ranked_participations,
) -> dict[int, int]:
    """
    Map bot IDs to their one-based competition placement.
    """
    return {
        participation.bot_id: rank
        for rank, participation in enumerate(
            ranked_participations,
            start=1,
        )
    }


def build_expected_trophies(
    competition: Competition,
    ranked_participations=None,
) -> tuple[list[ExpectedTrophy], list[str]]:
    issues = []

    if competition.award_set_id is None:
        return [], ["The competition does not have an award set."]

    award_items = list(competition.award_set.items.select_related("trophy_icon").order_by("condition"))

    if not award_items:
        return [], ["The competition award set does not contain any items."]

    configured_conditions = {item.condition for item in award_items}

    unsupported_conditions = configured_conditions - SUPPORTED_AUTOMATIC_CONDITIONS

    if unsupported_conditions:
        issues.append(
            "The award set contains conditions that cannot be "
            "checked automatically: " + ", ".join(sorted(unsupported_conditions))
        )

    if issues:
        return [], issues

    items_by_condition = {item.condition: item for item in award_items}

    if ranked_participations is None:
        ranked_participations = get_ranked_participations(competition)

    if not ranked_participations:
        return [], ["The competition has no ranked participants."]

    expected_trophies = []

    for rank, participation in enumerate(
        ranked_participations,
        start=1,
    ):
        condition = get_condition_for_rank(
            rank,
            configured_conditions,
        )

        if condition is None:
            continue

        award_item = items_by_condition.get(condition)

        if award_item is None:
            issues.append(f"No award item exists for condition '{condition}'.")
            continue

        expected_trophies.append(
            ExpectedTrophy(
                bot_id=participation.bot_id,
                bot_name=participation.bot.name,
                rank=rank,
                condition=condition,
                icon_id=award_item.trophy_icon_id,
                icon_name=award_item.trophy_icon.name,
            )
        )

    if issues:
        return [], issues

    if not expected_trophies:
        return [], ["The award set does not produce any trophies for the current competition rankings."]

    return expected_trophies, []


def serialize_incorrect_trophy(
    trophy: Trophy,
    rank_by_bot_id: dict[int, int],
) -> IncorrectTrophy:
    placement = rank_by_bot_id.get(trophy.bot_id)

    icon_image = None

    if trophy.icon and trophy.icon.image:
        try:
            icon_image = trophy.icon.image.url
        except ValueError:
            icon_image = None

    return IncorrectTrophy(
        id=trophy.id,
        name=trophy.name,
        bot_id=trophy.bot_id,
        bot_name=trophy.bot.name,
        condition=trophy.condition or "",
        condition_display=(trophy.get_condition_display() if trophy.condition else ""),
        icon_id=trophy.icon_id,
        icon_name=(trophy.icon.name if trophy.icon else None),
        icon_image=icon_image,
        competition_id=trophy.competition_id,
        competition_name=trophy.competition.name,
        participated=placement is not None,
        placement=placement,
    )


def check_competition_trophies(
    competition: Competition,
) -> CompetitionTrophyCheckReport:
    ranked_participations = get_ranked_participations(competition)

    rank_by_bot_id = build_rank_map(ranked_participations)

    expected_trophies, configuration_issues = build_expected_trophies(
        competition,
        ranked_participations=ranked_participations,
    )

    if configuration_issues:
        return CompetitionTrophyCheckReport(
            status="INCOMPLETE_OR_INCORRECT",
            message=("Trophies are incomplete or incorrect."),
            issues=configuration_issues,
        )

    existing_trophies = list(
        Trophy.objects.filter(
            competition=competition,
        )
        .select_related(
            "bot",
            "icon",
            "competition",
        )
        .order_by("id")
    )

    expected_by_key = {
        (
            expected.bot_id,
            expected.condition,
        ): expected
        for expected in expected_trophies
    }

    existing_by_key = defaultdict(list)

    for trophy in existing_trophies:
        existing_by_key[
            (
                trophy.bot_id,
                trophy.condition,
            )
        ].append(trophy)

    missing_trophies = []
    incorrect_trophy_records = []
    issues = []

    for key, expected in expected_by_key.items():
        matching_trophies = existing_by_key.get(
            key,
            [],
        )

        if not matching_trophies:
            missing_trophies.append(expected)
            continue

        if len(matching_trophies) > 1:
            duplicate_ids = [trophy.id for trophy in matching_trophies]

            incorrect_trophy_records.extend(matching_trophies)

            issues.append(f"{expected.bot_name} has duplicate '{expected.condition}' trophies: {duplicate_ids}.")
            continue

        trophy = matching_trophies[0]

        if trophy.icon_id != expected.icon_id:
            incorrect_trophy_records.append(trophy)

            actual_icon = trophy.icon.name if trophy.icon else "no icon"

            issues.append(
                f"Trophy {trophy.id} for "
                f"{expected.bot_name} has icon "
                f"'{actual_icon}', but "
                f"'{expected.icon_name}' is expected."
            )

    for key, trophies in existing_by_key.items():
        if key in expected_by_key:
            continue

        for trophy in trophies:
            incorrect_trophy_records.append(trophy)

            placement = rank_by_bot_id.get(trophy.bot_id)

            if placement is None:
                participation_description = "did not participate in this competition"
            else:
                participation_description = f"placed {placement}"

            issues.append(
                f"Trophy {trophy.id} for "
                f"{trophy.bot.name} with condition "
                f"'{trophy.condition or 'unset'}' is not "
                f"expected for this competition; the bot "
                f"{participation_description}."
            )

    incorrect_trophy_records = list({trophy.id: trophy for trophy in incorrect_trophy_records}.values())

    incorrect_trophy_records.sort(key=lambda trophy: trophy.id)

    incorrect_trophies = [
        serialize_incorrect_trophy(
            trophy,
            rank_by_bot_id,
        )
        for trophy in incorrect_trophy_records
    ]

    if incorrect_trophies:
        return CompetitionTrophyCheckReport(
            status="INCOMPLETE_OR_INCORRECT",
            message=("Trophies are incomplete or incorrect."),
            expected_trophies=expected_trophies,
            missing_trophies=missing_trophies,
            incorrect_trophies=incorrect_trophies,
            issues=issues,
            existing_trophy_count=len(existing_trophies),
        )

    if missing_trophies:
        return CompetitionTrophyCheckReport(
            status="NOT_AWARDED",
            message="Trophies have not been awarded.",
            expected_trophies=expected_trophies,
            missing_trophies=missing_trophies,
            existing_trophy_count=len(existing_trophies),
        )

    return CompetitionTrophyCheckReport(
        status="AWARDED",
        message="Trophies have been awarded.",
        expected_trophies=expected_trophies,
        existing_trophy_count=len(existing_trophies),
    )


@dataclass
class CompetitionTrophyAwardReport:
    success: bool
    message: str

    deleted_trophy_ids: list[int] = field(default_factory=list)
    created_trophy_ids: list[int] = field(default_factory=list)

    @property
    def deleted_trophy_count(self):
        return len(self.deleted_trophy_ids)

    @property
    def created_trophy_count(self):
        return len(self.created_trophy_ids)


def get_trophy_name(
    competition: Competition,
    condition: str,
) -> str:
    condition_labels = dict(Trophy._meta.get_field("condition").choices)

    condition_label = condition_labels.get(
        condition,
        condition,
    )

    return f"{condition_label} - {competition.name}"


@transaction.atomic
def award_competition_trophies(
    competition: Competition,
) -> CompetitionTrophyAwardReport:
    """
    Reconcile trophies for one competition.

    - Locks the competition and its existing trophies.
    - Deletes trophies identified as incorrect.
    - Creates trophies identified as missing.
    - Leaves correct trophies unchanged.
    - Marks awards_given=True after reconciliation.
    """
    locked_competition = Competition.objects.select_for_update().get(pk=competition.pk)

    if locked_competition.award_set_id is None:
        return CompetitionTrophyAwardReport(
            success=False,
            message=("The competition does not have an award set."),
        )

    # Lock existing trophy rows before checking them. This prevents
    # concurrent award requests from modifying the same trophies.
    list(Trophy.objects.select_for_update().filter(competition=locked_competition).values_list("id", flat=True))

    report = check_competition_trophies(locked_competition)

    # Configuration errors must not be fixed automatically. These
    # include invalid award sets or unsupported conditions.
    if report.status == "INCOMPLETE_OR_INCORRECT" and not report.incorrect_trophies:
        return CompetitionTrophyAwardReport(
            success=False,
            message=report.message,
        )

    incorrect_trophy_ids = [trophy.id for trophy in report.incorrect_trophies]

    if incorrect_trophy_ids:
        Trophy.objects.filter(
            competition=locked_competition,
            id__in=incorrect_trophy_ids,
        ).delete()

    created_trophies = []

    for expected in report.missing_trophies:
        trophy = Trophy.objects.create(
            bot_id=expected.bot_id,
            competition=locked_competition,
            condition=expected.condition,
            icon_id=expected.icon_id,
            name=get_trophy_name(
                locked_competition,
                expected.condition,
            ),
        )

        created_trophies.append(trophy)

    # Run the check again after reconciliation. This prevents the
    # competition being marked complete if deletion or creation logic
    # did not produce the expected final state.
    final_report = check_competition_trophies(locked_competition)

    if final_report.status != "AWARDED":
        raise RuntimeError("Trophy reconciliation did not produce a valid awarded state.")

    if not locked_competition.awards_given:
        locked_competition.awards_given = True
        locked_competition.save(update_fields=["awards_given"])

    return CompetitionTrophyAwardReport(
        success=True,
        message=("Trophies have been awarded successfully."),
        deleted_trophy_ids=incorrect_trophy_ids,
        created_trophy_ids=[trophy.id for trophy in created_trophies],
    )
