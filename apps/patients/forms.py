from django import forms
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User
from apps.patients.models import Patient


class PatientForm(forms.ModelForm):
    """Administrative fields only: medical notes are a separate doctor-only form."""

    class Meta:
        model = Patient
        fields = [
            "user",
            "first_name",
            "last_name",
            "birth_date",
            "phone",
            "email",
            "address",
            "social_security_number",
            "administrative_notes",
        ]
        widgets = {
            "birth_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "administrative_notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = "form-select" if name == "user" else "form-control"
            field.widget.attrs.setdefault("class", css)
        self.fields["user"].queryset = User.objects.filter(
            role=User.Role.PATIENT
        )
        self.fields["user"].required = False
        self.fields["user"].empty_label = _("— No account yet —")
        self.fields["user"].label = _("Account")
        self.fields["first_name"].label = _("First name")
        self.fields["last_name"].label = _("Last name")
        self.fields["birth_date"].label = _("Birth date")
        self.fields["phone"].label = _("Phone")
        self.fields["email"].label = _("Email")
        self.fields["address"].label = _("Address")
        self.fields["social_security_number"].label = _(
            "Social security number"
        )
        self.fields["administrative_notes"].label = _(
            "Administrative notes"
        )


class MedicalNotesForm(forms.ModelForm):
    """US-04 / RG-07: medical fields, doctor only."""

    class Meta:
        model = Patient
        fields = ["medical_notes"]
        widgets = {"medical_notes": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["medical_notes"].label = _("Medical notes")
