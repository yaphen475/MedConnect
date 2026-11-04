from django.contrib import admin

from .models import Consentement, DemandeDonnee, JournalAcces, RegleRetention


admin.site.register(Consentement)
admin.site.register(DemandeDonnee)
admin.site.register(JournalAcces)
admin.site.register(RegleRetention)
