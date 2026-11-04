from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email", "telephone", "cree_le")
    search_fields = ("last_name", "first_name", "email", "telephone")
