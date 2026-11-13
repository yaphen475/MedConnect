from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
def home(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")


@login_required
def dashboard(request):
    return render(
        request,
        "accounts/dashboard.html",
        {"section": "dashboard"},
    )
