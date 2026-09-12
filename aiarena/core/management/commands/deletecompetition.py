from django.core.management.base import BaseCommand, CommandError

from aiarena.core.models import Competition, CompetitionParticipation, Match, MatchParticipation, Result, Round


class Command(BaseCommand):
    help = (
        "Permanently deletes a competition, along with all its rounds, matches, participations, "
        "and any associated replay files, arena client logs and match logs in storage. "
        "This action cannot be undone."
    )

    def add_arguments(self, parser):
        parser.add_argument("competition_id", type=int, help="The id of the competition to delete.")
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            help="Do not prompt for confirmation.",
        )

    def handle(self, *args, **options):
        try:
            competition = Competition.objects.get(id=options["competition_id"])
        except Competition.DoesNotExist:
            raise CommandError(f"Competition with id {options['competition_id']} does not exist.")

        round_count = Round.objects.filter(competition=competition).count()
        match_count = Match.objects.filter(round__competition=competition).count()
        participation_count = CompetitionParticipation.objects.filter(competition=competition).count()
        replay_file_count = Result.objects.filter(match__round__competition=competition).exclude(replay_file="").count()
        arenaclient_log_count = (
            Result.objects.filter(match__round__competition=competition).exclude(arenaclient_log="").count()
        )
        match_log_count = (
            MatchParticipation.objects.filter(match__round__competition=competition).exclude(match_log="").count()
        )

        self.stdout.write("You are about to PERMANENTLY DELETE the following competition:")
        self.stdout.write(f"  ID:                  {competition.id}")
        self.stdout.write(f"  Name:                {competition.name}")
        self.stdout.write(f"  Status:              {competition.status}")
        self.stdout.write(f"  Game mode:           {competition.game_mode}")
        self.stdout.write(f"  Date created:        {competition.date_created}")
        self.stdout.write(f"  Date opened:         {competition.date_opened}")
        self.stdout.write(f"  Date closed:         {competition.date_closed}")
        self.stdout.write(f"  Rounds:              {round_count}")
        self.stdout.write(f"  Matches:             {match_count}")
        self.stdout.write(f"  Participations:      {participation_count}")
        self.stdout.write(f"  Replay files:        {replay_file_count}")
        self.stdout.write(f"  Arena client logs:   {arenaclient_log_count}")
        self.stdout.write(f"  Match logs:          {match_log_count}")
        self.stdout.write("")
        self.stdout.write(
            self.style.WARNING(
                "This will also delete all of the rounds, matches and participations listed above, "
                "along with their replay files, arena client logs and match logs in storage. "
                "This action cannot be undone."
            )
        )

        if options["interactive"]:
            confirm = input(
                f"\nType the competition's name ('{competition.name}') to confirm deletion, "
                f"or anything else to cancel: "
            )
        else:
            confirm = competition.name

        if confirm == competition.name:
            self._delete_storage_files(competition)
            competition_id, competition_name = competition.id, competition.name
            competition.delete()
            self.stdout.write(self.style.SUCCESS(f"Competition {competition_id} ({competition_name}) deleted."))
        else:
            self.stdout.write("Deletion cancelled.")

    def _delete_storage_files(self, competition):
        results = Result.objects.filter(match__round__competition=competition).exclude(
            replay_file="", arenaclient_log=""
        )
        cleaned_results = 0
        for result in results.iterator():
            replay_cleaned = result.clean_replay_file()
            log_cleaned = result.clean_arenaclient_log()
            if replay_cleaned or log_cleaned:
                result.save()
                cleaned_results += 1
        if cleaned_results:
            self.stdout.write(f"Cleaned up storage files for {cleaned_results} results.")

        participations = MatchParticipation.objects.filter(match__round__competition=competition).exclude(match_log="")
        cleaned_participations = 0
        for participation in participations.iterator():
            if participation.clean_match_log():
                participation.save()
                cleaned_participations += 1
        if cleaned_participations:
            self.stdout.write(f"Cleaned up match logs for {cleaned_participations} participations.")
