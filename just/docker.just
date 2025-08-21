# Конфиг
IMAGE_NAME  := "voice_assistant"
DOCKER_DIR  := "docker"
DOCKER_REPO := "ewasince"

# Сборка сервиса с ARG TAG
# usage: just docker:build <service>
build service:
  @image_tag="{{IMAGE_NAME}}:{{service}}"
  @docker compose -f "{{DOCKER_DIR}}/docker-compose.yml" build "{{service}}" --build-arg TAG="$image_tag"
  @echo "$image_tag builded"

# Тегирование и пуш; запрещаем перезаливку существующего версионного тега
# usage: just docker:pin-tag-and-push-docker <service> <version>
pin-tag-and-push-docker service version:
  @image_tag="{{IMAGE_NAME}}:{{service}}"
  @latest_tag="{{DOCKER_REPO}}/${image_tag}-latest"
  @current_tag="{{DOCKER_REPO}}/${image_tag}-{{version}}"
  @if docker images --format "{{'{{'}}.Repository{{'}}'}}:{{'{{'}}.Tag{{'}}'}}" | grep -q "^$current_tag$"; then \
    echo "Forbidden to re-upload version tags '$current_tag'" >&2; \
    exit 1; \
  fi
  @docker tag "$image_tag" "$latest_tag"
  @docker tag "$image_tag" "$current_tag"
  @docker push "$latest_tag"
  @docker push "$current_tag"
  @echo "$latest_tag pushed"
  @echo "$current_tag pushed"
