from django.contrib import admin

from .models import PatientScore, Segment, SegmentAssignment


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = ("nom", "slug", "cree_le")
    prepopulated_fields = {"slug": ("nom",)}


admin.site.register(SegmentAssignment)
admin.site.register(PatientScore)
