from django.db.models import QuerySet

from aiarena.core.models import ArenaClient, Match, Result


class ArenaClients:
    def get_incomplete_assigned_matches_queryset(self, arena_client: ArenaClient) -> QuerySet[Match, Match]:
        """Return matches assigned to the given ArenaClient that have no result yet.

        Parameters
        - arena_client: ArenaClient
            The arena client for which to fetch assigned matches.

        Returns
        - QuerySet[Match]
            A queryset of Match objects assigned to the client and without a Result.
        """
        return Match.objects.filter(assigned_to=arena_client, result__isnull=True)

    def get_assigned_matches_results_queryset(self, arena_client: ArenaClient) -> QuerySet[Result, Result]:
        """Return results for matches that are assigned to the given ArenaClient.

        Parameters
        - arena_client: ArenaClient
            The arena client for which to fetch match results.

        Returns
        - QuerySet[Result]
            A queryset of Result objects whose related Match is assigned to the client.
        """
        return Result.objects.filter(match__assigned_to=arena_client)
