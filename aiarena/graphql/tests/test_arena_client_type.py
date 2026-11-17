from datetime import timedelta

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from aiarena.core.models import ArenaClient, Match, MatchParticipation, Result
from aiarena.core.tests.base import GraphQLTest
from aiarena.graphql import ArenaClientType


def _submit_results(arena_client, *ages):
    """One result per age, submitted by `arena_client` that long ago."""
    for age in ages:
        result = Result.objects.create(type="MatchCancelled", game_steps=0, submitted_by=arena_client)
        Result.objects.filter(id=result.id).update(created=timezone.now() - age)


class TestArenaClients(GraphQLTest):
    # language=graphql
    query_text = """
        query {
            arenaClients {
                edges {
                    node {
                        username
                        trusted
                        owner { username }
                        matches1h
                        matches24h
                    }
                }
            }
        }
    """

    def _clients(self, **kwargs):
        data = self.query(self.query_text, **kwargs)
        return [edge["node"] for edge in data["arenaClients"]["edges"]]

    def test_lists_active_clients_with_recent_match_counts(self, arenaclient_user):
        _submit_results(
            arenaclient_user,
            timedelta(minutes=10),  # last hour (and last 24h)
            timedelta(minutes=50),  # last hour (and last 24h)
            timedelta(hours=5),  # last 24h only
            timedelta(days=3),  # neither
        )

        assert self._clients() == [
            {
                "username": "ac1",
                "trusted": True,
                "owner": {"username": arenaclient_user.owner.username},
                "matches1h": 2,
                "matches24h": 3,
            }
        ]

    def test_inactive_clients_are_not_listed(self, arenaclient_user):
        ArenaClient.objects.filter(id=arenaclient_user.id).update(is_active=False)

        assert self._clients() == []

    def test_is_public(self, arenaclient_user, user):
        """Anyone can see the list, signed in or not, as with the old page."""
        assert len(self._clients()) == 1
        assert len(self._clients(login_user=user)) == 1

    def test_exposes_only_allowlisted_account_fields(self, db):
        """Arena clients are user accounts: nothing beyond the allowlist (email,
        password, login state, ...) may appear on the type."""
        # language=graphql
        introspection = """
            { __type(name: "ArenaClientType") { fields { name } } }
        """
        data = self.query(introspection)
        exposed = {f["name"] for f in data["__type"]["fields"]}

        assert exposed == {
            "id",
            "databaseId",
            "username",
            "trusted",
            "owner",
            "matches1h",
            "matches24h",
            "matchesTotal",
            "assignedMatches",
            "recentResults",
        }


class TestArenaClientDetail(GraphQLTest):
    # language=graphql
    query_text = """
        query ($id: ID!) {
            node(id: $id) {
                ... on ArenaClientType {
                    username
                    matchesTotal
                    assignedMatches {
                        participant1 { name }
                        participant2 { name }
                        map { name }
                    }
                    recentResults {
                        type
                        participant1 { bot { name } }
                        participant2 { bot { name } }
                    }
                }
            }
        }
    """

    def _client(self, arena_client):
        data = self.query(self.query_text, variables={"id": self.to_global_id(ArenaClientType, arena_client.id)})
        return data["node"]

    def _finished_match(self, arena_client, bot, other_bot, map, result_type):
        result = Result.objects.create(type=result_type, game_steps=0, submitted_by=arena_client)
        match = Match.objects.create(map=map, assigned_to=arena_client, result=result)
        MatchParticipation.objects.create(match=match, participant_number=1, bot=bot)
        MatchParticipation.objects.create(match=match, participant_number=2, bot=other_bot)
        return match

    def test_shows_assigned_matches_results_and_total(self, arenaclient_user, queued_match, bot, other_bot, map):
        queued_match.assigned_to = arenaclient_user
        queued_match.save()
        self._finished_match(arenaclient_user, bot, other_bot, map, "MatchCancelled")
        self._finished_match(arenaclient_user, bot, other_bot, map, "Error")

        client = self._client(arenaclient_user)

        assert client["username"] == "ac1"
        assert client["matchesTotal"] == 2
        # Only the unfinished match is "assigned"; finished ones are results.
        assert client["assignedMatches"] == [
            {"participant1": {"name": bot.name}, "participant2": {"name": other_bot.name}, "map": {"name": map.name}}
        ]
        results = client["recentResults"]
        # Newest first.
        assert [r["type"] for r in results] == ["ERROR", "MATCHCANCELLED"]
        assert results[0]["participant1"] == {"bot": {"name": bot.name}}
        assert results[0]["participant2"] == {"bot": {"name": other_bot.name}}

    def test_total_counts_submitted_results_while_list_shows_assigned_matches(
        self, arenaclient_user, admin_user, bot, other_bot, map
    ):
        """The count is what the client submitted; the results list is every
        match assigned to it. They differ by timeouts: matches the client was
        given but never reported back, which the system cancels unsubmitted."""
        other_client = ArenaClient.objects.create(
            username="ac2", email="ac2@dev.aiarena.net", type="ARENA_CLIENT", owner=admin_user
        )
        # Assigned here and submitted by this client: a normal played match.
        self._finished_match(arenaclient_user, bot, other_bot, map, "Error")
        # Assigned here but cancelled by the system on timeout, with no submitter.
        timed_out = self._finished_match(arenaclient_user, bot, other_bot, map, "MatchCancelled")
        timed_out.result.submitted_by = None
        timed_out.result.save()
        # Submitted by this client, but the match was assigned elsewhere.
        assigned_elsewhere = self._finished_match(other_client, bot, other_bot, map, "MatchCancelled")
        assigned_elsewhere.result.submitted_by = arenaclient_user
        assigned_elsewhere.result.save()

        client = self._client(arenaclient_user)

        # Submitted: the played match and `assigned_elsewhere`.
        assert client["matchesTotal"] == 2
        # Assigned, newest first: `timed_out` and the played match.
        listed = client["recentResults"]
        assert [r["type"] for r in listed] == ["MATCHCANCELLED", "ERROR"]

    def test_other_clients_matches_are_not_included(self, arenaclient_user, admin_user, bot, other_bot, map):
        other_client = ArenaClient.objects.create(
            username="ac2", email="ac2@dev.aiarena.net", type="ARENA_CLIENT", owner=admin_user
        )
        self._finished_match(other_client, bot, other_bot, map, "MatchCancelled")

        client = self._client(arenaclient_user)

        assert client["matchesTotal"] == 0
        assert client["assignedMatches"] == []
        assert client["recentResults"] == []


class TestArenaClientRecentResults(GraphQLTest):
    # language=graphql
    query_text = """
        query ($id: ID!) {
            node(id: $id) {
                ... on ArenaClientType {
                    recentResults { gameSteps }
                }
            }
        }
    """

    def test_lists_only_the_latest_100_without_counting(self, arenaclient_user, map):
        """Capped at the newest 100, and never counted: counting a busy
        client's ~300k results is what made this page take ~20s."""
        for steps in range(101):
            result = Result.objects.create(type="MatchCancelled", game_steps=steps, submitted_by=arenaclient_user)
            Match.objects.create(map=map, assigned_to=arenaclient_user, result=result)

        with CaptureQueriesContext(connection) as queries:
            data = self.query(
                self.query_text, variables={"id": self.to_global_id(ArenaClientType, arenaclient_user.id)}
            )

        steps = [r["gameSteps"] for r in data["node"]["recentResults"]]
        # Newest first, and the oldest (game_steps=0) didn't make the cut.
        assert steps == list(range(100, 0, -1))
        # Django's .count() aliases its result "__count"; nothing may count the
        # client's results. (The 1h/24h numbers are subqueries, not .count().)
        assert not [q["sql"] for q in queries if '"__count"' in q["sql"] and "core_match" in q["sql"]]
