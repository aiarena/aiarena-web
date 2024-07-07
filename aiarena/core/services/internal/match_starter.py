import logging

from django.utils import timezone

from aiarena.core.models import ArenaClient, Match, MatchParticipation


logger = logging.getLogger(__name__)


class MatchStarter:
    """
    Responsible for starting a given competition match, including all necessary checks.
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
        participations = MatchParticipation.objects.raw(
            """
            SELECT cm.id FROM core_matchparticipation cm
            where ((cm.use_bot_data or cm.update_bot_data) or cm.bot_id not in (
                    select bot_id
                    from core_matchparticipation
                    inner join core_match m on core_matchparticipation.match_id = m.id
                    left join core_result cr on m.result_id = cr.id
                    where m.started is not null
                    and cr.type is null
                    and (core_matchparticipation.use_bot_data  or core_matchparticipation.update_bot_data)       
                    and m.id != %s 
                )) and match_id = %s
                """,
            (match.id, match.id),
        )

        if len(participations) < 2:
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
