from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User


def allowed_recipients(sender):
    queryset = User.objects.exclude(role=User.Role.ADMIN).exclude(pk=sender.pk)
    if sender.role == User.Role.PATIENT:
        queryset = queryset.filter(
            role__in=(User.Role.DOCTOR, User.Role.SECRETARY)
        )
    return queryset


class ComposeForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.none())
    body = forms.CharField(
        label=_("Message"),
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
    )

    def __init__(self, *args, sender=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        queryset = User.objects.none()
        if sender is not None:
            queryset = allowed_recipients(sender)
        self.fields["recipient"].queryset = queryset
        self.fields["recipient"].widget.attrs.setdefault(
            "class", "form-select"
        )

    def clean_recipient(self):
        recipient = self.cleaned_data["recipient"]
        if recipient.role == User.Role.ADMIN:
            raise forms.ValidationError(
                _("The technical administrator cannot receive messages.")
            )
        return recipient
