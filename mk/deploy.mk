REMOTE_HOST := cloud
REMOTE_INSTALL_LOCATION := ~/psychoapp_docker
REMOTE_SCREEN_SESSION_NAME := psychoapp_docker

AGREGATOR_TAG := agregator

GIT_MAIN_BRANCH := master


#CONTAINER_NAME_BACKEND := psychoapp_backend
#CONTAINER_NAME_BOT := psychoapp_bot
#
#DATA_PATH := images

.PHONY: deploy
deploy: prod_build push remote_install

.PHONY: prod_build
prod_build:
	$(call CHECK_BRANCH,$(GIT_MAIN_BRANCH))
	$(call BUILD,$(AGREGATOR_TAG))

.PHONY: push
push:
	$(call ENSURE_CLEAN_WORKTREE)
	$(call PIN_TAG_AND_PUSH_DOCKER,$(AGREGATOR_TAG),$(call PRINT_CURRENT_PROD_TAG))
	@git push

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

