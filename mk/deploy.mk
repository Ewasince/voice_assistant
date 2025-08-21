REMOTE_HOST := cloud
REMOTE_INSTALL_LOCATION := ~/psychoapp_docker
REMOTE_SCREEN_SESSION_NAME := psychoapp_docker

DOCKER_DIR := docker
DOCKER_REPO := ewasince

IMAGE_NAME := voice_assistant
AGREGATOR_TAG := agregator

TAG=$(shell git rev-parse --short HEAD)

MAIN_BRANCH := master


#CONTAINER_NAME_BACKEND := psychoapp_backend
#CONTAINER_NAME_BOT := psychoapp_bot
#
#DATA_PATH := images


define pin_tag_and_push
	@IMAGE_TAG=$(IMAGE_NAME):$(1) && \
	LATEST_TAG=$(DOCKER_REPO)/$$IMAGE_TAG-latest && \
	CURRENT_TAG=$(DOCKER_REPO)/$$IMAGE_TAG-$(shell git describe --tags) && \
	if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$$CURRENT_TAG$$" ; \
	then \
		echo "Forbidden to re-upload version tags '$$CURRENT_TAG'" >&2; \
		exit 1; \
	fi && \
	docker tag $$IMAGE_TAG $$LATEST_TAG && \
	docker tag $$IMAGE_TAG $$CURRENT_TAG && \
	docker push $$LATEST_TAG && \
	docker push $$CURRENT_TAG && \
	echo "$$LATEST_TAG pushed" && \
	echo "$$CURRENT_TAG pushed"
endef

define build
	@IMAGE_TAG=$(IMAGE_NAME):$(1) && \
	docker compose -f $(DOCKER_DIR)/docker-compose.yml build $(1) --build-arg TAG=$$IMAGE_TAG && \
	echo "$$IMAGE_TAG builded"
endef

define check_branch
	@CURRENT_BRANCH=$$(git rev-parse --abbrev-ref HEAD) && \
	if [ "$$CURRENT_BRANCH" != "$(1)" ]; then \
		echo "❌ Forbid prod build, because branch '$$CURRENT_BRANCH' is not '$(1)'!"; \
		exit 1; \
	else \
		echo "✅ Allow prod build, because branch $(1)"; \
	fi
endef

.PHONY: deploy
deploy: prod_build push remote_install

.PHONY: prod_build
prod_build:
	$(call check_branch,$(MAIN_BRANCH))
	$(call build,$(AGREGATOR_TAG))

.PHONY: push
push:
	$(call pin_tag_and_push,$(AGREGATOR_TAG))
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

