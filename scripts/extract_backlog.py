"""Convertit le PDF du backlog MedConnect fourni par l'equipe en docs/BACKLOG.md.

Usage (n'importe ou) :  python scripts/extract_backlog.py
"""
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT.parent / "MedConnect_Product_Backlog.pdf"
CIBLE = ROOT / "docs" / "BACKLOG.md"

HEADER = """\
> Source : `MedConnect_Product_Backlog.pdf` fourni par l'equipe.
> **CECI EST LE BACKLOG DE REFERENCE** pour le developpement (P0 = MVP).
> Matrice de propriete des fichiers + premieres taches : voir CONTRIBUTING.md.

---

"""

reader = pypdf.PdfReader(str(SOURCE))
text = "\n".join((page.extract_text() or "") for page in reader.pages)
CIBLE.parent.mkdir(parents=True, exist_ok=True)
CIBLE.write_text(HEADER + text, encoding="utf-8")
print(f"{CIBLE} ecrit ({len(text)} caracteres, {len(reader.pages)} pages)")
