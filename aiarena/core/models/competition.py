import logging

from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from wiki.models import Article, ArticleRevision
from django.core.validators import MinValueValidator

from .bot_race import BotRace
from .game_mode import GameMode
from .mixins import LockableModelMixin

logger = logging.getLogger(__name__)


class CompetitionType(models.TextChoices):
    LEAGUE = u'L', 'League - Round Robin'
    # TOURNAMENT = u'T', 'Tournament'
    # CUSTOM = u'C', 'Custom'
    # flash_challenge = u'F', 'FlashChallenge'


class Competition(models.Model, LockableModelMixin):
    """ Represents a competition of play in the context of a ladder """
    COMPETITION_STATUSES = (
        ('created', 'Created'),  # The initial state for a competition. Functionally identical to paused.
        ('frozen', 'Frozen'),  # While a competition is frozen, no matches are played
        ('paused', 'Paused'),
        # While a competition is paused, existing rounds can be played, but no new ones are generated.
        ('open', 'Open'),  # When a competition is open, new rounds can be generated and played.
        ('closing', 'Closing'),
        # When a competition is closing, it's the same as paused except it will automatically move to closed when all rounds are finished.
        ('closed', 'Closed'),  # Functionally identical to paused, except not intended to change after this status, other than to be finalized.
    )
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=32,
                            choices=CompetitionType.choices,
                            default=CompetitionType.LEAGUE)
    game_mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, related_name='game_modes')
    date_created = models.DateTimeField(auto_now_add=True, blank=True)
    date_opened = models.DateTimeField(blank=True, null=True)
    date_closed = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=16, choices=COMPETITION_STATUSES, default='created', blank=True)
    max_active_rounds = models.IntegerField(default=2, blank=True)
    wiki_article = models.OneToOneField(Article, on_delete=models.PROTECT, blank=True, null=True)
    interest = models.IntegerField(default=0, blank=True)

    # Defines target number of divisions to create when a new cycle begins.
    target_n_divisions = models.IntegerField(default=1, validators=[MinValueValidator(1)], blank=True)
    n_divisions = models.IntegerField(default=1, validators=[MinValueValidator(1)], blank=True)
    # Defines the minimum size of each division, also defines when divisions will split.
    target_division_size = models.IntegerField(default=2, validators=[MinValueValidator(2)], blank=True)
    # Defines the number of rounds between division updates.
    rounds_per_cycle = models.IntegerField(default=1, validators=[MinValueValidator(1)], blank=True)
    # Tracks the number of rounds that have completed this cycle.
    rounds_this_cycle = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    # Defines the number of matches that need to be played before promotions are allowed for a player.
    n_placements = models.IntegerField(default=0, validators=[MinValueValidator(0)], blank=True)
    # List of which bot races are playable in this competition. When left blank, all races are playable.
    playable_races = models.ManyToManyField(BotRace, blank=True)
    require_trusted_infrastructure = models.BooleanField(default=True)
    statistics_finalized = models.BooleanField(default=False)
    """Marks that this competition's statistics have been finalized and therefore cannot be modified."""
    competition_finalized = models.BooleanField(default=False)
    """Marks that this competition has been finalized, and it's round and match data purged."""
    indepth_bot_statistics_enabled = models.BooleanField(default=True)
    """Whether to generate and display indepth bot statistics for this competition."""

    def __str__(self):
        return self.name

    def should_split_divisions(self, n_bots):
        return self.n_divisions < self.target_n_divisions and n_bots >= (self.n_divisions+1)*self.target_division_size

    def should_merge_divisions(self, n_bots):
        return self.n_divisions > 1 and n_bots <= (self.n_divisions-1)*self.target_division_size + self.target_division_size//2

    @property
    def is_paused(self):
        return self.status in ['paused', 'created']

    @property
    def is_open(self):
        return self.status == 'open'

    @property
    def is_closing(self):
        return self.status == 'closing'

    @transaction.atomic
    def freeze(self):
        self.lock_me()
        if self.status in ['open', 'paused']:
            self.status = 'frozen'
            self.save()
            return None
        else:
            return "Cannot freeze a competition with a status of {}".format(self.status)

    @transaction.atomic
    def pause(self):
        self.lock_me()
        if self.status in ['open', 'frozen']:
            self.status = 'paused'
            self.save()
            return None
        else:
            return "Cannot pause a competition with a status of {}".format(self.status)

    @transaction.atomic
    def open(self):
        self.lock_me()

        if self.status in ['created', 'paused', 'frozen']:
            if self.status == 'created':
                self.date_opened = timezone.now()

            self.status = 'open'
            self.save()
            return None
        else:
            return "Cannot open a competition with a status of {}".format(self.status)

    @transaction.atomic
    def start_closing(self):
        self.lock_me()
        if self.is_open or self.is_paused:
            self.status = 'closing'
            self.save()
            return None
        else:
            return "Cannot start closing a competition with a status of {}".format(self.status)

    @transaction.atomic
    def try_to_close(self):
        self.lock_me()
        from .round import Round
        if self.is_closing and Round.objects.filter(competition=self, complete=False).count() == 0:
            self.status = 'closed'
            self.date_closed = timezone.now()
            self.save()

            # deactivate bots in this competition
            from . import CompetitionParticipation  # avoid circular reference
            CompetitionParticipation.objects.filter(competition=self).update(active=False)

    def get_absolute_url(self):
        return reverse('competition', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')

    def get_absolute_url(self):
        return reverse('competition', kwargs={'pk': self.pk})

    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url()}">{escape(self.__str__())}</a>')

    @property
    def is_accepting_new_participants(self):
        return self.status not in ['closing', 'closed']

    def get_wiki_article(self):
        try:
            return self.wiki_article
        except:
            return None

    def create_competition_wiki_article(self):
        article_kwargs = {'owner': None,
                          'group': None,
                          'group_read': True,
                          'group_write': False,
                          'other_read': True,
                          'other_write': False}
        article = Article(**article_kwargs)
        article.add_revision(ArticleRevision(title=self.name), save=True)
        article.save()

        self.wiki_article = article


@receiver(pre_save, sender=Competition)
def pre_save_competition(sender, instance, **kwargs):
    # automatically create a wiki article for this competition if it doesn't exists
    if instance.get_wiki_article() is None:
        instance.create_competition_wiki_article()
