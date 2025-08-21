
IMAGE_NAME := voice_assistant

DOCKER_DIR := docker
DOCKER_REPO := ewasince


#define PIN_TAG_AND_PUSH_DOCKER
#	@IMAGE_TAG=$(IMAGE_NAME):$(1) && \
#	LATEST_TAG=$(DOCKER_REPO)/$$IMAGE_TAG-latest && \
#	CURRENT_TAG=$(DOCKER_REPO)/$$IMAGE_TAG-$(2) && \
#	if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$$CURRENT_TAG$$" ; \
#	then \
#		echo "Forbidden to re-upload version tags '$$CURRENT_TAG'" >&2; \
#		exit 1; \
#	fi && \
#	docker tag $$IMAGE_TAG $$LATEST_TAG && \
#	docker tag $$IMAGE_TAG $$CURRENT_TAG && \
#	docker push $$LATEST_TAG && \
#	docker push $$CURRENT_TAG && \
#	echo "$$LATEST_TAG pushed" && \
#	echo "$$CURRENT_TAG pushed"
#endef

.PHONY:
pin_tag_and_push_docker:
	IMAGE_TAG=$(IMAGE_NAME):$(ARG1)
	LATEST_TAG=$(DOCKER_REPO)/$$IMAGE_TAG-latest
	CURRENT_TAG=$(DOCKER_REPO)/$$IMAGE_TAG-$(ARG2)
	if docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$$CURRENT_TAG$$" ; \
	then \
	  	make error "Forbidden to re-upload version tags '$$CURRENT_TAG'"; \
	fi
	docker tag $$IMAGE_TAG $$LATEST_TAG
	docker tag $$IMAGE_TAG $$CURRENT_TAG
	docker push $$LATEST_TAG
	docker push $$CURRENT_TAG
	make success "$$LATEST_TAG pushed"
	make success "$$CURRENT_TAG pushed"


define BUILD
	@IMAGE_TAG=$(IMAGE_NAME):$(1) && \
	docker compose -f $(DOCKER_DIR)/docker-compose.yml build $(1) --build-arg TAG=$$IMAGE_TAG && \
	echo "$$IMAGE_TAG builded"
endef