# Trophy-system tests
#
# Covers condition matching and precedence (including Best Zerg/Protoss/Terran/Random),
# expected trophy derivation, GraphQL admin/auth validation, incorrect/missing
# trophy reconciliation, idempotency, closed-competition enforcement, and
# protection against malformed or nefarious GraphQL inputs.

from types import SimpleNamespace

import pytest

from aiarena.core.models import (
    AwardSet,
    AwardSetItem,
    Trophy,
    TrophyIcon,
)
from aiarena.core.models.trophy import TrophyCondition
from aiarena.core.services.service_implementations import _competition_trophies
from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import BotType, CompetitionType
from aiarena.graphql.common import NOT_LOGGED_IN_MESSAGE


ADMIN_REQUIRED_MESSAGE = "Administrator access is required."
COMPETITION_CLOSED_MESSAGE = "Competition must be closed before trophies can be awarded."


def make_admin(user):
    user.is_staff = True
    user.is_superuser = True
    user.save(
        update_fields=[
            "is_staff",
            "is_superuser",
        ]
    )
    return user


def create_standard_award_set():
    first_icon = TrophyIcon.objects.create(
        name="test-medal-1",
        image="trophy_images/test-medal-1.png",
    )
    second_icon = TrophyIcon.objects.create(
        name="test-medal-2",
        image="trophy_images/test-medal-2.png",
    )
    third_icon = TrophyIcon.objects.create(
        name="test-medal-3",
        image="trophy_images/test-medal-3.png",
    )
    top_10_icon = TrophyIcon.objects.create(
        name="test-diploma",
        image="trophy_images/test-diploma.png",
    )

    award_set = AwardSet.objects.create(name="Test Standard Awards")

    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.FIRST_PLACE,
        trophy_icon=first_icon,
    )
    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.SECOND_PLACE,
        trophy_icon=second_icon,
    )
    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.THIRD_PLACE,
        trophy_icon=third_icon,
    )
    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.TOP_10,
        trophy_icon=top_10_icon,
    )

    return SimpleNamespace(
        award_set=award_set,
        first_icon=first_icon,
        second_icon=second_icon,
        third_icon=third_icon,
        top_10_icon=top_10_icon,
    )


def configure_competition(
    competition,
    *,
    status="closed",
):
    awards = create_standard_award_set()

    competition.status = status
    competition.award_set = awards.award_set
    competition.awards_given = False
    competition.save(
        update_fields=[
            "status",
            "award_set",
            "awards_given",
        ]
    )

    return awards


def mock_rankings(
    monkeypatch,
    bots,
):
    """
    Trophy calculation only needs bot_id and bot from each ranked
    participation, so tests do not need to construct an entire
    historical ladder dataset.
    """
    participations = [
        SimpleNamespace(
            bot_id=bot.id,
            bot=bot,
        )
        for bot in bots
    ]

    monkeypatch.setattr(
        _competition_trophies,
        "get_ranked_participations",
        lambda competition: participations,
    )

    return participations


def make_participation(
    bot_id: int,
    name: str,
    race_label: str,
):
    """Create the minimal ranked participation needed by condition tests."""
    bot = SimpleNamespace(
        id=bot_id,
        name=name,
        plays_race=SimpleNamespace(
            label=race_label,
        ),
    )

    return SimpleNamespace(
        bot_id=bot_id,
        bot=bot,
    )


class TestTrophyConditions:
    def make_context(
        self,
        *,
        rank,
        participation,
        rankings,
    ):
        return _competition_trophies.ConditionContext(
            rank=rank,
            participation=participation,
            ranked_participations=rankings,
        )

    @pytest.mark.parametrize(
        "condition,rank,expected",
        [
            (TrophyCondition.FIRST_PLACE, 1, True),
            (TrophyCondition.FIRST_PLACE, 2, False),
            (TrophyCondition.SECOND_PLACE, 2, True),
            (TrophyCondition.SECOND_PLACE, 1, False),
            (TrophyCondition.THIRD_PLACE, 3, True),
            (TrophyCondition.THIRD_PLACE, 4, False),
            (TrophyCondition.TOP_5, 1, True),
            (TrophyCondition.TOP_5, 5, True),
            (TrophyCondition.TOP_5, 6, False),
            (TrophyCondition.TOP_10, 10, True),
            (TrophyCondition.TOP_10, 11, False),
            (TrophyCondition.TOP_15, 15, True),
            (TrophyCondition.TOP_15, 16, False),
            (TrophyCondition.TOP_20, 20, True),
            (TrophyCondition.TOP_20, 21, False),
            (TrophyCondition.PARTICIPANT, 1, True),
            (TrophyCondition.PARTICIPANT, 100, True),
        ],
    )
    def test_rank_conditions(
        self,
        condition,
        rank,
        expected,
    ):
        participation = make_participation(
            bot_id=1,
            name="TestBot",
            race_label="Z",
        )

        context = self.make_context(
            rank=rank,
            participation=participation,
            rankings=[participation],
        )

        assert (
            _competition_trophies.condition_matches(
                condition,
                context,
            )
            is expected
        )

    def test_custom_condition_is_not_automatic(self):
        participation = make_participation(
            bot_id=1,
            name="TestBot",
            race_label="Z",
        )

        context = self.make_context(
            rank=1,
            participation=participation,
            rankings=[participation],
        )

        assert (
            _competition_trophies.condition_matches(
                TrophyCondition.CUSTOM,
                context,
            )
            is False
        )

    def test_all_non_custom_conditions_have_automatic_checks(self):
        expected_automatic_conditions = {
            condition.value for condition in TrophyCondition if condition != TrophyCondition.CUSTOM
        }

        assert set(_competition_trophies.AUTOMATIC_CONDITION_CHECKS) == expected_automatic_conditions

    def test_condition_groups_cover_all_automatic_conditions(self):
        grouped_conditions = set(_competition_trophies.PLACEMENT_CONDITIONS) | set(
            _competition_trophies.SPECIAL_CONDITIONS
        )

        assert grouped_conditions == set(_competition_trophies.AUTOMATIC_CONDITION_CHECKS)

    def test_condition_groups_are_unique_and_do_not_overlap(self):
        placement = _competition_trophies.PLACEMENT_CONDITIONS
        special = _competition_trophies.SPECIAL_CONDITIONS

        assert len(placement) == len(set(placement))
        assert len(special) == len(set(special))
        assert not (set(placement) & set(special))

    def test_first_place_has_priority_over_top_conditions(self):
        winner = make_participation(1, "Winner", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=1,
            participation=winner,
            ranked_participations=[winner],
            configured_conditions={
                TrophyCondition.FIRST_PLACE,
                TrophyCondition.TOP_5,
                TrophyCondition.TOP_10,
                TrophyCondition.PARTICIPANT,
            },
        )

        assert conditions == [TrophyCondition.FIRST_PLACE]

    def test_second_place_has_priority_over_top_conditions(self):
        first = make_participation(1, "Winner", "Z")
        second = make_participation(2, "RunnerUp", "P")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=2,
            participation=second,
            ranked_participations=[first, second],
            configured_conditions={
                TrophyCondition.SECOND_PLACE,
                TrophyCondition.TOP_5,
                TrophyCondition.TOP_10,
            },
        )

        assert conditions == [TrophyCondition.SECOND_PLACE]

    def test_smallest_top_condition_wins(self):
        participation = make_participation(4, "Fourth", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=4,
            participation=participation,
            ranked_participations=[participation],
            configured_conditions={
                TrophyCondition.TOP_5,
                TrophyCondition.TOP_10,
                TrophyCondition.TOP_20,
            },
        )

        assert conditions == [TrophyCondition.TOP_5]

    def test_falls_through_to_next_top_condition(self):
        participation = make_participation(8, "Eighth", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=8,
            participation=participation,
            ranked_participations=[participation],
            configured_conditions={
                TrophyCondition.TOP_5,
                TrophyCondition.TOP_10,
                TrophyCondition.TOP_20,
            },
        )

        assert conditions == [TrophyCondition.TOP_10]

    def test_participant_is_fallback_condition(self):
        participation = make_participation(20, "Participant", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=20,
            participation=participation,
            ranked_participations=[participation],
            configured_conditions={
                TrophyCondition.TOP_5,
                TrophyCondition.PARTICIPANT,
            },
        )

        assert conditions == [TrophyCondition.PARTICIPANT]

    @pytest.mark.parametrize(
        "condition,race_label",
        [
            (TrophyCondition.BEST_ZERG, "Z"),
            (TrophyCondition.BEST_PROTOSS, "P"),
            (TrophyCondition.BEST_TERRAN, "T"),
            (TrophyCondition.BEST_RANDOM, "R"),
        ],
    )
    def test_highest_ranked_bot_of_race_matches(
        self,
        condition,
        race_label,
    ):
        other_race = "P" if race_label != "P" else "Z"
        overall_winner = make_participation(1, "OverallWinner", other_race)
        top_race = make_participation(2, "TopRace", race_label)
        second_race = make_participation(3, "SecondRace", race_label)
        rankings = [overall_winner, top_race, second_race]

        context = self.make_context(
            rank=2,
            participation=top_race,
            rankings=rankings,
        )

        assert _competition_trophies.condition_matches(condition, context) is True

    @pytest.mark.parametrize(
        "condition,race_label",
        [
            (TrophyCondition.BEST_ZERG, "Z"),
            (TrophyCondition.BEST_PROTOSS, "P"),
            (TrophyCondition.BEST_TERRAN, "T"),
            (TrophyCondition.BEST_RANDOM, "R"),
        ],
    )
    def test_lower_ranked_bot_of_same_race_does_not_match(
        self,
        condition,
        race_label,
    ):
        top_race = make_participation(1, "TopRace", race_label)
        second_race = make_participation(2, "SecondRace", race_label)
        rankings = [top_race, second_race]

        context = self.make_context(
            rank=2,
            participation=second_race,
            rankings=rankings,
        )

        assert _competition_trophies.condition_matches(condition, context) is False

    def test_best_random_is_highest_ranked_random(self):
        overall_winner = make_participation(1, "OverallWinner", "Z")
        best_random = make_participation(2, "BestRandom", "R")
        second_random = make_participation(3, "SecondRandom", "R")
        rankings = [overall_winner, best_random, second_random]

        context = self.make_context(
            rank=2,
            participation=best_random,
            rankings=rankings,
        )

        assert _competition_trophies.is_best_random(context) is True

    def test_wrong_race_does_not_match_special_condition(self):
        protoss = make_participation(1, "Protoss", "P")
        context = self.make_context(
            rank=1,
            participation=protoss,
            rankings=[protoss],
        )

        assert _competition_trophies.is_best_zerg(context) is False
        assert _competition_trophies.is_best_terran(context) is False
        assert _competition_trophies.is_best_random(context) is False

    def test_bot_can_receive_placement_and_best_race_trophy(self):
        winner = make_participation(1, "Winner", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=1,
            participation=winner,
            ranked_participations=[winner],
            configured_conditions={
                TrophyCondition.FIRST_PLACE,
                TrophyCondition.TOP_5,
                TrophyCondition.BEST_ZERG,
            },
        )

        assert conditions == [
            TrophyCondition.FIRST_PLACE,
            TrophyCondition.BEST_ZERG,
        ]

    def test_bot_does_not_receive_multiple_placement_trophies(self):
        winner = make_participation(1, "Winner", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=1,
            participation=winner,
            ranked_participations=[winner],
            configured_conditions={
                TrophyCondition.FIRST_PLACE,
                TrophyCondition.TOP_5,
                TrophyCondition.TOP_10,
                TrophyCondition.TOP_20,
                TrophyCondition.PARTICIPANT,
            },
        )

        assert conditions == [TrophyCondition.FIRST_PLACE]

    def test_only_matching_best_race_trophy_is_returned(self):
        winner = make_participation(1, "Winner", "Z")

        conditions = _competition_trophies.get_conditions_for_participation(
            rank=1,
            participation=winner,
            ranked_participations=[winner],
            configured_conditions={
                TrophyCondition.BEST_ZERG,
                TrophyCondition.BEST_PROTOSS,
                TrophyCondition.BEST_TERRAN,
                TrophyCondition.BEST_RANDOM,
            },
        )

        assert conditions == [TrophyCondition.BEST_ZERG]


def test_build_expected_trophies_includes_placement_and_race_awards(
    competition,
):
    first_icon = TrophyIcon.objects.create(
        name="integration-first",
        image="trophy_images/integration-first.png",
    )
    zerg_icon = TrophyIcon.objects.create(
        name="integration-zerg",
        image="trophy_images/integration-zerg.png",
    )
    protoss_icon = TrophyIcon.objects.create(
        name="integration-protoss",
        image="trophy_images/integration-protoss.png",
    )

    award_set = AwardSet.objects.create(
        name="Race Award Integration Set",
    )

    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.FIRST_PLACE,
        trophy_icon=first_icon,
    )
    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.BEST_ZERG,
        trophy_icon=zerg_icon,
    )
    AwardSetItem.objects.create(
        award_set=award_set,
        condition=TrophyCondition.BEST_PROTOSS,
        trophy_icon=protoss_icon,
    )

    competition.award_set = award_set
    competition.save(update_fields=["award_set"])

    first_zerg = make_participation(1001, "BestZerg", "Z")
    first_protoss = make_participation(1002, "BestProtoss", "P")
    second_zerg = make_participation(1003, "SecondZerg", "Z")

    expected, issues = _competition_trophies.build_expected_trophies(
        competition,
        ranked_participations=[
            first_zerg,
            first_protoss,
            second_zerg,
        ],
    )

    assert issues == []
    assert [(trophy.bot_name, trophy.condition) for trophy in expected] == [
        ("BestZerg", TrophyCondition.FIRST_PLACE),
        ("BestZerg", TrophyCondition.BEST_ZERG),
        ("BestProtoss", TrophyCondition.BEST_PROTOSS),
    ]


class TestCheckCompetitionTrophies(GraphQLTest):
    mutation_name = "checkCompetitionTrophies"

    # language=graphql
    mutation = """
        mutation ($input: CheckCompetitionTrophiesInput!) {
            checkCompetitionTrophies(input: $input) {
                status
                message

                expectedTrophyCount
                existingTrophyCount
                missingTrophyCount
                incorrectTrophyCount

                incorrectTrophyIds
                issues

                missingTrophies {
                    botId
                    botName
                    rank
                    condition
                    iconId
                    iconName
                }

                incorrectTrophies {
                    id
                    name

                    botId
                    botName

                    condition
                    conditionDisplay

                    iconId
                    iconName
                    iconImage

                    competitionId
                    competitionName

                    participated
                    placement
                }

                errors {
                    field
                    messages
                }
            }
        }
    """

    def test_admin_can_check_missing_trophies(
        self,
        user,
        competition,
        bot,
        other_bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        configure_competition(
            competition,
            status="closed",
        )

        mock_rankings(
            monkeypatch,
            [
                bot,
                other_bot,
            ],
        )

        response = self.mutate(
            login_user=admin,
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        result = response["checkCompetitionTrophies"]

        assert result["status"] == "NOT_AWARDED"
        assert result["expectedTrophyCount"] == 2
        assert result["existingTrophyCount"] == 0
        assert result["missingTrophyCount"] == 2
        assert result["incorrectTrophyCount"] == 0

        assert result["missingTrophies"][0]["botId"] == str(bot.id)
        assert result["missingTrophies"][0]["condition"] == TrophyCondition.FIRST_PLACE

        assert result["missingTrophies"][1]["botId"] == str(other_bot.id)
        assert result["missingTrophies"][1]["condition"] == TrophyCondition.SECOND_PLACE

    def test_check_reports_incorrect_trophy_details(
        self,
        user,
        competition,
        bot,
        other_bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        awards = configure_competition(
            competition,
            status="closed",
        )

        # Only bot participates.
        mock_rankings(
            monkeypatch,
            [bot],
        )

        wrong_trophy = Trophy.objects.create(
            bot=other_bot,
            competition=competition,
            condition=TrophyCondition.TOP_10,
            icon=awards.top_10_icon,
            name=f"Top 10 - {competition.name}",
        )

        response = self.mutate(
            login_user=admin,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        result = response["checkCompetitionTrophies"]

        assert result["status"] == "INCOMPLETE_OR_INCORRECT"
        assert result["incorrectTrophyCount"] == 1
        assert result["incorrectTrophyIds"] == [str(wrong_trophy.id)]

        incorrect = result["incorrectTrophies"][0]

        assert incorrect["id"] == str(wrong_trophy.id)
        assert incorrect["botId"] == str(other_bot.id)
        assert incorrect["botName"] == other_bot.name

        assert incorrect["condition"] == TrophyCondition.TOP_10
        assert incorrect["conditionDisplay"] == "Top 10"

        assert incorrect["iconName"] == "test-diploma"

        assert incorrect["competitionId"] == str(competition.id)
        assert incorrect["competitionName"] == competition.name

        assert incorrect["participated"] is False
        assert incorrect["placement"] is None

    def test_non_admin_cannot_check(
        self,
        user,
        competition,
    ):
        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
            expected_errors_like=[
                ADMIN_REQUIRED_MESSAGE,
            ],
        )

    def test_anonymous_cannot_check(
        self,
        competition,
    ):
        self.mutate(
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
            expected_errors_like=[
                NOT_LOGGED_IN_MESSAGE,
            ],
        )

    def test_invalid_competition_id_is_rejected(
        self,
        user,
    ):
        admin = make_admin(user)

        self.mutate(
            login_user=admin,
            expected_status=400,
            variables={
                "input": {
                    "competition": ("Innocent competition'); DROP TABLE core_trophy; --"),
                }
            },
            expected_errors_like=[
                "Invalid ID format",
            ],
        )

    def test_wrong_relay_object_type_is_rejected(
        self,
        user,
        bot,
    ):
        admin = make_admin(user)

        self.mutate(
            login_user=admin,
            expected_status=400,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        BotType,
                        bot.id,
                    ),
                }
            },
            expected_errors_like=[
                'Wrong ID type "BotType" passed, expected CompetitionType.',
            ],
        )

    def test_unknown_input_field_is_rejected(
        self,
        user,
        competition,
    ):
        admin = make_admin(user)

        self.mutate(
            login_user=admin,
            expected_status=400,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                    "deleteEverything": True,
                }
            },
            expected_errors_like=[
                "Field 'deleteEverything' is not defined",
            ],
        )

    def test_check_marks_awards_given_when_all_trophies_are_correct(
        self,
        user,
        competition,
        bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        awards = configure_competition(
            competition,
            status="closed",
        )

        mock_rankings(
            monkeypatch,
            [bot],
        )

        Trophy.objects.create(
            bot=bot,
            competition=competition,
            condition=TrophyCondition.FIRST_PLACE,
            icon=awards.first_icon,
            name=f"1st Place - {competition.name}",
        )

        assert competition.awards_given is False

        response = self.mutate(
            login_user=admin,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        result = response["checkCompetitionTrophies"]

        assert result["status"] == "AWARDED"

        competition.refresh_from_db()
        assert competition.awards_given is True


class TestAwardCompetitionTrophies(GraphQLTest):
    mutation_name = "awardCompetitionTrophies"

    # language=graphql
    mutation = """
        mutation ($input: AwardCompetitionTrophiesInput!) {
            awardCompetitionTrophies(input: $input) {
                success
                message

                createdTrophyCount
                deletedTrophyCount

                createdTrophyIds
                deletedTrophyIds

                errors {
                    field
                    messages
                }
            }
        }
    """

    def test_admin_awards_missing_trophies(
        self,
        user,
        competition,
        bot,
        other_bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        awards = configure_competition(
            competition,
            status="closed",
        )

        mock_rankings(
            monkeypatch,
            [
                bot,
                other_bot,
            ],
        )

        assert not Trophy.objects.filter(competition=competition).exists()

        response = self.mutate(
            login_user=admin,
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        result = response["awardCompetitionTrophies"]

        assert result["success"] is True
        assert result["createdTrophyCount"] == 2
        assert result["deletedTrophyCount"] == 0

        trophies = Trophy.objects.filter(competition=competition).order_by("condition")

        assert trophies.count() == 2

        first = Trophy.objects.get(
            competition=competition,
            bot=bot,
        )
        assert first.condition == TrophyCondition.FIRST_PLACE
        assert first.icon == awards.first_icon
        assert first.name == (f"1st Place - {competition.name}")

        second = Trophy.objects.get(
            competition=competition,
            bot=other_bot,
        )
        assert second.condition == TrophyCondition.SECOND_PLACE
        assert second.icon == awards.second_icon

        competition.refresh_from_db()
        assert competition.awards_given is True

    def test_award_removes_incorrect_and_creates_correct(
        self,
        user,
        competition,
        bot,
        other_bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        awards = configure_competition(
            competition,
            status="closed",
        )

        mock_rankings(
            monkeypatch,
            [
                bot,
                other_bot,
            ],
        )

        # Bot is rank 1 but has the wrong trophy.
        incorrect = Trophy.objects.create(
            bot=bot,
            competition=competition,
            condition=TrophyCondition.TOP_10,
            icon=awards.top_10_icon,
            name=f"Top 10 - {competition.name}",
        )

        # Rank 2 has no trophy at all.
        assert not Trophy.objects.filter(
            bot=other_bot,
            competition=competition,
        ).exists()

        response = self.mutate(
            login_user=admin,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        result = response["awardCompetitionTrophies"]

        assert result["success"] is True

        assert result["deletedTrophyCount"] == 1
        assert result["deletedTrophyIds"] == [str(incorrect.id)]

        # Both correct trophies need creating:
        # the bad rank-1 trophy was removed and rank 2
        # was missing.
        assert result["createdTrophyCount"] == 2

        assert not Trophy.objects.filter(id=incorrect.id).exists()

        assert (
            Trophy.objects.filter(
                competition=competition,
                bot=bot,
                condition=TrophyCondition.FIRST_PLACE,
                icon=awards.first_icon,
            ).count()
            == 1
        )

        assert (
            Trophy.objects.filter(
                competition=competition,
                bot=other_bot,
                condition=TrophyCondition.SECOND_PLACE,
                icon=awards.second_icon,
            ).count()
            == 1
        )

        competition.refresh_from_db()
        assert competition.awards_given is True

    def test_does_not_touch_trophies_from_other_competitions(
        self,
        user,
        competition,
        competition_factory,
        game_mode,
        bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        configure_competition(
            competition,
            status="closed",
        )

        mock_rankings(
            monkeypatch,
            [bot],
        )

        other_competition = competition_factory(
            name="Do Not Touch Me",
            game_mode=game_mode,
            status="closed",
        )

        unrelated_icon = TrophyIcon.objects.create(
            name="unrelated-icon",
            image="trophy_images/unrelated.png",
        )

        unrelated_trophy = Trophy.objects.create(
            bot=bot,
            competition=other_competition,
            condition=TrophyCondition.CUSTOM,
            icon=unrelated_icon,
            name="Some completely unrelated trophy",
        )

        self.mutate(
            login_user=admin,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        # A targeted reconciliation must never delete a trophy
        # belonging to a different competition.
        unrelated_trophy.refresh_from_db()

        assert unrelated_trophy.competition == other_competition
        assert unrelated_trophy.condition == TrophyCondition.CUSTOM
        assert unrelated_trophy.icon == unrelated_icon

    def test_repeated_award_request_does_not_duplicate_trophies(
        self,
        user,
        competition,
        bot,
        monkeypatch,
    ):
        admin = make_admin(user)

        configure_competition(
            competition,
            status="closed",
        )

        mock_rankings(
            monkeypatch,
            [bot],
        )

        variables = {
            "input": {
                "competition": self.to_global_id(
                    CompetitionType,
                    competition.id,
                ),
            }
        }

        first_response = self.mutate(
            login_user=admin,
            variables=variables,
        )

        assert first_response["awardCompetitionTrophies"]["createdTrophyCount"] == 1

        assert Trophy.objects.filter(competition=competition).count() == 1

        second_response = self.mutate(
            login_user=admin,
            variables=variables,
        )

        second = second_response["awardCompetitionTrophies"]

        assert second["success"] is True
        assert second["createdTrophyCount"] == 0
        assert second["deletedTrophyCount"] == 0

        # Most important assertion: no duplicate trophy.
        assert Trophy.objects.filter(competition=competition).count() == 1

    def test_non_admin_cannot_award(
        self,
        user,
        competition,
    ):
        before = Trophy.objects.count()

        self.mutate(
            login_user=user,
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
            expected_errors_like=[
                ADMIN_REQUIRED_MESSAGE,
            ],
        )

        assert Trophy.objects.count() == before

        competition.refresh_from_db()
        assert competition.awards_given is False

    def test_anonymous_cannot_award(
        self,
        competition,
    ):
        before = Trophy.objects.count()

        self.mutate(
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
            expected_errors_like=[
                NOT_LOGGED_IN_MESSAGE,
            ],
        )

        assert Trophy.objects.count() == before

        competition.refresh_from_db()
        assert competition.awards_given is False

    def test_invalid_competition_id_cannot_mutate_data(
        self,
        user,
    ):
        admin = make_admin(user)

        trophy_count = Trophy.objects.count()

        self.mutate(
            login_user=admin,
            expected_status=400,
            variables={
                "input": {
                    "competition": ("Robert'); DROP TABLE core_trophy; --"),
                }
            },
            expected_errors_like=[
                "Invalid ID format",
            ],
        )

        assert Trophy.objects.count() == trophy_count

    def test_open_competition_cannot_be_awarded(
        self,
        user,
        competition,
        bot,
        monkeypatch,
    ):
        """
        Only closed competitions may have trophies awarded.
        """
        admin = make_admin(user)

        configure_competition(
            competition,
            status="open",
        )

        mock_rankings(
            monkeypatch,
            [bot],
        )

        assert competition.status == "open"

        response = self.mutate(
            login_user=admin,
            expected_status=200,
            variables={
                "input": {
                    "competition": self.to_global_id(
                        CompetitionType,
                        competition.id,
                    ),
                }
            },
        )

        result = response["awardCompetitionTrophies"]

        assert result["success"] is False
        assert result["message"] == ("Competition must be closed before trophies can be awarded.")

        assert not Trophy.objects.filter(competition=competition).exists()

        competition.refresh_from_db()
        assert competition.awards_given is False
