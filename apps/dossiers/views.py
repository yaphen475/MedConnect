from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from apps.core.permissions import role_required
from apps.dossiers.forms import (
    MedicalReportForm,
    PrescriptionForm,
    PrescriptionItemFormSet,
)
from apps.dossiers.models import MedicalReport, Prescription
from apps.patients.models import Patient

DOCTOR = "DOCTOR"
PATIENT = "PATIENT"
SECRETARY = "SECRETARY"
ADMIN = "ADMIN"


@role_required(DOCTOR, PATIENT)
def reports(request):
    """US-11 / US-12: doctor reads everything, patient only his own history."""
    is_doctor = request.user.role == DOCTOR
    queryset = MedicalReport.objects.select_related("patient", "author")
    if not is_doctor:
        queryset = queryset.filter(patient__user=request.user)
    context = {
        "reports": queryset,
        "is_doctor": is_doctor,
        "section": "records",
    }
    return render(request, "dossiers/reports.html", context)


@role_required(DOCTOR)
def patient_history(request, patient_id):
    """US-12: chronological medical history, doctor only (RG-07)."""
    patient = get_object_or_404(Patient, pk=patient_id)
    reports = patient.medical_reports.order_by(
        "consultation_date", "created_at"
    )
    prescriptions = patient.prescriptions.all()
    context = {
        "patient": patient,
        "reports": reports,
        "prescriptions": prescriptions,
        "section": "records",
    }
    return render(request, "dossiers/history.html", context)


@role_required(DOCTOR)
def report_new(request):
    """US-11: the doctor writes a compte rendu linked to the right patient."""
    if request.method == "POST":
        form = MedicalReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.author = request.user
            report.save()
            messages.success(request, _("Medical report saved."))
            return redirect(
                "dossiers:patient_history", patient_id=report.patient_id
            )
    else:
        form = MedicalReportForm(
            initial={"consultation_date": timezone.localdate()}
        )
    return render(
        request,
        "dossiers/report_form.html",
        {"form": form, "title": _("New medical report"), "section": "records"},
    )


@role_required(DOCTOR, PATIENT)
def prescriptions(request):
    """US-13 / US-14: patient sees his own prescriptions only (RG-06)."""
    is_doctor = request.user.role == DOCTOR
    queryset = Prescription.objects.prefetch_related("items").select_related(
        "patient", "author"
    )
    if not is_doctor:
        queryset = queryset.filter(patient__user=request.user)
    context = {
        "prescriptions": queryset,
        "is_doctor": is_doctor,
        "section": "prescriptions",
    }
    return render(request, "dossiers/prescription_list.html", context)


@role_required(DOCTOR)
def prescription_new(request):
    """US-13: demonstration prescription, doctor only (RG-09)."""
    if request.method == "POST":
        form = PrescriptionForm(request.POST)
        formset = PrescriptionItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            filled_lines = [
                data
                for data in formset.cleaned_data
                if data and data.get("medication")
            ]
            if not filled_lines:
                messages.error(
                    request, _("Add at least one medication line.")
                )
            else:
                with transaction.atomic():
                    prescription = form.save(commit=False)
                    prescription.author = request.user
                    prescription.save()
                    formset.instance = prescription
                    formset.save()
                messages.success(request, _("Prescription saved."))
                return redirect("dossiers:prescriptions")
    else:
        form = PrescriptionForm(
            initial={"issued_date": timezone.localdate()}
        )
        formset = PrescriptionItemFormSet()
    return render(
        request,
        "dossiers/prescription_form.html",
        {
            "form": form,
            "formset": formset,
            "title": _("New prescription"),
            "section": "prescriptions",
        },
    )


@role_required(DOCTOR)
@require_POST
def report_delete(request, pk):
    """Small helper so the doctor can remove a report written by mistake."""
    report = get_object_or_404(MedicalReport, pk=pk)
    patient_id = report.patient_id
    report.delete()
    messages.info(request, _("Medical report deleted."))
    return redirect("dossiers:patient_history", patient_id=patient_id)
