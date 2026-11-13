from apps.accounts.navigation import ROLE_LABELS, navigation_for


def authenticated_navigation(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "navigation_items": navigation_for(request.user),
        "navigation_role_label": ROLE_LABELS.get(
            request.user.role,
            request.user.role,
        ),
    }
