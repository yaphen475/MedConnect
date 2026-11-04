from django.contrib import admin

from .models import Appointment, AvailabilitySlot, Block


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("patient", "debut", "motif", "statut", "rappel_envoye")
    list_filter = ("statut",)
    search_fields = ("patient__last_name", "patient__first_name", "motif")


admin.site.register(AvailabilitySlot)
admin.site.register(Block)
