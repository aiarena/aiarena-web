from datetime import timedelta

from django.utils import timezone

from aiarena.core.models import Match, MatchParticipation, Result, Round
from aiarena.core.tests.base import GraphQLTest


class TestMatchQueue(GraphQLTest):
    # language=graphql
    query_text = """
        query {
            matchQueue {
                requestedMatches {
                    databaseId
                    participant1 { name }
                    participant2 { name }
                    map { name }
                    assignedTo { username }
                }
                rounds {
                    round { number competition { name } }
                    matches { databaseId }
                }
            }
        }
    """

    def _match(self, bot, other_bot, map, *, round=None, started=None, finished=False, assigned_to=None):
        result = Result.objects.create(type="MatchCancelled", game_steps=0) if finished else None
        match = Match.objects.create(map=map, round=round, started=started, result=result, assigned_to=assigned_to)
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=other_bot)
        return match

    def _queue(self, **kwargs):
        return self.query(self.query_text, **kwargs)["matchQueue"]

    def test_requested_matches_are_unfinished_ones_in_queue_order(self, bot, other_bot, map, arenaclient_user):
        now = timezone.now()
        queued_first = self._match(bot, other_bot, map)
        running_later = self._match(bot, other_bot, map, started=now, assigned_to=arenaclient_user)
        running_earlier = self._match(bot, other_bot, map, started=now - timedelta(minutes=5))
        queued_second = self._match(bot, other_bot, map)
        self._match(bot, other_bot, map, finished=True)  # has a result: not in the queue

        requested = self._queue()["requestedMatches"]

        # Running matches by start time, then queued ones by id.
        assert [m["databaseId"] for m in requested] == [
            running_earlier.id,
            running_later.id,
            queued_first.id,
            queued_second.id,
        ]
        running = next(m for m in requested if m["databaseId"] == running_later.id)
        assert running == {
            "databaseId": running_later.id,
            "participant1": {"name": bot.name},
            "participant2": {"name": other_bot.name},
            "map": {"name": map.name},
            "assignedTo": {"username": arenaclient_user.username},
        }

    def test_rounds_are_incomplete_ones_with_their_unfinished_matches(self, competition, bot, other_bot, map):
        done_round = Round.objects.create(competition=competition, complete=True)
        open_round = Round.objects.create(competition=competition)
        self._match(bot, other_bot, map, round=done_round)
        pending = self._match(bot, other_bot, map, round=open_round)
        self._match(bot, other_bot, map, round=open_round, finished=True)

        queue = self._queue()

        assert queue["requestedMatches"] == []
        assert queue["rounds"] == [
            {
                "round": {"number": open_round.number, "competition": {"name": competition.name}},
                "matches": [{"databaseId": pending.id}],
            }
        ]

    def test_empty_queue(self, db):
        assert self._queue() == {"requestedMatches": [], "rounds": []}

    def test_is_public(self, bot, other_bot, map, user):
        """Anyone can see the queue, signed in or not, as with the old page."""
        self._match(bot, other_bot, map)
        assert len(self._queue()["requestedMatches"]) == 1
        assert len(self._queue(login_user=user)["requestedMatches"]) == 1
