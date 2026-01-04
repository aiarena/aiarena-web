import logging

from django.db.models import Exists, OuterRef, Q
from django.utils import timezone

from aiarena.core.models import ArenaClient, Match, MatchParticipation


logger = logging.getLogger(__name__)


class MatchStarter:
    """
    Responsible for starting a given match, including all necessary checks.
    """

    @staticmethod
    def start(match: Match, arenaclient: ArenaClient) -> bool:
        """
        Start the match.
        """
        if MatchStarter.__requires_trusted_arenaclient(match) and not arenaclient.trusted:
            return False

        match.lock_me()  # lock self to avoid race conditions

        if match.is_already_started:
            logger.warning(f"Match {match.id} failed to start unexpectedly as it was already started.")
            return False

        # Avoid starting a match when a participant is not available
        target_match_not_locked_by_bot_data = Q(use_bot_data=False) | Q(
            update_bot_data=False, match__requested_by__isnull=False
        )
        not_in_another_match = ~Exists(
            MatchParticipation.objects.exclude(
                match_id=match.id,
            ).filter(
                bot_id=OuterRef("bot_id"),
                use_bot_data=True,
                update_bot_data=True,
                match__started__isnull=False,
                match__result=None,
            )
        )
        available_participants = MatchParticipation.objects.filter(
            target_match_not_locked_by_bot_data | not_in_another_match,
            match_id=match.id,
        ).only("id")

        if len(available_participants) < 2:
            # Todo: Commented out to avoid log spam. This used to be a last second sanity check.
            # Todo: Investigate whether it is still the case or whether this is no longer considered a system fault
            # Todo: worthy of a warning message being logged.
            # logger.warning(f"Match {match.id} failed to start unexpectedly"
            #                f" because one of the participants was not available.")
            return False

        # If all checks pass, start the match
        match.started = match.first_started = timezone.now()
        match.assigned_to = arenaclient
        match.save()
        return True

    @staticmethod
    def __requires_trusted_arenaclient(match):
        require_trusted_arenaclient = match.require_trusted_arenaclient or (
            not match.participant1.bot.bot_zip_publicly_downloadable
            or not match.participant2.bot.bot_zip_publicly_downloadable
            or not match.participant1.bot.bot_data_publicly_downloadable
            or not match.participant2.bot.bot_data_publicly_downloadable
        )
        return require_trusted_arenaclient
