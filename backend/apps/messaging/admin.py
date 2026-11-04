from django.contrib import admin

from .models import Message, Thread


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("sujet", "patient", "nb_participants", "modifie_le")

    def nb_participants(self, obj):
        return obj.participants.count()

    nb_participants.short_description = "participants"
    inlines = [MessageInline]
