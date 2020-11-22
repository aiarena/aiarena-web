import logging
import uuid

from constance import config
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.functional import cached_property
from private_storage.fields import PrivateFileField
from wiki.models import Article, ArticleRevision

from aiarena.api.arenaclient.exceptions import NoCurrentSeason
from aiarena.core.storage import OverwritePrivateStorage
from aiarena.core.utils import calculate_md5_django_filefield
from aiarena.core.validators import validate_bot_name, validate_bot_zip_file
from .match import Match
from .mixins import LockableModelMixin
from .season import Season
from .user import User

logger = logging.getLogger(__name__)


def bot_zip_upload_to(instance, filename):
    return '/'.join(['bots', str(instance.id), 'bot_zip'])


def bot_data_upload_to(instance, filename):
    return '/'.join(['bots', str(instance.id), 'bot_data'])


class Bot(models.Model, LockableModelMixin):
    RACES = (
        ('T', 'Terran'),
        ('Z', 'Zerg'),
        ('P', 'Protoss'),
        ('R', 'Random'),
    )
    TYPES = (  # todo: update display names. capitalize etc
        ('cppwin32', 'cppwin32'),
        ('cpplinux', 'cpplinux'),
        ('dotnetcore', 'dotnetcore'),
        ('java', 'java'),
        ('nodejs', 'nodejs'),
        ('python', 'python'),
    )
    BOT_ZIP_LIMIT_MAP = {
        "none": config.BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER,
        "bronze": config.BOT_ZIP_SIZE_LIMIT_IN_MB_BRONZE_TIER,
        "silver": config.BOT_ZIP_SIZE_LIMIT_IN_MB_SILVER_TIER,
        "gold": config.BOT_ZIP_SIZE_LIMIT_IN_MB_GOLD_TIER,
        "platinum": config.BOT_ZIP_SIZE_LIMIT_IN_MB_PLATINUM_TIER,
        "diamond": config.BOT_ZIP_SIZE_LIMIT_IN_MB_DIAMOND_TIER,
    }
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bots')
    name = models.CharField(max_length=50, unique=True, validators=[validate_bot_name, ])
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)  # todo: change this to instead be an enrollment in a ladder?
    bot_zip = PrivateFileField(upload_to=bot_zip_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                               validators=[validate_bot_zip_file, ])
    bot_zip_updated = models.DateTimeField(editable=False)
    bot_zip_md5hash = models.CharField(max_length=32, editable=False)
    bot_zip_publicly_downloadable = models.BooleanField(default=False)
    # todo: set a file size limit which will be checked on result submission
    # and the bot deactivated if the file size exceeds it
    bot_data_enabled = models.BooleanField(default=True)
    """Whether the use of bot data is enabled."""
    bot_data = PrivateFileField(upload_to=bot_data_upload_to, storage=OverwritePrivateStorage(base_url='/'),
                                blank=True, null=True)
    bot_data_md5hash = models.CharField(max_length=32, editable=False, null=True)
    bot_data_publicly_downloadable = models.BooleanField(default=False)
    plays_race = models.CharField(max_length=1, choices=RACES)
    type = models.CharField(max_length=32, choices=TYPES)
    # the ID displayed to other bots during a game so they can recognize their opponent
    game_display_id = models.UUIDField(default=uuid.uuid4)
    wiki_article = models.OneToOneField(Article, on_delete=models.PROTECT, blank=True, null=True)

    @property
    def current_elo_trend(self):
        from .relative_result import RelativeResult
        return (RelativeResult.objects
            .filter(me__bot=self)
            .order_by('-created')[:30]
            .aggregate(Sum('elo_change'))['elo_change__sum'])

    @property
    def current_matches(self):
        return Match.objects.only('id').filter(matchparticipation__bot=self, started__isnull=False, result__isnull=True)

    def is_in_match(self, match_id):
        matches = Match.objects.only('id').filter(matchparticipation__bot=self,
                                                  started__isnull=False,
                                                  result__isnull=True,
                                                  id=match_id
                                                  )
        return matches.count() > 0

    def get_bot_zip_limit_in_mb(self):
        limit = self.BOT_ZIP_LIMIT_MAP[self.user.patreon_level]
        return limit if limit is not None else None

    def regen_game_display_id(self):
        self.game_display_id = uuid.uuid4()

    def get_wiki_article(self):
        try:
            return self.wiki_article
        except:
            return None

    def create_bot_wiki_article(self):
        article_kwargs = {'owner': self.user,
                          'group': None,
                          'group_read': True,
                          'group_write': False,
                          'other_read': True,
                          'other_write': False}
        article = Article(**article_kwargs)
        article.add_revision(ArticleRevision(title=self.name), save=True)
        article.save()

        self.wiki_article = article

    # todo: once multiple ladders comes in, this will need to be updated to 1 bot race per ladder per user.
    def validate_active_bot_race_per_user(self):
        bot_limit = self.user.get_active_bots_per_race_limit()

        # None means no limit
        if bot_limit is not None:
            # if the active bots playing the same race exceeds the allowed count, then back out
            if Bot.objects.filter(user=self.user, active=True, plays_race=self.plays_race).exclude(
                    id=self.id).count() >= bot_limit \
                    and self.active:
                raise ValidationError(
                    'Too many active bots playing that race already exist for this user.'
                    ' You are allowed ' + str(bot_limit) + ' active bot(s) per race.')

    def validate_max_bot_count(self):
        if Bot.objects.filter(user=self.user).exclude(id=self.id).count() >= config.MAX_USER_BOT_COUNT:
            raise ValidationError(
                'Maximum bot count of {0} already reached. No more bots may be added for this user.'.format(
                    config.MAX_USER_BOT_COUNT))

    def clean(self):
        self.validate_max_bot_count()
        self.validate_active_bot_race_per_user()
        self.validate_current_season()

    def __str__(self):
        return self.name

    def bot_data_is_currently_frozen(self):
        # dont alter bot_data while the data is locked in a match, unless there was no bot_data initially
        matches = Match.objects.only('id').filter(matchparticipation__bot=self, started__isnull=False,
                                                  result__isnull=True)
        data_frozen = False
        for match in matches:
            for p in match.matchparticipation_set.filter(bot=self):
                if p.use_bot_data and p.update_bot_data:
                    data_frozen = True  # todo: maybe we can cache this flag
                    break
        return self.bot_data and data_frozen

    @staticmethod
    def get_random_active():
        # todo: apparently this is really slow
        # https://stackoverflow.com/questions/962619/how-to-pull-a-random-record-using-djangos-orm#answer-962672
        return Bot.objects.filter(active=True).order_by('?').first()

    @staticmethod
    def active_count():
        return Bot.objects.filter(active=True).count()

    def get_random_active_excluding_self(self, **kwargs):
        if Bot.active_count() <= 1:
            raise RuntimeError("I am the only bot.")
        return Bot.objects.filter(active=True, **kwargs).exclude(id=self.id).order_by('?').first()

    @cached_property
    def get_absolute_url(self):
        return reverse('bot', kwargs={'pk': self.pk})

    @cached_property
    def as_html_link(self):
        return mark_safe(f'<a href="{self.get_absolute_url}">{escape(self.__str__())}</a>')

    @cached_property
    def as_html_link_with_race(self):
        return mark_safe(f'<a href="{self.get_absolute_url}">{escape(self.__str__())} ({self.plays_race})</a>')

    @cached_property
    def expected_executable_filename(self):
        """
        The expected file name that should be run to start the bot.
        e.g. for a cpp binary bot, this would be Bot.exe
        :return:
        """
        if self.type == 'cppwin32':
            return f'{self.name}.exe'
        elif self.type == 'cpplinux':
            return self.name
        elif self.type == 'dotnetcore':
            return f'{self.name}.dll'
        elif self.type == 'java':
            return f'{self.name}.jar'
        elif self.type == 'nodejs':
            return f'{self.name}.js'
        elif self.type == 'python':
            return 'run.py'

    def current_season_participation(self):
        return self.seasonparticipation_set.get(season=Season.get_current_season())

    def validate_current_season(self):
        if self.active:
            try:
                Season.get_current_season()
            except NoCurrentSeason:
                raise ValidationError('You cannot activate a bot when there is no current season.')

    def can_download_bot_zip(self, user):
        return self.user == user or self.bot_zip_publicly_downloadable or user.is_staff

    def can_download_bot_data(self, user):
        return self.user == user or self.bot_data_publicly_downloadable or user.is_staff

    # for purpose of distinquish news in activity feed
    def get_model_name(self):
        return 'Bot'


_UNSAVED_BOT_ZIP_FILEFIELD = 'unsaved_bot_zip_filefield'
_UNSAVED_BOT_DATA_FILEFIELD = 'unsaved_bot_data_filefield'


# The following methods will temporarily store the bot_zip and bot_data files while we wait for the Bot model to be
# saved in order to generate an ID, which can then be used in the path for the bot_zip name
# This needs to happen because we want to use the model ID in the file path, but until the model is saved, it doesn't
# have an ID.
@receiver(pre_save, sender=Bot)
def pre_save_bot(sender, instance, **kwargs):
    # If the Bot model hasn't been created yet (i.e. it's missing its ID) then set any files aside for the time being
    if not instance.pk and not hasattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD):
        setattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD, instance.bot_zip)
        instance.bot_zip = None
        instance.bot_zip_updated = timezone.now()

    # bot data
    if not instance.pk and not hasattr(instance, _UNSAVED_BOT_DATA_FILEFIELD) and instance.bot_data:
        setattr(instance, _UNSAVED_BOT_DATA_FILEFIELD, instance.bot_data)
        instance.bot_data = None

    # automatically create a wiki article for this bot if it doesn't exists
    if instance.get_wiki_article() is None:
        instance.create_bot_wiki_article()


@receiver(post_save, sender=Bot)
def post_save_bot(sender, instance, created, **kwargs):
    # bot zip
    if created and hasattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD):
        instance.bot_zip = getattr(instance, _UNSAVED_BOT_ZIP_FILEFIELD)
        post_save.disconnect(pre_save_bot, sender=sender)
        instance.save()
        post_save.connect(pre_save_bot, sender=sender)
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_BOT_ZIP_FILEFIELD)

    # bot data
    if created and hasattr(instance, _UNSAVED_BOT_DATA_FILEFIELD):
        instance.bot_data = getattr(instance, _UNSAVED_BOT_DATA_FILEFIELD)
        post_save.disconnect(pre_save_bot, sender=sender)
        instance.save()
        post_save.connect(pre_save_bot, sender=sender)
        # delete the saved instance
        instance.__dict__.pop(_UNSAVED_BOT_DATA_FILEFIELD)

    # Re-calculate the file hashes if required.
    if instance.bot_zip:
        bot_zip_hash = calculate_md5_django_filefield(instance.bot_zip)
        if instance.bot_zip_md5hash != bot_zip_hash:
            instance.bot_zip_md5hash = bot_zip_hash
            instance.bot_zip_updated = timezone.now()
            post_save.disconnect(pre_save_bot, sender=sender)
            instance.save()
            post_save.connect(pre_save_bot, sender=sender)

    if instance.bot_data:
        bot_data_hash = calculate_md5_django_filefield(instance.bot_data)
        if instance.bot_data_md5hash != bot_data_hash:
            instance.bot_data_md5hash = bot_data_hash
            post_save.disconnect(pre_save_bot, sender=sender)
            instance.save()
            post_save.connect(pre_save_bot, sender=sender)
    elif instance.bot_data_md5hash is not None:
        instance.bot_data_md5hash = None
        post_save.disconnect(pre_save_bot, sender=sender)
        instance.save()
        post_save.connect(pre_save_bot, sender=sender)

    # register a season participation if the bot has been activated
    if instance.active and instance.seasonparticipation_set.filter(season=Season.get_current_season()).count() == 0:
        from .season_participation import SeasonParticipation
        SeasonParticipation.objects.create(season=Season.get_current_season(), bot=instance)
