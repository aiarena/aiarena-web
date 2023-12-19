from django.core.management import call_command

from aiarena.core.management.commands.basefilecleanupcommand import BaseFileCleanupCommand


class Command(BaseFileCleanupCommand):
    help = "Cleanup and remove old match logfiles."

    _DEFAULT_DAYS_LOOKBACK = 30

    def _perform_cleanup(self, days, verbose):
        call_command("cleanupresultfiles", days=days, verbosity=verbose)
        call_command("cleanupmatchlogfiles", days=days, verbosity=verbose)
