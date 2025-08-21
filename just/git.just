#set shell := ["bash", "-euo", "pipefail", "-c"]

TAG_RE           := '^v[0-9]+\.[0-9]+\.[0-9]+$'
GIT_MAIN_BRANCH  := "master"

## Проверка ветки
@ensure-main-branch:
  current="$(git rev-parse --abbrev-ref HEAD)"; \
  if [[ "$current" != {{GIT_MAIN_BRANCH}} ]]; then \
    just error "Forbid prod build, because branch '$current' is not '{{GIT_MAIN_BRANCH}}'!" >&2; \
  else \
    just success "Allow prod build, because branch {{GIT_MAIN_BRANCH}}"; \
  fi


@ensure-clean-worktree: ensure-main-branch
  git update-index -q --refresh; \
  git diff --quiet --ignore-submodules -- 2>/dev/null \
    || just error "There is unstaged changes"; \
  git diff --cached --quiet --ignore-submodules -- 2>/dev/null \
    || just error  "There is changes in index (staged), not commited"; \
  if [[ -n "$(git ls-files --others --exclude-standard)" ]]; then \
    just error  "There is untracked-files" >&2; \
  fi

# Печатает тег vMAJOR.MINOR.PATCH, указывающий на HEAD
@current-tag:
  t="$(git tag --points-at HEAD | grep -E {{TAG_RE}} | head -n1 || true)"; \
  [[ -n "$t" ]] || just error "HEAD not marked with tag like vMAJOR.MINOR.PATCH"; \
  printf '%s\n' "$t"
