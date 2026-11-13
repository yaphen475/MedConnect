from django import forms

from apps.accounts.models import User


class ComposeForm(forms.Form):
    recipient = forms.ModelChoiceField(queryset=User.objects.none())
    body = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
    )

    def __init__(self, *args, sender=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        queryset = User.objects.exclude(role=User.Role.ADMIN)
        if sender is not None:
            queryset = queryset.exclude(pk=sender.pk)
            if sender.role == User.Role.PATIENT:
                # A patient writes to the doctor or the secretary only.
                queryset = queryset.filter(
                    role__in=(User.Role.DOCTOR, User.Role.SECRETARY)
                )
        self.fields["recipient"].queryset = queryset
        self.fields["recipient"].widget.attrs.setdefault(
            "class", "form-select"
        )

    def clean_recipient(self):
        recipient = self.cleaned_data["recipient"]
        if recipient.role == User.Role.ADMIN:
            raise forms.ValidationError(
                "The technical administrator cannot receive messages (RG-12)."
            )
        return recipient
