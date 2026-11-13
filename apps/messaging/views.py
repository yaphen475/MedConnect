from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.core.permissions import role_required
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
    context = {
        "conversation": conversation,
        "messages_list": conversation_messages,
        "other_participants": conversation.other_participants(request.user),
        "section": "messaging",
    }
    return render(request, "messaging/thread.html", context)


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
