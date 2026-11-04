from django.contrib import admin

from .models import CompteRendu, Ordonnance


@admin.register(CompteRendu)
class CompteRenduAdmin(admin.ModelAdmin):
    list_display = ("patient", "date_consultation", "titre", "medecin")
    search_fields = ("patient__last_name", "patient__first_name", "titre")


@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ("patient", "date_ordonnance", "medecin")
    search_fields = ("patient__last_name", "patient__first_name")
