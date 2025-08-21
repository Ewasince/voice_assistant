REMOTE_HOST := cloud
REMOTE_INSTALL_LOCATION := ~/psychoapp_docker
REMOTE_SCREEN_SESSION_NAME := psychoapp_docker

AGREGATOR_TAG := agregator


#CONTAINER_NAME_BACKEND := psychoapp_backend
#CONTAINER_NAME_BOT := psychoapp_bot
#
#DATA_PATH := images

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
	@ssh -t $(REMOTE_HOST) '\
		cd $(REMOTE_INSTALL_LOCATION) && \
		touch .env && \
		docker compose down $(CONTAINER_NAME_BACKEND) $(CONTAINER_NAME_BOT) && \
		screen -S $(REMOTE_SCREEN_SESSION_NAME) -X quit || echo no screen && \
		docker compose pull && \
		docker compose up -d $(CONTAINER_NAME_BACKEND) $(CONTAINER_NAME_BOT) && \
		screen -S $(REMOTE_SCREEN_SESSION_NAME) -c .screenrc'

.PHONY: upload_data
upload_data:
	@scp $(DATA_PATH)/* $(REMOTE_HOST):$(REMOTE_INSTALL_LOCATION)/$(DATA_PATH)

