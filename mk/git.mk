TAG_REGEXP := ^v[0-9]+\.[0-9]+\.[0-9]+$$
GIT_MAIN_BRANCH := master


VERSION_PYFILE := voice_assistant/__init__.py

.PHONY: bump_tag
bump_tag:
	TAG=$$(scripts/bump_version.sh $(ARG1) --dry-run)
	sed -i "s/^__version__ = \".*\"/__version__ = \"$$TAG\"/" $(VERSION_PYFILE)
	git add $(VERSION_PYFILE)
	COMMIT_MESSAGE="Release $$TAG"
	git commit -m "$$COMMIT_MESSAGE" --no-verify
	git tag -a "$$TAG" -m "$$COMMIT_MESSAGE"
	$(call SUCCESS,"Released new tag $$TAG")


.PHONY: _ensure_main_branch
_ensure_main_branch:
	make _check_branch $(GIT_MAIN_BRANCH) && \
	$(call SUCCESS,"Allow prod build, because branches matches") || \
	$(call ERROR,"Forbid prod build because branches doesn't match!")


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
	tag=$$(git tag --points-at HEAD | grep -E '$(TAG_REGEXP)' | tail -n1)
	[ -n "$$tag" ] || $(call ERROR,"HEAD not marked with tag like vMAJOR.MINOR.PATCH")
	printf '%s\n' "$$tag"


.PHONY: _check_branch
_check_branch:
	CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD)
	CHOOSED_BRANCH=$(ARG1)
	if [ "$$CURRENT_BRANCH" != "$$CHOOSED_BRANCH" ]; then \
		$(call ERROR,"Branches doesnt match"); \
	else \
		$(call SUCCESS,"Branches matches, current branch $$CHOOSED_BRANCH"); \
	fi

