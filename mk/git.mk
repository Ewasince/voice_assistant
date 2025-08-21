TAG_REGEXP := ^v[0-9]+\.[0-9]+\.[0-9]+$$
GIT_MAIN_BRANCH := master


.PHONY: bump_tag
bump_tag:
	@TAG_PREFIX=$(TAG_PREFIX) BUMP=$(BUMP) PUSH=$(PUSH) DRY_RUN=$(DRY_RUN) scripts/bump_version.sh


.PHONY: _ensure_main_branch
_ensure_main_branch:
	make _check_branch $(GIT_MAIN_BRANCH) && \
	make success Allow prod build, because branches matches || \
	make error Forbid prod build, because branches doesn$(apostrophe)t match!


.PHONY: _ensure_clean_worktree
_ensure_clean_worktree:
	git update-index -q --refresh
	git diff --quiet --ignore-submodules -- 2> /dev/null || \
	  make error "There is unstaged changes"
	git diff --cached --quiet --ignore-submodules -- 2> /dev/null || \
	  make error "There is changes in index (staged), not commited"
	test -z "$$(git ls-files --others --exclude-standard)" || \
	  make error "There is untracked-files"
	make success Git ready to push!


.PHONY: _print_current_prod_tag
_print_current_prod_tag:
	tag=$$(git tag --points-at HEAD | grep -E '$(TAG_REGEXP)' | head -n1)
	[ -n "$$tag" ] || make error "HEAD not marked with tag like vMAJOR.MINOR.PATCH"
	printf '%s\n' "$$tag"

.PHONY: _check_branch
_check_branch:
	CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD)
	CHOOSED_BRANCH=$(ARG1)
	if [ "$$CURRENT_BRANCH" != "$$CHOOSED_BRANCH" ]; then \
		make error "Branches doesn't match$(colon) $$CURRENT_BRANCH is not $$CHOOSED_BRANCH!"; \
	else \
		make success Branches matches, current branch $$CHOOSED_BRANCH; \
	fi
