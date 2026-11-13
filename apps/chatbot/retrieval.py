"""Lightweight retrieval for the assistant (US-19 — RAG approach).

``answer(question)`` retrieves the documents that best match the question
(term matching with weights) and builds the answer from their content,
returning the sources used — like a minimal RAG pipeline (retrieve → read),
implemented offline so the demonstration never depends on an API key.
"""

import re
import unicodedata

from apps.chatbot.knowledge import DOCS, FALLBACK, INTRO, REFUSAL

STOPWORDS = {
    "les",
    "une",
    "est",
    "sur",
    "dans",
    "pour",
    "avec",
    "quoi",
    "comment",
    "quel",
    "quelle",
    "quelles",
    "quels",
    "pourquoi",
    "vous",
    "mon",
    "mes",
    "ma",
    "mes",
    "du",
    "de",
    "la",
    "le",
    "un",
    "et",
    "qui",
    "que",
    "quel",
    "au",
    "aux",
    "par",
    "peut",
    "puis",
    "cette",
    "ces",
    "comment",
    # English stopwords (bilingual questions).
    "the",
    "and",
    "for",
    "with",
    "what",
    "when",
    "how",
    "does",
    "you",
    "your",
    "can",
    "from",
    "this",
    "that",
    "are",
    "have",
    "has",
    "not",
    "any",
    "please",
    "tell",
    "about",
}

DIAGNOSIS_TERMS = {
    "diagnostic",
    "diagnostique",
    "diagnostiquer",
    "maladie",
    "maladies",
    "ai-je",
    "suis-je",
    "symptome",
    "symptomes",
    "prescrire",
    "traitement",
    "soigner",
    "guerir",
    # English safety terms (RG-13 applies in every language).
    "diagnosis",
    "diagnose",
    "disease",
    "diseases",
    "symptom",
    "symptoms",
    "treatment",
    "treatments",
    "prescribe",
    "prescribing",
    "cure",
    "heal",
    "healing",
    "am-i",
}


def _tokens(text):
    text = unicodedata.normalize("NFKD", text.lower()).encode(
        "ascii", "ignore"
    ).decode("ascii")
    words = re.findall(r"[a-z0-9]+", text)
    return [w for w in words if len(w) > 2 and w not in STOPWORDS]


def _wants_diagnosis(question):
    tokens = set(_tokens(question)) | {
        w for w in re.findall(r"[a-z0-9-]+", question.lower())
    }
    return any(term in tokens for term in DIAGNOSIS_TERMS)


def score_document(doc, query_tokens):
    """Return (strong_match, score).

    A *strong* match means at least one query term appears in the title or
    the tags of the document: this keeps the retrieval precise (a random word
    found somewhere in a long content must not select an unrelated document).
    """
    title_tokens = set(_tokens(doc["title"]))
    tag_tokens = set(_tokens(" ".join(doc["tags"])))
    content_tokens = _tokens(doc["content"])

    score = 0
    strong = 0
    for token in query_tokens:
        if token in title_tokens:
            score += 3
            strong += 1
        if token in tag_tokens:
            score += 2
            strong += 1
        score += content_tokens.count(token)
    return strong, score


def retrieve(question, limit=3):
    """Return the best matching documents, best first."""
    query_tokens = _tokens(question)
    if not query_tokens:
        return []
    scored = []
    for doc in DOCS:
        strong, score = score_document(doc, query_tokens)
        if strong and score > 0:
            scored.append((score, doc))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _score, doc in scored[:limit]]


def answer(question):
    """Full pipeline: refuse medical intent → retrieve → build the answer.

    The returned strings are plain ``str`` (forced with ``str()``) so the
    history can be stored in the JSON session, and so the answer is frozen in
    the language active when it was produced.
    """
    if _wants_diagnosis(question):
        return {
            "text": str(REFUSAL),
            "sources": [],
            "refused": True,
        }

    documents = retrieve(question)
    if not documents:
        return {"text": str(FALLBACK), "sources": [], "refused": False}

    best = documents[0]
    text = f"{INTRO}\n\n{best['content']}"
    return {
        "text": text,
        "sources": [str(doc["title"]) for doc in documents],
        "refused": False,
    }
