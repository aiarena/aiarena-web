from django.core.management.base import BaseCommand


class Command(BaseCommand):
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
        raise NotImplementedError("This method must be implemented in a subclass.")
