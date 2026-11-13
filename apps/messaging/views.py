from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_POST

from apps.accounts.models import User
from apps.core.permissions import role_required
from apps.core.sse import streaming_response
from apps.messaging.forms import ComposeForm, allowed_recipients
from apps.messaging.models import Conversation, Message

DOCTOR = "DOCTOR"
SECRETARY = "SECRETARY"
PATIENT = "PATIENT"
STAFF_ROLES = (DOCTOR, SECRETARY, PATIENT)


@role_required(*STAFF_ROLES)
def inbox(request):
    """US-16: only the conversations of the logged-in user."""
    conversations = request.user.conversations.prefetch_related(
        "participants", "messages"
    )
    items = [
        {
            "conversation": conversation,
            "others": conversation.other_participants(request.user),
            "last": conversation.last_message,
        }
        for conversation in conversations
    ]
    context = {"conversations": items, "section": "messaging"}
    return render(request, "messaging/inbox.html", context)


@role_required(*STAFF_ROLES)
def thread(request, pk):
    """US-15 / US-16 / US-17: participants only (RG-11)."""
    conversation = get_object_or_404(Conversation, pk=pk)
    if not conversation.is_participant(request.user):
        # RG-11: no access to a conversation you do not belong to.
        raise PermissionDenied

    if request.method == "POST":
        body = request.POST.get("body", "").strip()
        if body:
            Message.objects.create(
                conversation=conversation, sender=request.user, body=body
            )
            conversation.save(update_fields=["updated_at"])
            return redirect("messaging:thread", pk=conversation.pk)
        messages.error(request, _("The message cannot be empty."))

    # Mark the messages received as read.
    Message.objects.filter(
        conversation=conversation,
        read_at__isnull=True,
    ).exclude(sender=request.user).update(read_at=timezone.now())

    conversation_messages = conversation.messages.select_related("sender")
    last_message_id = (
        conversation.messages.order_by("-pk").values_list("pk", flat=True).first()
        or 0
    )
    context = {
        "conversation": conversation,
        "messages_list": conversation_messages,
        "last_message_id": last_message_id,
        "other_participants": conversation.other_participants(request.user),
        "section": "messaging",
    }
    return render(request, "messaging/thread.html", context)


@role_required(*STAFF_ROLES)
@require_GET
def thread_events(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if not conversation.is_participant(request.user):
        raise PermissionDenied

    raw_cursor = (
        request.headers.get("Last-Event-ID")
        or request.GET.get("after")
        or "0"
    )
    try:
        cursor = int(raw_cursor)
        if cursor < 0:
            raise ValueError
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Invalid message cursor.")

    def poll_messages():
        nonlocal cursor
        new_messages = list(
            conversation.messages.filter(pk__gt=cursor)
            .select_related("sender")
            .order_by("pk")[:100]
        )
        if not new_messages:
            return []

        message_ids = [message.pk for message in new_messages]
        Message.objects.filter(
            pk__in=message_ids,
            read_at__isnull=True,
        ).exclude(sender=request.user).update(read_at=timezone.now())

        events = []
        for message in new_messages:
            cursor = message.pk
            events.append(
                (
                    {
                        "id": message.pk,
                        "sender_id": message.sender_id,
                        "sender": message.sender.username,
                        "sent_at": timezone.localtime(message.sent_at).strftime(
                            "%d/%m/%Y %H:%M"
                        ),
                        "body": message.body,
                    },
                    "message",
                    message.pk,
                )
            )
        return events

    return streaming_response(poll_messages)


@role_required(*STAFF_ROLES)
def compose(request):
    """US-15: pick an authorised recipient and send a first message."""
    if request.method == "POST":
        form = ComposeForm(request.POST, sender=request.user)
        if form.is_valid():
            conversation, _created = Conversation.direct(
                request.user, form.cleaned_data["recipient"]
            )
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                body=form.cleaned_data["body"],
            )
            conversation.save(update_fields=["updated_at"])
            messages.success(request, _("Message sent."))
            return redirect("messaging:thread", pk=conversation.pk)
    else:
        form = ComposeForm(sender=request.user)
    return render(
        request,
        "messaging/compose.html",
        {"form": form, "section": "messaging"},
    )


@role_required(*STAFF_ROLES)
@require_POST
def start_with(request, pk):
    """Shortcut: open (or create) the conversation with this user."""
    other = get_object_or_404(User, pk=pk)
    if not allowed_recipients(request.user).filter(pk=other.pk).exists():
        raise PermissionDenied
    conversation, _created = Conversation.direct(request.user, other)
    return redirect("messaging:thread", pk=conversation.pk)
