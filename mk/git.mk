TAG_REGEXP := ^v[0-9]+\.[0-9]+\.[0-9]+$$
GIT_MAIN_BRANCH := master


.PHONY: bump_tag
bump_tag:
	@TAG_PREFIX=$(TAG_PREFIX) BUMP=$(BUMP) PUSH=$(PUSH) DRY_RUN=$(DRY_RUN) scripts/bump_version.sh


.PHONY: _ensure_main_branch
_ensure_main_branch:
	make _check_branch $(GIT_MAIN_BRANCH) && \
	$(call SUCCESS,"Allow prod build$(c) because branches matches") || \
	echo adfsdf


.PHONY: _ensure_clean_worktree
_ensure_clean_worktree:
	git update-index -q --refresh
	git diff --quiet --ignore-submodules -- 2> /dev/null || \
	  $(call ERROR,"There is unstaged changes")
	git diff --cached --quiet --ignore-submodules -- 2> /dev/null || \
	  $(call ERROR,"There is changes in index (staged), not commited")
	test -z "$$(git ls-files --others --exclude-standard)" || \
	  $(call ERROR,"There is untracked-files")
	$(call SUCCESS,"Git ready to push!")


.PHONY: _print_current_prod_tag
_print_current_prod_tag:
	tag=$$(git tag --points-at HEAD | grep -E '$(TAG_REGEXP)' | head -n1)
	[ -n "$$tag" ] || $(call ERROR,"HEAD not marked with tag like vMAJOR.MINOR.PATCH")
	printf '%s\n' "$$tag"


.PHONY: _check_branch
_check_branch:
	@CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD)
	@CHOOSED_BRANCH=$(ARG1)
	@if [ "$$CURRENT_BRANCH" != "$$CHOOSED_BRANCH" ]; then \
		$(call ERROR,"Branches doesnt match") \
	else \
		$(call SUCCESS,"Branches matches$(c) current branch $$CHOOSED_BRANCH") \
	fi

