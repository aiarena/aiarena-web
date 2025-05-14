import asyncio
import concurrent.futures
from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from asgiref.sync import sync_to_async

from aiarena.core.models import MatchParticipation, Result


class Command(BaseCommand):
    help = "Cleanup and remove old match logfiles."

    _DEFAULT_DAYS_LOOKBACK = 30

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            help=f"Number of days into the past to start cleaning from. Default is {self._DEFAULT_DAYS_LOOKBACK}.",
        )
        parser.add_argument("--verbose", action="store_true", help="Output information with each action.")

    def handle(self, *args, **options):
        if options["days"] is not None:
            days = options["days"]
        else:
            days = self._DEFAULT_DAYS_LOOKBACK
        self._perform_cleanup(days, options["verbose"])

    def _perform_cleanup(self, days, verbose):
        asyncio.run(self.cleanup_result_files(days, verbose))
        self.cleanup_match_participant_logs(days, verbose)

    def cleanup_match_participant_logs(self, days, verbose):
        self.stdout.write(f"Cleaning up match logfiles starting from {days} days into the past...")
        self.stdout.write("Gathering records to clean...")
        participants_qs = (
            MatchParticipation.objects.exclude(match_log="")
            .filter(match__result__created__lt=timezone.now() - timedelta(days=days))
            .only("id", "match_log", "match")
        )
        participants_count = participants_qs.count()
        self.stdout.write(f"{participants_count} records gathered.")
        cleanup_count = 0
        processed_participants = 0
        for participant in participants_qs.iterator():
            if participant.clean_match_log():
                participant.save()
                cleanup_count += 1
                if verbose:
                    self.stdout.write(f"Participant {participant.id} match log deleted.")
            processed_participants += 1
            if processed_participants % 100 == 0 or processed_participants == participants_count:
                self.stdout.write(
                    f"\rProgress: {processed_participants}/{participants_count}",
                    ending="",
                )
        self.stdout.write("\n")
        self.stdout.write(f"Cleaned up {cleanup_count} logfiles.")

    async def cleanup_result_files(self, days, verbose):
        self.stdout.write(f"Cleaning up result files starting from {days} days into the past...")
        self.stdout.write("Gathering records to clean...")

        # Use sync_to_async for database operations
        get_results_count = sync_to_async(self._get_results_count)
        get_results_batch = sync_to_async(self._get_results_batch)

        # Get the date cutoff
        cutoff_date = timezone.now() - timedelta(days=days)

        # Get count synchronously first
        results_count = await get_results_count(cutoff_date)
        self.stdout.write(f"{results_count} records gathered.")

        replays_cleaned_count = 0
        ac_logs_cleaned_count = 0
        processed_count = 0

        batch_size = 100

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(0, results_count, batch_size):
                # Get batch of results using sync_to_async wrapper
                batch = await get_results_batch(cutoff_date, i, batch_size)

                tasks = [self._process_result(result, executor, verbose) for result in batch]
                results = await asyncio.gather(*tasks)

                for replay_cleaned, ac_log_cleaned in results:
                    if replay_cleaned:
                        replays_cleaned_count += 1
                    if ac_log_cleaned:
                        ac_logs_cleaned_count += 1
                    processed_count += 1

                    if processed_count % 100 == 0 or processed_count == results_count:
                        self.stdout.write(
                            f"\rProgress: {processed_count}/{results_count}",
                            ending="",
                        )

        self.stdout.write("\n")
        self.stdout.write(f"Cleaned up {replays_cleaned_count} replays and {ac_logs_cleaned_count} arena client logs.")

    def _get_results_count(self, cutoff_date):
        """Get the count of results to process - runs in synchronous context"""
        return Result.objects.exclude(replay_file="", arenaclient_log="").filter(created__lt=cutoff_date).count()

    def _get_results_batch(self, cutoff_date, offset, limit):
        """Get a batch of results - runs in synchronous context"""
        return list(
            Result.objects.exclude(replay_file="", arenaclient_log="")
            .filter(created__lt=cutoff_date)
            .only("id", "replay_file", "arenaclient_log", "match", "created")[offset : offset + limit]
        )

    async def _process_result(self, result, executor, verbose):
        replay_cleaned, ac_log_cleaned = await self._clean_result_files(result, executor)

        if replay_cleaned or ac_log_cleaned:
            await asyncio.get_event_loop().run_in_executor(
                executor, self._save_result, result, replay_cleaned, ac_log_cleaned, verbose
            )
        elif result.replay_file or result.arenaclient_log:
            self.stdout.write(f"WARNING: Match {result.match.id} had no files to clean up even though it should have.")

        return replay_cleaned, ac_log_cleaned

    async def _clean_result_files(self, result, executor):
        replay_cleaned = await asyncio.get_event_loop().run_in_executor(executor, result.clean_replay_file)
        ac_log_cleaned = await asyncio.get_event_loop().run_in_executor(executor, result.clean_arenaclient_log)
        return replay_cleaned, ac_log_cleaned

    def _save_result(self, result, replay_cleaned, ac_log_cleaned, verbose):
        result.save()
        if verbose:
            if replay_cleaned:
                self.stdout.write(f"Match {result.match.id} replay file deleted.")
            if ac_log_cleaned:
                self.stdout.write(f"Match {result.match.id} arenaclient log deleted.")
