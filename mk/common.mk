.ONESHELL:
SHELL := /bin/bash
.SHELLFLAGS := -e -u -o pipefail -c
.SILENT:

apostrophe := \'

MAKEFLAGS += --no-print-directory


ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

$(ARGS): ;

#NARGS := $(words $(ARGS))
#
## Разворачиваем ARGS в ARG1, ARG2, ... (чистый GNU Make, без shell)
#__arg_idx :=
#$(foreach a,$(ARGS), \
#  $(eval __arg_idx += x) \
#  $(eval ARG$$(words $$(__arg_idx)) := $(a)) \
#)
#MAKEFLAGS += -s
