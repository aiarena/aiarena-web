from django.core.management.base import BaseCommand
from django.utils import timezone

from constance import config

from aiarena.core.match_interest_analyzer import MatchInterestAnalyzer
from aiarena.core.models import Match


class Command(BaseCommand):
    help = 'Runs analysis on matches to determine how "interesting" they were.'

    def add_arguments(self, parser):
        parser.add_argument("num_matches", type=int, default=1, help="The number of matches to analyze")

    def handle(self, *args, **options):
        num_matches = options["num_matches"]

        self.stdout.write(f"Analyzing {num_matches} matches...")

        analyzer = MatchInterestAnalyzer(config.ELO_DIFF_RATING_MODIFIER, config.COMBINED_ELO_RATING_DIVISOR)

        # if a result has a round, it's a ladder match
        for i, match in enumerate(Match.objects.filter(round__isnull=False).order_by("-result__created")):
            match.result.interest_rating = analyzer.rate_match(match)
            match.result.date_interest_rating_calculated = timezone.now()
            match.result.save()
            self.stdout.write(f"Match {match.id} analyzed")

            if i >= num_matches - 1:
                break

        self.stdout.write("Analysis finished.")
