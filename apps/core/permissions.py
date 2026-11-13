"""Shared role helpers for the functional modules.

This package is a plain Python helper package: it is intentionally NOT listed
in ``INSTALLED_APPS`` so that no teammate-owned configuration file needs to be
modified. Every module enforces the permission matrix of the Product Backlog
(section 5) on top of Django's ``login_required``.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*roles):
    """Allow only authenticated users whose role is in ``roles``."""

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def can_access_patient_medical_data(user):
    """RG-07 / RG-12: only the doctor reads medical fields."""
    return user.is_authenticated and user.role == user.Role.DOCTOR


def can_access_patient_admin_data(user):
    """Administrative fiches: doctor + secretary only (admin = technical)."""
    return user.is_authenticated and user.role in (
        user.Role.DOCTOR,
        user.Role.SECRETARY,
    )
