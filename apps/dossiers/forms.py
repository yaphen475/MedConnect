from django import forms
from django.forms import inlineformset_factory

from apps.dossiers.models import MedicalReport, Prescription, PrescriptionItem
from apps.patients.models import Patient


class MedicalReportForm(forms.ModelForm):
    class Meta:
        model = MedicalReport
        fields = ["patient", "consultation_date", "title", "content"]
        widgets = {
            "consultation_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "content": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.all()
        self.fields["patient"].widget.attrs.setdefault("class", "form-select")
        for name in ("consultation_date", "title", "content"):
            self.fields[name].widget.attrs.setdefault("class", "form-control")


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "issued_date", "title", "notes"]
        widgets = {
            "issued_date": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["patient"].queryset = Patient.objects.all()
        self.fields["patient"].widget.attrs.setdefault("class", "form-select")
        for name in ("issued_date", "title", "notes"):
            self.fields[name].widget.attrs.setdefault("class", "form-control")


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ["medication", "dosage", "instructions"]
        widgets = {
            "medication": forms.TextInput(attrs={"class": "form-control"}),
            "dosage": forms.TextInput(attrs={"class": "form-control"}),
            "instructions": forms.TextInput(attrs={"class": "form-control"}),
        }


PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=3,
    can_delete=False,
)
