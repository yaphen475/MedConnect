from django import forms

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
        self.fields["user"].empty_label = "— No account yet —"


class MedicalNotesForm(forms.ModelForm):
    """US-04 / RG-07: medical fields, doctor only."""

    class Meta:
        model = Patient
        fields = ["medical_notes"]
        widgets = {"medical_notes": forms.Textarea(attrs={"rows": 4})}
