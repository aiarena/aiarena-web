import logging

from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from wiki.models import Article, ArticleRevision

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
        ('closed', 'Closed'),  # Functionally identical to paused, except not intended to change after this status.
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

    def __str__(self):
        return self.name

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
        from .round import Round
        if self.is_closing and Round.objects.filter(competition=self, complete=False).count() == 0:
            Competition.objects.filter(id=self.id, status='closing').update(status='closed', date_closed=timezone.now())

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
