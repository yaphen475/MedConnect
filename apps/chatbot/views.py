from django.contrib import messages
from django.shortcuts import render
from django.utils.translation import gettext, gettext_lazy
from django.views.decorators.http import require_POST

from apps.chatbot import retrieval
from apps.core.permissions import role_required

HISTORY_KEY = "chatbot_history"
MAX_HISTORY = 20

EXAMPLES = [
    gettext_lazy("Quels sont les horaires d'ouverture du cabinet ?"),
    gettext_lazy("Comment demander un rendez-vous ?"),
    gettext_lazy("Comment retrouver mes ordonnances ?"),
    gettext_lazy("Comment contacter la secretaire ?"),
]


@role_required("DOCTOR", "SECRETARY", "PATIENT", "ADMIN")
def chat(request):
    """US-19: assistant on the documentary base, for every profile."""
    history = request.session.get(HISTORY_KEY, [])

    if request.method == "POST":
        question = request.POST.get("question", "").strip()
        if question:
            result = retrieval.answer(question)
            history.append(
                {
                    "question": question,
                    "answer": result["text"],
                    "sources": result["sources"],
                    "refused": result["refused"],
                }
            )
            request.session[HISTORY_KEY] = history[-MAX_HISTORY:]
        else:
            messages.warning(request, gettext("Please type a question."))
        return render(
            request,
            "chatbot/chat.html",
            _context(request, history),
        )

    return render(request, "chatbot/chat.html", _context(request, history))


def _context(request, history):
    return {
        "history": history,
        "examples": EXAMPLES,
        "section": "chatbot",
    }


@role_required("DOCTOR", "SECRETARY", "PATIENT", "ADMIN")
@require_POST
def clear(request):
    request.session.pop(HISTORY_KEY, None)
    return render(
        request, "chatbot/chat.html", _context(request, [])
    )
