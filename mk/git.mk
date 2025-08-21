.ONESHELL:
SHELL := /bin/bash
SHELLFLAGS := -eu -o pipefail -c

TAG_REGEXP := ^v[0-9]+\.[0-9]+\.[0-9]+$$

GIT_NP := git --no-pager

GIT_MAIN_BRANCH := master


.PHONY: testt
testt:
	test_var=asd
	make error "Есть незакоммиченные (unstaged) изменения"
	echo $$test_var

get_val:
	@echo 123

receive_val:
	@echo $$(make --no-print-directory get_val)

define PRINT_CURRENT_PROD_TAG
	@t=$$(git tag --points-at HEAD | grep -E '$(TAG_REGEXP)' | head -n1); \
	[ -n "$$t" ] || { echo "HEAD not marked with tag like vMAJOR.MINOR.PATCH" >&2; exit 1; }; \
	printf '%s\n' "$$t"
endef



.PHONY: print_current_prod_tag
print_current_prod_tag:
	tag=$$(git tag --points-at HEAD | grep -E '$(TAG_REGEXP)' | head -n1)
	[ -n "$$tag" ] || make error "HEAD not marked with tag like vMAJOR.MINOR.PATCH"
	printf '%s\n' "$$tag"

.PHONY: check_branch
check_branch:
	CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD)
	CHOOSED_BRANCH=$(word 1,$(ARGS))
	if [ "$$CURRENT_BRANCH" != "$$CHOOSED_BRANCH" ]; then \
		make error "Branches doesn't match$(colon) $$CURRENT_BRANCH is not $$CHOOSED_BRANCH!"; \
	else \
		make success Branches matches, current branch $$CHOOSED_BRANCH; \
	fi


.PHONY: ensure_main_branch
ensure_main_branch:
	make check_branch $(GIT_MAIN_BRANCH) && \
	make success Allow prod build, because branches matches || \
	make error Forbid prod build, because branches doesn$(apostrophe)t match!

.PHONY: ensure_clean_worktree
ensure_clean_worktree: ensure_main_branch
	git update-index -q --refresh
	git diff --quiet --ignore-submodules -- 2> /dev/null || \
	  make error "There is unstaged changes"
	git diff --cached --quiet --ignore-submodules -- 2> /dev/null || \
	  make error "There is changes in index (staged), not commited"
	test -z "$$(git ls-files --others --exclude-standard)" || \
	  make error "There is untracked-files"
	make success Git ready to push!








#.PHONY: ensure_clean_worktree
#ensure_clean_worktree: ensure_main_branch
#	git update-index -q --refresh
#	git diff --quiet --ignore-submodules -- 2> /dev/null || \
#	  make error "Есть незакоммиченные (unstaged) изменения"
#	git diff --cached --quiet --ignore-submodules -- 2> /dev/null || { \
#	  echo "Есть изменения в индексе (staged), не закоммиченные" >&2; exit 1; }
#	test -z "$$(git ls-files --others --exclude-standard)" || { \
#	  echo "Есть untracked-файлы" >&2; exit 1; }

.PHONY: bump_tag
bump_tag:
	@TAG_PREFIX=$(TAG_PREFIX) BUMP=$(BUMP) PUSH=$(PUSH) DRY_RUN=$(DRY_RUN) scripts/bump_version.sh