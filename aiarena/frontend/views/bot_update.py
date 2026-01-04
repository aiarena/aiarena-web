from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.views.generic import UpdateView

from wiki.editors import getEditor

from aiarena.core.models import Bot
from aiarena.core.services import bots


class BotUpdateForm(forms.ModelForm):
    """
    Standard form for updating a bot
    """

    wiki_article_content = forms.CharField(label="Bot page content", required=False, widget=getEditor().get_widget())

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # change the available fields based upon whether the bot_data is available for editing or not
        # and whether there's a current competition
        if bots.bot_data_is_frozen(self.instance):
            self.fields["bot_data"].disabled = True

    def clean_bot_zip(self):
        zip_file = self.cleaned_data["bot_zip"]
        self.instance.validate_bot_zip_file(zip_file)
        return zip_file

    class Meta:
        model = Bot
        fields = [
            "bot_zip",
            "bot_zip_publicly_downloadable",
            "bot_data",
            "bot_data_publicly_downloadable",
            "bot_data_enabled",
        ]


class BotUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    template_name = "bot_edit.html"
    form_class = BotUpdateForm

    redirect_field_name = "next"
    success_message = "Bot saved successfully"

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)

    def get_login_url(self):
        return reverse("login")

    def get_success_url(self):
        return reverse("bot_edit", kwargs={"pk": self.object.pk})

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""

        if form_class is None:
            form_class = self.get_form_class()

        # load the wiki article content as the initial value
        wiki_article_content = self.object.wiki_article.current_revision.content
        kwargs = self.get_form_kwargs()
        kwargs["initial"]["wiki_article_content"] = wiki_article_content
        return form_class(**kwargs)

    def form_valid(self, form):
        """Create a new article revision for the bot wiki page when the form is valid"""
        form.instance.update_bot_wiki_article(
            new_content=form.cleaned_data["wiki_article_content"],
            request=self.request,
        )
        return super().form_valid(form)
