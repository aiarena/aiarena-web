from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append a group for "Administration" & "Applications"
        self.children.append(
            modules.Group(
                _("Group: Administration & Applications"),
                column=1,
                collapsible=True,
                children=[
                    modules.AppList(
                        _("Administration"),
                        column=1,
                        collapsible=False,
                        models=("django.contrib.*",),
                    ),

                ],
            )
        )
        self.children.append(
            modules.Group(
                _("Group: Administration & Applications"),
                column=2,
                collapsible=True,
                children=[
                    modules.AppList(
                        _("Applications"),
                        column=1,
                        css_classes=("collapse closed",),
                        exclude=("django.contrib.*",),
                    ),
                ],
            )
        )
        self.children.append(modules.RecentActions(
            title='Recent actions',
            column=3,
            limit=5,
        ))

