.PHONY: error
error:
	echo "❌ $(ARGS)" >&2; exit 1

.PHONY: success
success:
	echo "✅ $(ARGS)"