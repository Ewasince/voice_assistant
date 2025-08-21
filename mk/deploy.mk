REMOTE_HOST := cloud
REMOTE_INSTALL_LOCATION := ~/$(APP_NAME)
REMOTE_SCREEN_SESSION_NAME := $(APP_NAME)

AGREGATOR_TAG := agregator


#CONTAINER_NAME_BACKEND := psychoapp_backend
#CONTAINER_NAME_BOT := psychoapp_bot
#
DATA_PATH := host.data
REMOTE_DATA_PATH := data

.PHONY: deploy
deploy: prod_build push remote_install


.PHONY: ensure_all_stable
ensure_all_stable: _ensure_main_branch _ensure_clean_worktree

.PHONY: prod_build
prod_build: ensure_all_stable
	make _build_with_tag $(AGREGATOR_TAG)
	$(call SUCCESS,"All services was built!")

.PHONY: push
push: ensure_all_stable
	CURRENT_PROD_TAG=$$(make _print_current_prod_tag)
	make pin_tag_and_push_docker $(AGREGATOR_TAG) $$CURRENT_PROD_TAG
	git push --tags
	$(call SUCCESS,"Pushed!")

.PHONY: remote_install
remote_install:
	ssh -t $(REMOTE_HOST) '\
		CONTAINERS=$(call CONTAINER_NAME,$(AGREGATOR_TAG)) && \
		cd $(REMOTE_INSTALL_LOCATION) && \
		touch .env && \
		docker compose down $$CONTAINERS && \
		screen -S $(REMOTE_SCREEN_SESSION_NAME) -X quit || echo no screen && \
		docker compose pull && \
		docker compose up -d $$CONTAINERS && \
		screen -S $(REMOTE_SCREEN_SESSION_NAME) -c .screenrc'

.PHONY: remote_restart
remote_restart:
	ssh -t $(REMOTE_HOST) '\
		CONTAINERS=$(call CONTAINER_NAME,$(AGREGATOR_TAG)) && \
		cd $(REMOTE_INSTALL_LOCATION) && \
		touch .env && \
		docker compose down $$CONTAINERS && \
		screen -S $(REMOTE_SCREEN_SESSION_NAME) -X quit || echo no screen && \
		docker compose up -d $$CONTAINERS && \
		screen -S $(REMOTE_SCREEN_SESSION_NAME) -c .screenrc'

.PHONY: upload_data
upload_data:
	@scp $(DATA_PATH)/* $(REMOTE_HOST):$(REMOTE_INSTALL_LOCATION)/$(REMOTE_DATA_PATH)

.PHONY: upload_and_restart
upload_and_restart: upload_data remote_restart

define CONTAINER_NAME
$(APP_NAME)_$(1)
endef

