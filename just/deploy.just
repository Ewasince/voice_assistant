# Конфиг из deploy.mk
REMOTE_HOST                := "cloud"
REMOTE_INSTALL_LOCATION    := "~/psychoapp_docker"
REMOTE_SCREEN_SESSION_NAME := "psychoapp_docker"

AGREGATOR_TAG              := "agregator"

# Опциональные имена контейнеров (оставь пустыми, если не нужны)
CONTAINER_NAME_BACKEND     := ""
CONTAINER_NAME_BOT         := ""

DATA_PATH                  := "images"

# зависимость на git:ensure-main-branch
prod-build: ensure-main-branch
  just docker:build {{AGREGATOR_TAG}}

# push → чистое дерево, получить текущий тег и запушить образы + git tags
push: ensure-clean-worktree
  @tag="$(just --quiet git:current-tag)"
  @just docker:pin-tag-and-push-docker {{AGREGATOR_TAG}} "$tag"
  @git push --tags

## Установка на сервере
#remote-install:
#  ssh -t {{REMOTE_HOST}} '
#    set -e
#    cd {{REMOTE_INSTALL_LOCATION}} &&
#    touch .env &&
#    docker compose down {{CONTAINER_NAME_BACKEND}} {{CONTAINER_NAME_BOT}} &&
#    screen -S {{REMOTE_SCREEN_SESSION_NAME}} -X quit || echo no screen &&
#    docker compose pull &&
#    docker compose up -d {{CONTAINER_NAME_BACKEND}} {{CONTAINER_NAME_BOT}} &&
#    screen -S {{REMOTE_SCREEN_SESSION_NAME}} -c .screenrc
#  '
#
## Копирование данных
#upload-data:
#  scp {{DATA_PATH}}/* {{REMOTE_HOST}}:{{REMOTE_INSTALL_LOCATION}}/{{DATA_PATH}}
#
## Полный деплой: билд → пуш → установка
#deploy: prod-build push remote-install
#  :
