# =============================================================================
#  MedConnect - commandes d'equipe (interface : make)
#
#    make setup    installe tout (idempotent, a relancer quand besoin)
#    make start    demarre backend (:8000) + frontend (:3000)
#    make stop     arrete les deux serveurs (ports 8000/3000 uniquement)
#    make test     lance les tests Django
#    make reset    reinitialise la base de demonstration
#    make seed     (re)importe les donnees de demonstration
#    make health   verifie que les serveurs repondent
#    make logs     affiche la fin des logs
#    make help     liste des commandes (defaut)
#
#  Multiplateforme : Windows, macOS, Linux, WSL.
#  Aucun script shell / PowerShell necessaire : make appelle python directement.
#
#  Installation de make (une fois) :
#      Windows : scoop install make   (ou winget install GnuWin32.Make)
#      macOS   : brew install make
#      Linux   : apt install make / dnf install make / etc.
# =============================================================================

.DEFAULT_GOAL := help

PY ?= python
BROWSER_OPEN ?= 1

.PHONY: help setup start stop test seed reset health logs

help: ## Affiche les commandes disponibles
	@grep -h -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-7s\033[0m %s\n", $$1, $$2}'

setup: ## Installe tout : venv, dependances, base, seed, frontend (idempotent)
	$(PY) setup.py

start: ## Demarre backend (:8000) + frontend (:3000) et ouvre le navigateur
	$(PY) setup.py --start $(if $(filter 0,$(BROWSER_OPEN)),--no-browser,)

stop: ## Arrete les serveurs (backend + frontend)
	$(PY) setup.py --stop

test: ## Lance les tests Django
	$(PY) setup.py --test

seed: ## (Re)importe les donnees de demonstration
	$(PY) setup.py --seed

reset: ## Reinitialise la base de demonstration
	$(PY) setup.py --reset

health: ## Verifie que les serveurs repondent
	$(PY) setup.py --health

logs: ## Affiche la fin des logs des serveurs
	$(PY) setup.py --logs
