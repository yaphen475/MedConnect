from django.contrib import admin

from .models import Conversation, Document, MessageChat


admin.site.register(Document)
admin.site.register(Conversation)
admin.site.register(MessageChat)
