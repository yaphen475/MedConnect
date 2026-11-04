"""Journalisation des acces - PROPRIETAIRE : Ahmed (US-36).

Ne logge que les utilisateurs connectes, hors fichiers statiques.
Silencieux si la table n'existe pas encore (avant les migrations).
"""
from .models import JournalAcces

EXCLUDED_PREFIXES = ("/static/", "/media/", "/admin/jsi18n")
EXCLUDED_SUBSTRINGS = ("/api/rgpd/journal",)


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            user = getattr(request, "user", None)
            if user is None or not user.is_authenticated:
                return response
            path = request.path
            if path.startswith(EXCLUDED_PREFIXES) or any(s in path for s in EXCLUDED_SUBSTRINGS):
                return response
            JournalAcces.objects.create(
                utilisateur=user,
                action=request.method,
                chemin=path,
                adresse_ip=_client_ip(request),
            )
        except Exception:
            pass
        return response
