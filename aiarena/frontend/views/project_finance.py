from django.http import Http404
from django.shortcuts import redirect

from constance import config


def project_finance(request):
    if config.PROJECT_FINANCE_LINK is not None and config.PROJECT_FINANCE_LINK:
        # if the link is configured, redirect.
        return redirect(to=config.PROJECT_FINANCE_LINK)
    else:
        raise Http404()
