from django import forms
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, FormView
from django.views.generic.detail import SingleObjectMixin

from aiarena.core.models import Match, MatchTag, Tag
from aiarena.core.utils import parse_tags


class MatchDisplay(DetailView):
    model = Match
    template_name = "match.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            tags = self.object.tags.filter(user=self.request.user).all()
            context["match_tag_form"] = MatchTagForm(initial={"tags": ",".join(str(mtag.tag) for mtag in tags)})
            others_tags = self.object.tags.exclude(user=self.request.user).all()
        else:
            others_tags = self.object.tags.all()

        others_tags_dict = {}
        for mt in others_tags:
            if mt.user.as_html_link not in others_tags_dict:
                others_tags_dict[mt.user.as_html_link] = str(mt.tag)
            else:
                others_tags_dict[mt.user.as_html_link] += ", " + str(mt.tag)
        context["others_tags_dict"] = others_tags_dict
        return context


class MatchDetail(View):
    def get(self, request, *args, **kwargs):
        view = MatchDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = MatchTagFormView.as_view()
        return view(request, *args, **kwargs)


class MatchTagForm(forms.Form):
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={"data-role": "tagsinput"}))

    def clean_tags(self):
        return parse_tags(self.cleaned_data["tags"])


class MatchTagFormView(SingleObjectMixin, FormView):
    model = Match
    template_name = "match.html"
    form_class = MatchTagForm

    def get_success_url(self):
        return reverse("match", kwargs={"pk": self.kwargs["pk"]})

    def post(self, request, *args, **kwargs):
        form = MatchTagForm(request.POST)
        if request.user.is_authenticated and form.is_valid():
            match = self.get_object()
            match_tags = []
            for tag in form.cleaned_data["tags"]:
                tag_obj = Tag.objects.get_or_create(name=tag)
                match_tags.append(MatchTag.objects.get_or_create(tag=tag_obj[0], user=request.user)[0])

            # remove tags for this match that belong to this user and were not sent in the form
            match.tags.remove(*match.tags.filter(user=request.user).exclude(id__in=[mt.id for mt in match_tags]))
            # add everything, this shouldn't cause duplicates
            match.tags.add(*match_tags)

        return super().post(request, *args, **kwargs)
