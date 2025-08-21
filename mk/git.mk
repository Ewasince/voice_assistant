TAG_REGEXP := ^v[0-9]+\.[0-9]+\.[0-9]+$$

GIT_NP := git --no-pager

define CHECK_BRANCH
	@CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD) && \
	if [ "$$CURRENT_BRANCH" != "$(1)" ]; then \
		echo "❌ Forbid prod build, because branch '$$CURRENT_BRANCH' is not '$(1)'!"; \
		exit 1; \
	else \
		echo "✅ Allow prod build, because branch $(1)"; \
	fi
endef

define PRINT_CURRENT_PROD_TAG
	t=$$(git tag --points-at HEAD | grep -E '$(TAG_REGEXP)' | head -n1); \
	[ -n "$$t" ] || { echo "HEAD not marked with tag like vMAJOR.MINOR.PATCH" >&2; exit 1; }; \
	printf '%s\n' "$$t"
endef

define ENSURE_CLEAN_WORKTREE
	@git update-index -q --refresh && \
	git diff --quiet --ignore-submodules -- 2> /dev/null || { \
	  echo "Есть незакоммиченные (unstaged) изменения" >&2; exit 1; }; \
	git diff --cached --quiet --ignore-submodules -- 2> /dev/null  || { \
	  echo "Есть изменения в индексе (staged), не закоммиченные" >&2; exit 1; }; \
	test -z "$$(git ls-files --others --exclude-standard)" || { \
	  echo "Есть untracked-файлы" >&2; exit 1; }
endef
