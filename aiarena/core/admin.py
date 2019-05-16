from django.contrib import admin

from .models import *

admin.site.register(User)
admin.site.register(Bot)
admin.site.register(Map)
admin.site.register(Match)
admin.site.register(Participant)
admin.site.register(Result)
