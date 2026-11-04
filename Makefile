# ==============================================================
#  MedConnect - commandes d'equipe (interface : make)
#
#    make setup    installe tout (idempotent, a relancer quand besoin)
#    make start    demarre backend (:8000) + frontend (:3000)
#    make stop     arrete les deux serveurs
#    make test     lance les tests Django
#    make reset    reinitialise la base de demonstration
#    make help     liste des commandes (defaut)
#
#  Windows : Git for Windows (fournit le sh) + make
#            installation : scoop install make
#  Sans make : .\setup.cmd  puis  .\dev.cmd   (meme etapes, sans make)
# ==============================================================

.DEFAULT_GOAL := help

# --- Windows : make a besoin d'un sh -> on prend celui de Git ---
ifeq ($(OS),Windows_NT)
WINDOWS_SH := $(firstword \
	$(wildcard C:/PROGRA~1/Git/bin/sh.exe) \
	$(wildcard C:/PROGRA~1/Git/usr/bin/sh.exe) \
	$(wildcard C:/PROGRA~2/Git/bin/sh.exe) \
	$(wildcard C:/PROGRA~2/Git/usr/bin/sh.exe))
ifeq ($(WINDOWS_SH),)
$(error Aucun sh.exe trouve. Installez Git for Windows (https://git-scm.com), ou utilisez .\setup.cmd sans make)
endif
SHELL := $(WINDOWS_SH)
SH := "$(WINDOWS_SH)"
else
SH := bash
endif

# BROWSER_OPEN=0 : ne pas ouvrir le navigateur avec "make start"
BROWSER_OPEN ?= 1

.PHONY: help setup start stop test seed reset health logs

help: ## Affiche les commandes disponibles
	@grep -h -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-7s\033[0m %s\n", $$1, $$2}'

setup: ## Installe tout : venv, dependances, base, seed, frontend
	@$(SH) setup.sh

start: ## Demarre backend (:8000) + frontend (:3000) et ouvre le navigateur
	@OPEN=$(BROWSER_OPEN) $(SH) setup.sh --start

stop: ## Arrete les serveurs (backend + frontend)
	@$(SH) setup.sh --stop

test: ## Lance les tests Django
	@$(SH) setup.sh --test

seed: ## (Re)importe les donnees de demonstration
	@$(SH) setup.sh --seed

reset: ## Reinitialise la base de demonstration
	@$(SH) setup.sh --reset

health: ## Verifie que les serveurs repondent
	@curl -fsS http://127.0.0.1:8000/api/health/; echo; \
	curl -fsS -o /dev/null -w "frontend : HTTP %{http_code}\n" http://127.0.0.1:3000/

logs: ## Affiche la fin des logs des serveurs
	@tail -n 30 .backend.log .frontend.log 2>/dev/null || true
