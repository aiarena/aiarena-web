import logging

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from wiki.models import ArticleRevision

from aiarena.core.models import Competition, CompetitionSchedule


logger = logging.getLogger(__name__)


def create_competition(schedule, start, end):
    """
    Create and open a competition from its schedule.

    Must be called while holding a database lock on the schedule.
    """
    competition = Competition.objects.create(
        name=schedule.get_competition_name(start.year),
        game_mode=schedule.game_mode,
        award_set=schedule.award_set,
        max_active_rounds=schedule.max_active_rounds,
        target_n_divisions=schedule.target_n_divisions,
        n_divisions=schedule.n_divisions,
        target_division_size=schedule.target_division_size,
        rounds_per_cycle=schedule.rounds_per_cycle,
        n_placements=schedule.n_placements,
        require_trusted_infrastructure=schedule.require_trusted_infrastructure,
        indepth_bot_statistics_enabled=schedule.indepth_bot_statistics_enabled,
        schedule=schedule,
        scheduled_start=start,
        scheduled_end=end,
    )

    # Copy playable races from the schedule.
    competition.playable_races.set(schedule.playable_races.all())

    # Copy the description from the schedule.
    revision = ArticleRevision()
    revision.inherit_predecessor(competition.wiki_article)
    revision.title = competition.name
    revision.content = schedule.wiki_article_content.replace("{year}", str(start.year))
    competition.wiki_article.add_revision(revision)

    error = competition.open()

    if error:
        raise RuntimeError(f"Failed to open competition {competition.pk}: {error}")

    logger.info(
        "Created and opened competition %s from schedule %s",
        competition.name,
        schedule.pk,
    )

    return competition


def process_schedule(schedule_id, now):
    """
    Process one annual schedule.

    Only creates a competition if the current time falls
    within its scheduled start/end window.
    """
    with transaction.atomic():
        schedule = CompetitionSchedule.objects.select_for_update().get(pk=schedule_id)

        if not schedule.enabled:
            return

        # Check this year's schedule and the previous year's.
        # The previous year is needed for competitions crossing
        # December -> January.
        for year in (now.year - 1, now.year):
            start = schedule.get_start(year)
            end = schedule.get_end(year)

            if not start <= now < end:
                continue

            # Idempotency: don't create the same competition twice.
            if Competition.objects.filter(
                schedule=schedule,
                scheduled_start=start,
            ).exists():
                continue

            create_competition(schedule, start, end)


def close_competition(competition):
    """
    Progress a scheduled competition towards closure.

    - Open/paused competitions move to closing.
    - Closing competitions become closed once all rounds finish.
    - Frozen competitions are left untouched.
    """
    if competition.status in ["open", "paused"]:
        error = competition.start_closing()

        if error:
            raise RuntimeError(f"Failed to start closing competition {competition.pk}: {error}")

        logger.info(
            "Competition %s started closing",
            competition.name,
        )

    if competition.status == "closing":
        competition.try_to_close()

        if competition.status == "closed":
            logger.info(
                "Competition %s closed",
                competition.name,
            )


def process_competition_schedules():
    """
    Process annual competition schedules.
    """
    now = timezone.now()

    # Create competitions whose schedules are active.
    schedule_ids = CompetitionSchedule.objects.filter(
        enabled=True,
    ).values_list("pk", flat=True)

    for schedule_id in schedule_ids:
        try:
            process_schedule(schedule_id, now)
        except Exception:
            logger.exception(
                "Failed processing competition schedule %s",
                schedule_id,
            )

    # Process competitions that need to close.
    competitions = Competition.objects.filter(
        schedule__isnull=False,
    ).filter(
        Q(
            scheduled_end__lte=now,
            status__in=["open", "paused"],
        )
        | Q(status="closing")
    )

    for competition in competitions:
        try:
            close_competition(competition)
        except Exception:
            logger.exception(
                "Failed closing competition %s",
                competition.pk,
            )
