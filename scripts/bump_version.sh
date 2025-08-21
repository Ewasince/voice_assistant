#!/usr/bin/env sh
set -eu

usage() {
  cat <<EOF
Usage: $0 [major|minor|patch] [--push] [--dry-run|-n] [--prefix PREFIX]

Bumps semantic version tag (default bump: patch). Tags look like: PREFIXMAJOR.MINOR.PATCH (default PREFIX=v).
Examples:
  $0 patch
  $0 minor --push
  $0 major --dry-run --prefix v
EOF
}

# Defaults
bump="patch"
push=0
dry=0
prefix="v"

# Parse args
while [ $# -gt 0 ]; do
  case "$1" in
    major|minor|patch) bump="$1"; shift ;;
    --push)            push=1; shift ;;
    --dry-run|-n)      dry=1; shift ;;
    --prefix)
      [ $# -ge 2 ] || { echo "Missing value for --prefix" >&2; usage; exit 2; }
      prefix="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

# Require clean worktree (tracked + staged + untracked)
make --no-print-directory ensure_clean_worktree

# Get last semver-like tag reachable from HEAD (or PREFIX0.0.0)
last_tag="$(git describe --tags --abbrev=0 --match "${prefix}[0-9]*" 2>/dev/null || echo "${prefix}0.0.0")"

# Validate format: ^PREFIX[0-9]+\.[0-9]+\.[0-9]+$
tag_re="^${prefix}[0-9]+\.[0-9]+\.[0-9]+$"
printf '%s\n' "$last_tag" | grep -Eq "$tag_re" || { echo "Текущий тег не семвер: $last_tag" >&2; exit 1; }

# Split MAJOR.MINOR.PATCH
ver="${last_tag#${prefix}}"
IFS=. set -- $ver
maj="$1"; min="$2"; pat="$3"

# Bump
case "$bump" in
  major) maj=$((maj+1)); min=0; pat=0 ;;
  minor) min=$((min+1)); pat=0 ;;
  patch) pat=$((pat+1)) ;;
esac

new_tag="${prefix}${maj}.${min}.${pat}"

# Ensure tag doesn't exist
if git rev-parse -q --verify "refs/tags/${new_tag}" >/dev/null 2>&1; then
  echo "Тег уже существует: ${new_tag}" >&2
  exit 1
fi

# Create or dry-run
if [ "$dry" -eq 1 ]; then
  echo "[DRY] Создал бы тег: ${new_tag}"
else
  git tag -a "${new_tag}" -m "Release ${new_tag}"
  [ "$push" -eq 1 ] && git push origin "${new_tag}"
  echo "Создан тег: ${new_tag}"
fi

# Print tag for pipelines
printf '%s\n' "$new_tag"
