from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from apps.core.permissions import role_required
from apps.patients.forms import MedicalNotesForm, PatientForm
from apps.patients.models import Patient


DOCTOR = "DOCTOR"
SECRETARY = "SECRETARY"
PATIENT = "PATIENT"


def _own_profile(user):
    return Patient.objects.filter(user=user).first()


@role_required(DOCTOR, SECRETARY, PATIENT)
def patient_list(request):
    """US-03: list restricted by role. Patients are redirected to their own fiche."""
    if request.user.role == PATIENT:
        return redirect("patients:mine")

    patients = Patient.objects.all()
    context = {
        "patients": patients,
        "can_create": True,
        "show_medical": request.user.role == DOCTOR,
        "role_label": request.user.get_role_display(),
    }
    return render(request, "patients/list.html", context)


@role_required(DOCTOR, SECRETARY)
def patient_create(request):
    if request.method == "POST":
        form = PatientForm(request.POST)
        medical_form = MedicalNotesForm(
            request.POST if request.user.role == DOCTOR else None
        )
        if form.is_valid() and (
            request.user.role != DOCTOR or medical_form.is_valid()
        ):
            patient = form.save()
            if request.user.role == DOCTOR and medical_form.is_valid():
                medical_form.save(commit=False)
                Patient.objects.filter(pk=patient.pk).update(
                    medical_notes=medical_form.cleaned_data["medical_notes"]
                )
            messages.success(request, "Patient file created.")
            return redirect("patients:detail", pk=patient.pk)
    else:
        form = PatientForm()
        medical_form = MedicalNotesForm()

    return render(
        request,
        "patients/form.html",
        {
            "form": form,
            "medical_form": medical_form,
            "title": "New patient file",
            "show_medical": request.user.role == DOCTOR,
            "role_label": request.user.get_role_display(),
        },
    )


@role_required(DOCTOR, SECRETARY, PATIENT)
def patient_detail(request, pk):
    if request.user.role == PATIENT:
        profile = _own_profile(request.user)
        if profile is None or profile.pk != pk:
            raise PermissionDenied  # RG-06: own data only
        patient = profile
    else:
        patient = get_object_or_404(Patient, pk=pk)

    context = {
        "patient": patient,
        "show_medical": request.user.role == DOCTOR,
        "can_edit": request.user.role in (DOCTOR, SECRETARY),
        "role_label": request.user.get_role_display(),
    }
    return render(request, "patients/detail.html", context)


@role_required(DOCTOR, SECRETARY, PATIENT)
def patient_mine(request):
    """Convenience route used when a patient opens the module."""
    profile = _own_profile(request.user)
    if profile is not None:
        return redirect("patients:detail", pk=profile.pk)
    messages.warning(
        request, "No patient file is linked to your account yet."
    )
    if request.user.role == PATIENT:
        return redirect("accounts:dashboard")
    return redirect("patients:list")


@role_required(DOCTOR, SECRETARY)
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == "POST":
        form = PatientForm(request.POST, instance=patient)
        medical_form = MedicalNotesForm(
            request.POST if request.user.role == DOCTOR else None,
            instance=patient if request.user.role == DOCTOR else None,
        )
        forms_valid = form.is_valid() and (
            request.user.role != DOCTOR or medical_form.is_valid()
        )
        if forms_valid:
            form.save()
            if request.user.role == DOCTOR and medical_form.is_valid():
                medical_form.save()
            messages.success(request, "Patient file updated.")
            return redirect("patients:detail", pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
        medical_form = (
            MedicalNotesForm(instance=patient)
            if request.user.role == DOCTOR
            else None
        )

    return render(
        request,
        "patients/form.html",
        {
            "form": form,
            "medical_form": medical_form,
            "patient": patient,
            "title": f"Edit {patient}",
            "show_medical": request.user.role == DOCTOR,
            "role_label": request.user.get_role_display(),
        },
    )
