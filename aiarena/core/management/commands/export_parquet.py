import re
from pathlib import Path
from uuid import UUID

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models.signals import post_delete

import pandas as pd

from aiarena.core.models import (
    Bot,
    BotRace,
    Competition,
    Game,
    GameMode,
    Map,
    Match,
    MatchParticipation,
    MatchTag,
    Result,
    Round,
    Tag,
)
from aiarena.core.models.match_tag import delete_orphan_tags


GAME_FIELDS = ["id", "name", "map_file_extension"]
GAME_MODE_FIELDS = ["id", "name", "game_id", "game__name"]

COMPETITION_FIELDS = [
    "id",
    "name",
    "game_mode_id",
    "game_mode__name",
    "game_mode__game_id",
    "game_mode__game__name",
    "date_created",
    "date_opened",
    "date_closed",
    "status",
    "max_active_rounds",
    "interest",
    "target_n_divisions",
    "n_divisions",
    "target_division_size",
    "rounds_per_cycle",
    "rounds_this_cycle",
    "n_placements",
    "require_trusted_infrastructure",
    "statistics_finalized",
    "competition_finalized",
    "indepth_bot_statistics_enabled",
]

PLAYABLE_RACE_FIELDS = ["id", "label"]
MAP_FIELDS = ["id", "name", "game_mode_id", "game_mode__name", "enabled"]
ROUND_FIELDS = ["id", "number", "competition_id", "started", "finished", "complete"]

MATCH_FIELDS = [
    "id",
    "result_id",
    "map_id",
    "map__name",
    "created",
    "started",
    "first_started",
    "round_id",
    "assigned_to_id",
    "assigned_to__username",
    "requested_by_id",
    "requested_by__username",
    "require_trusted_arenaclient",
]

RESULT_FIELDS = [
    "id",
    "type",
    "created",
    "winner_id",
    "winner__name",
    "winner__game_display_id",
    "winner__plays_race_id",
    "winner__plays_race__label",
    "game_steps",
    "submitted_by_id",
    "submitted_by__username",
    "replay_file_has_been_cleaned",
    "arenaclient_log_has_been_cleaned",
]

MATCH_MATCH_TAG_FIELDS = ["match_id", "matchtag_id"]
MATCH_TAG_FIELDS = ["id", "tag_id", "tag__name", "user_id", "user__username"]
TAG_FIELDS = ["id", "name"]

MATCH_PARTICIPATION_FIELDS = [
    "id",
    "match_id",
    "participant_number",
    "bot_id",
    "bot__name",
    "bot__game_display_id",
    "bot__plays_race_id",
    "bot__plays_race__label",
    "bot__type",
    "bot__user_id",
    "bot__user__username",
    "starting_elo",
    "resultant_elo",
    "elo_change",
    "avg_step_time",
    "result",
    "result_cause",
    "use_bot_data",
    "update_bot_data",
    "match_log_has_been_cleaned",
]

BOT_FIELDS = [
    "id",
    "name",
    "created",
    "plays_race_id",
    "plays_race__label",
    "type",
    "game_display_id",
    "user_id",
    "user__username",
    "bot_zip_publicly_downloadable",
    "bot_data_enabled",
    "bot_data_publicly_downloadable",
]


class Command(BaseCommand):
    help = "Export competition or requested bot matches to sanitized Parquet."

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="mode", required=True)

        competition_parser = subparsers.add_parser("competition")
        competition_parser.add_argument("competition_id", type=int)

        all_competitions_parser = subparsers.add_parser("all_competitions")
        all_competitions_parser.add_argument("year", type=int)

        requested_parser = subparsers.add_parser("requested")
        requested_parser.add_argument("user_id", type=int)
        requested_parser.add_argument("year", type=int)

        all_requests_parser = subparsers.add_parser("all_requests")
        all_requests_parser.add_argument("year", type=int)

        parser.add_argument("--output-dir", default="exports")

    def write_parquet(self, qs, path, fields):
        rows = list(qs)
        df = pd.DataFrame.from_records(rows, columns=fields)

        for column in df.columns:
            if df[column].map(lambda value: isinstance(value, UUID)).any():
                df[column] = df[column].map(lambda value: str(value) if value is not None else None)

        df.to_parquet(path, index=False)

        row_count = len(df)
        self.stdout.write(f"{path.name}: {row_count} rows")

        return row_count

    def safe_name(self, value):
        value = value.strip().lower()
        value = re.sub(r"[^a-z0-9_-]+", "_", value)
        return value.strip("_") or "unknown"

    def handle(self, *args, **options):
        mode = options["mode"]
        base_output_dir = Path(options["output_dir"])

        if mode == "competition":
            self.export_competition(
                options["competition_id"],
                base_output_dir,
            )

        elif mode == "all_competitions":
            self.export_all_competitions(
                options["year"],
                base_output_dir,
            )

        elif mode == "requested":
            self.export_requested_matches(
                options["user_id"],
                options["year"],
                base_output_dir,
            )

        elif mode == "all_requests":
            self.export_all_requested_matches(
                options["year"],
                base_output_dir,
            )

        else:
            raise CommandError("Unknown mode")

    def export_competition(self, competition_id, base_output_dir):
        output_dir = base_output_dir / f"competition_{competition_id}"
        output_dir.mkdir(parents=True, exist_ok=True)

        competition = Competition.objects.get(id=competition_id)

        if competition.playable_races.exists():
            playable_races_qs = competition.playable_races.values(*PLAYABLE_RACE_FIELDS)
        else:
            playable_races_qs = BotRace.objects.all().values(*PLAYABLE_RACE_FIELDS)

        rounds = Round.objects.filter(competition_id=competition_id)
        matches = Match.objects.filter(round__competition_id=competition_id)

        ds = self.export_match_dataset(
            output_dir=output_dir,
            matches=matches,
            rounds=rounds,
            playable_races_qs=playable_races_qs,
            competition_qs=Competition.objects.filter(id=competition_id),
            success_message=f"Finished sanitized Parquet export for competition {competition_id}",
        )

        # self.cleanup_exported_competition_data(
        #         competition.id
        # )
        return ds

    def export_all_competitions(self, year, base_output_dir):
        competitions = Competition.objects.filter(
            date_closed__year=year,
        ).order_by("id")
        total_rows = 0
        exported_competitions = []

        for competition in competitions:
            self.stdout.write(
                self.style.HTTP_INFO(f"Starting export for competition {competition.id} ({competition.name})")
            )

            rows_exported = self.export_competition(
                competition.id,
                base_output_dir,
            )

            total_rows += rows_exported or 0

            exported_competitions.append(
                {
                    "id": competition.id,
                    "name": competition.name,
                }
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Finished sanitized Parquet export for {len(exported_competitions)} competitions closed in {year}"
            )
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Exported competitions:"))

        for competition in exported_competitions:
            self.stdout.write(f"- {competition['id']}: {competition['name']}")

        self.stdout.write(self.style.SUCCESS(f"Total exported rows across all competitions: {total_rows:,}"))

    def export_requested_matches(self, user_id, year, base_output_dir):
        output_dir = base_output_dir / "requested_matches" / f"user_{user_id}" / str(year)
        output_dir.mkdir(parents=True, exist_ok=True)

        matches = Match.objects.filter(
            requested_by_id=user_id,
            created__year=year,
        ).distinct()

        self.export_match_dataset(
            output_dir=output_dir,
            matches=matches,
            rounds=Round.objects.none(),
            playable_races_qs=BotRace.objects.all().values(*PLAYABLE_RACE_FIELDS),
            competition_qs=Competition.objects.none(),
            success_message=f"Finished sanitized Parquet export for requested matches by user {user_id} in {year}",
        )

    def export_all_requested_matches(self, year, base_output_dir):
        total_rows = 0
        exported_users = []

        all_output_dir = base_output_dir / "requested_matches" / "all_users" / str(year)
        all_output_dir.mkdir(parents=True, exist_ok=True)

        all_matches = Match.objects.filter(
            requested_by_id__isnull=False,
            created__year=year,
        ).distinct()

        rows_exported = self.export_match_dataset(
            output_dir=all_output_dir,
            matches=all_matches,
            rounds=Round.objects.none(),
            playable_races_qs=BotRace.objects.all().values(*PLAYABLE_RACE_FIELDS),
            competition_qs=Competition.objects.none(),
            success_message=f"Finished sanitized Parquet export for all requested matches in {year}",
        )

        total_rows += rows_exported or 0

        user_ids = all_matches.values_list("requested_by_id", flat=True).distinct()

        for user_id in user_ids:
            output_dir = base_output_dir / "requested_matches" / f"user_{user_id}" / str(year)
            output_dir.mkdir(parents=True, exist_ok=True)

            matches = all_matches.filter(
                requested_by_id=user_id,
            ).distinct()

            rows_exported = self.export_match_dataset(
                output_dir=output_dir,
                matches=matches,
                rounds=Round.objects.none(),
                playable_races_qs=BotRace.objects.all().values(*PLAYABLE_RACE_FIELDS),
                competition_qs=Competition.objects.none(),
                success_message=f"Finished sanitized Parquet export for requested matches by user {user_id} in {year}",
            )

            total_rows += rows_exported or 0

            exported_users.append(user_id)

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(f"Finished exporting requested matches for {len(exported_users):,} users in {year}")
        )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Exported users:"))

        for user_id in exported_users:
            self.stdout.write(f"- user_{user_id}")

        self.stdout.write(self.style.SUCCESS(f"Total exported rows across all requested exports: {total_rows:,}"))

    def cleanup_exported_competition_data(self, competition_id):
        self.stdout.write(self.style.WARNING(f"Cleaning up exported DB data for competition {competition_id}"))

        with transaction.atomic():
            rounds = Round.objects.filter(competition_id=competition_id)

            matches = Match.objects.filter(round__competition_id=competition_id)

            match_ids = list(matches.values_list("id", flat=True))
            result_ids = list(matches.exclude(result_id__isnull=True).values_list("result_id", flat=True))

            # delete m2m rows first
            Match.tags.through.objects.filter(match_id__in=match_ids).delete()

            # delete participations
            MatchParticipation.objects.filter(match_id__in=match_ids).delete()

            # delete matches
            matches.delete()

            # delete results
            Result.objects.filter(id__in=result_ids).delete()

            # delete rounds
            rounds.delete()

            # delete orphaned match tags
            orphaned_match_tags = MatchTag.objects.filter(match__isnull=True)

            orphaned_tag_ids = list(orphaned_match_tags.values_list("tag_id", flat=True))

            post_delete.disconnect(
                delete_orphan_tags,
                sender=MatchTag,
            )

            try:
                orphaned_match_tags.delete()
            finally:
                post_delete.connect(
                    delete_orphan_tags,
                    sender=MatchTag,
                )

            # delete orphaned tags
            used_tag_ids = MatchTag.objects.values_list(
                "tag_id",
                flat=True,
            ).distinct()

            Tag.objects.filter(id__in=orphaned_tag_ids).exclude(id__in=used_tag_ids).delete()

            # finally delete competition
            Competition.objects.filter(id=competition_id).delete()

        self.stdout.write(self.style.SUCCESS(f"Finished cleanup for competition {competition_id}"))

    def export_match_dataset(
        self,
        output_dir,
        matches,
        rounds,
        playable_races_qs,
        competition_qs,
        success_message,
    ):
        total_rows = 0

        result_ids = matches.exclude(result_id__isnull=True).values_list("result_id", flat=True)
        results = Result.objects.filter(id__in=result_ids)

        participations = MatchParticipation.objects.filter(match_id__in=matches.values_list("id", flat=True))

        match_ids = matches.values_list("id", flat=True)
        bot_ids = participations.values_list("bot_id", flat=True).distinct()

        map_ids = matches.values_list("map_id", flat=True).distinct()
        maps = Map.objects.filter(id__in=map_ids)

        game_mode_ids = maps.values_list("game_mode_id", flat=True).distinct()
        game_modes = GameMode.objects.filter(id__in=game_mode_ids)
        game_ids = game_modes.values_list("game_id", flat=True).distinct()

        bots = Bot.objects.filter(id__in=bot_ids)

        match_match_tags = Match.tags.through.objects.filter(match_id__in=match_ids)
        match_tag_ids = match_match_tags.values_list("matchtag_id", flat=True).distinct()

        match_tags = MatchTag.objects.filter(id__in=match_tag_ids)
        tag_ids = match_tags.values_list("tag_id", flat=True).distinct()

        total_rows += self.write_parquet(
            Game.objects.filter(id__in=game_ids).values(*GAME_FIELDS), output_dir / "games.parquet", GAME_FIELDS
        )
        total_rows += self.write_parquet(
            game_modes.values(*GAME_MODE_FIELDS), output_dir / "game_modes.parquet", GAME_MODE_FIELDS
        )
        total_rows += self.write_parquet(
            competition_qs.values(*COMPETITION_FIELDS), output_dir / "competitions.parquet", COMPETITION_FIELDS
        )
        total_rows += self.write_parquet(playable_races_qs, output_dir / "playable_races.parquet", PLAYABLE_RACE_FIELDS)
        total_rows += self.write_parquet(maps.values(*MAP_FIELDS), output_dir / "maps.parquet", MAP_FIELDS)
        total_rows += self.write_parquet(rounds.values(*ROUND_FIELDS), output_dir / "rounds.parquet", ROUND_FIELDS)
        total_rows += self.write_parquet(matches.values(*MATCH_FIELDS), output_dir / "matches.parquet", MATCH_FIELDS)
        total_rows += self.write_parquet(results.values(*RESULT_FIELDS), output_dir / "results.parquet", RESULT_FIELDS)
        total_rows += self.write_parquet(
            match_match_tags.values(*MATCH_MATCH_TAG_FIELDS),
            output_dir / "match_match_tags.parquet",
            MATCH_MATCH_TAG_FIELDS,
        )
        total_rows += self.write_parquet(
            match_tags.values(*MATCH_TAG_FIELDS), output_dir / "match_tags.parquet", MATCH_TAG_FIELDS
        )
        total_rows += self.write_parquet(
            Tag.objects.filter(id__in=tag_ids).values(*TAG_FIELDS), output_dir / "tags.parquet", TAG_FIELDS
        )
        total_rows += self.write_parquet(
            participations.values(*MATCH_PARTICIPATION_FIELDS),
            output_dir / "match_participations.parquet",
            MATCH_PARTICIPATION_FIELDS,
        )
        total_rows += self.write_parquet(bots.values(*BOT_FIELDS), output_dir / "bots_sanitized.parquet", BOT_FIELDS)

        self.stdout.write(self.style.SUCCESS(f"{success_message} | Total exported rows: {total_rows:,}"))

        return total_rows
