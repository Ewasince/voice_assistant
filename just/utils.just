

# push → чистое дерево, получить текущий тег и запушить образы + git tags
@error msg:
  echo "❌ {{msg}}" >&2; exit 1

@success msg:
  echo "✅ {{msg}}"
