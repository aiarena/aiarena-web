import logging
import uuid
from zipfile import BadZipFile, ZipFile

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property

from constance import config
from private_storage.fields import PrivateFileField
from wiki.models import Article, ArticleRevision

from aiarena.core.utils import calculate_md5_django_filefield
from aiarena.core.validators import validate_bot_name

from .bot_race import BotRace
from .match import Match
from .mixins import LockableModelMixin
from .user import User


logger = logging.getLogger(__name__)


def bot_zip_upload_to(instance, filename):
    return "/".join(["bots", str(instance.id), "bot_zip"])


def bot_data_upload_to(instance, filename):
    return "/".join(["bots", str(instance.id), "bot_data"])


class Bot(models.Model, LockableModelMixin):
    RACES = (
        ("T", "Terran"),
        ("Z", "Zerg"),
        ("P", "Protoss"),
        ("R", "Random"),
    )
    TYPES = (  # todo: update display names. capitalize etc
        # cppwin32 is a legacy option that we no longer actively support, but it's existance in types is still required
        ("cppwin32", "cppwin32"),
        ("cpplinux", "cpplinux"),
        ("dotnetcore", "dotnetcore"),
        ("java", "java"),
        ("nodejs", "nodejs"),
        ("python", "python"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bots")
    name = models.CharField(
        max_length=50,
        unique=True,
        validators=[
            validate_bot_name,
        ],
    )
    created = models.DateTimeField(auto_now_add=True)
    bot_zip = PrivateFileField(upload_to=bot_zip_upload_to)
    bot_zip_updated = models.DateTimeField(editable=False)
    bot_zip_md5hash = models.CharField(max_length=32, editable=False)
    bot_zip_publicly_downloadable = models.BooleanField(default=False)
    # todo: set a file size limit which will be checked on result submission
    # and the bot deactivated if the file size exceeds it
    bot_data_enabled = models.BooleanField(default=True)
    """Whether the use of bot data is enabled."""
    bot_data = PrivateFileField(upload_to=bot_data_upload_to, blank=True, null=True)
    bot_data_md5hash = models.CharField(max_length=32, editable=False, null=True)
    bot_data_publicly_downloadable = models.BooleanField(default=False)
    plays_race = models.ForeignKey(BotRace, on_delete=models.PROTECT)
    type = models.CharField(max_length=32, choices=TYPES)
    # the ID displayed to other bots during a game so they can recognize their opponent
    game_display_id = models.UUIDField(default=uuid.uuid4)
    wiki_article = models.OneToOneField(Article, on_delete=models.PROTECT, blank=True, null=True)

    def current_elo_trend(self, competition, n_matches):
        from .relative_result import RelativeResult

        return (
            RelativeResult.objects.filter(
                me__bot=self, match__requested_by__isnull=True, match__round__competition=competition
            )
            .order_by("-started")[:n_matches]
            .aggregate(Sum("elo_change"))["elo_change__sum"]
        )

    def is_in_match(self, match_id):
        matches = Match.objects.only("id").filter(
            matchparticipation__bot=self, started__isnull=False, result__isnull=True, id=match_id
        )
        return matches.count() > 0

    def get_bot_zip_limit_in_mb(self):
        limit = {
            "none": config.BOT_ZIP_SIZE_LIMIT_IN_MB_FREE_TIER,
            "bronze": config.BOT_ZIP_SIZE_LIMIT_IN_MB_BRONZE_TIER,
            "silver": config.BOT_ZIP_SIZE_LIMIT_IN_MB_SILVER_TIER,
            "gold": config.BOT_ZIP_SIZE_LIMIT_IN_MB_GOLD_TIER,
            "platinum": config.BOT_ZIP_SIZE_LIMIT_IN_MB_PLATINUM_TIER,
            "diamond": config.BOT_ZIP_SIZE_LIMIT_IN_MB_DIAMOND_TIER,
        }[self.user.patreon_level]
        return limit if limit is not None else None

    def get_wiki_article(self):
        try:
            return self.wiki_article
        except Exception:
            return None

    def create_bot_wiki_article(self):
        article_kwargs = {
            "owner": self.user,
            "group": None,
            "group_read": True,
            "group_write": False,
            "other_read": True,
            "other_write": False,
        }
        article = Article(**article_kwargs)
        article.add_revision(ArticleRevision(title=self.name), save=True)
        article.save()

        self.wiki_article = article

    def update_bot_wiki_article(self, new_content, request):
        if self.wiki_article.current_revision.content == new_content:
            return

        # If the article content is different, add a new revision
        revision = ArticleRevision()
        revision.inherit_predecessor(self.wiki_article)
        revision.title = self.name
        revision.content = new_content
        revision.deleted = False
        revision.set_from_request(request)
        self.wiki_article.add_revision(revision)

    def validate_max_bot_count(self):
        if Bot.objects.filter(user=self.user).exclude(id=self.id).count() >= config.MAX_USER_BOT_COUNT:
            raise ValidationError(
                f"Maximum bot count of {config.MAX_USER_BOT_COUNT} already reached. "
                "No more bots may be added for this user."
            )

    def validate_bot_zip_file(self, value):
        limit = self.get_bot_zip_limit_in_mb()
        if value.size > limit * 1024 * 1024:  # convert limit to bytes
            raise ValidationError(
                f"File too large. Size should not exceed {limit} MB. "
                f"You can donate to the ladder to increase this limit."
            )

        try:
            with ZipFile(value.open()) as zip_file:
                expected_name = self.expected_executable_filename
                if expected_name not in zip_file.namelist():
                    raise ValidationError(
                        f"Incorrect bot zip file structure. A bot of type {self.type} "
                        f"would need to have a file in the zip file root named {expected_name}"
                    )
        except BadZipFile:
            raise ValidationError("Bot zip must be a valid zip file")

    def clean(self):
        self.validate_max_bot_count()
        self.validate_bot_zip_file(self.bot_zip)

    def __str__(self):
        return self.name

    def get_random_excluding_self(self):
        if Bot.objects.all().count() <= 1:
            raise RuntimeError("I am the only bot.")
        return Bot.objects.exclude(id=self.id).order_by("?").first()

    @cached_property
    def expected_executable_filename(self):
        """
        The expected file name that should be run to start the bot.
        e.g. for a cpp binary bot, this would be Bot.exe
        :return:
        """
        if self.type == "cppwin32":
            return f"{self.name}.exe"
        elif self.type == "cpplinux":
            return self.name
        elif self.type == "dotnetcore":
            return f"{self.name}.dll"
        elif self.type == "java":
            return f"{self.name}.jar"
        elif self.type == "nodejs":
            return f"{self.name}.js"
        elif self.type == "python":
            return "run.py"

    def can_download_bot_zip(self, user):
        """
        Only allow download of bot_zip if any of:
        - This user owns the bot
        - The bot_zip is publicly downloadable
        - This user is a staff user
        - This user is a trusted arenaclient
        """
        return (
            self.user.id == user.id
            or self.bot_zip_publicly_downloadable
            or user.is_staff
            or (user.is_arenaclient and user.arenaclient.trusted)
        )

    def can_download_bot_data(self, user):
        """
        Only allow download of bot_data if any of:
        - This user owns the bot
        - The bot_data is publicly downloadable
        - This user is a staff user
        - This user is a trusted arenaclient
        """
        return (
            self.user.id == user.id
            or self.bot_data_publicly_downloadable
            or user.is_staff
            or (user.is_arenaclient and user.arenaclient.trusted)
        )

    # for purpose of distinquish news in activity feed
    def get_model_name(self):
        return "Bot"


_UNSAVED_BOT_ZIP_FILEFIELD = "unsaved_bot_zip_filefield"
_UNSAVED_BOT_DATA_FILEFIELD = "unsaved_bot_data_filefield"


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
