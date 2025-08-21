define ERROR
	{ echo "❌ $(subst ",,$(1))" >&2 && exit 1; }
endef

define SUCCESS
	echo "✅ $(subst ",,$(1))"
endef


.PHONY: error
error:
	echo "❌ $(ARGS)" >&2; exit 1

.PHONY: success
success:
	echo "✅ $(ARGS)"