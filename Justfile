set shell := ["bash", "-euo", "pipefail", "-c"]

# Подтягиваем модули под неймспейсами
import "./just/git.just"
import "./just/docker.just"
import "./just/deploy.just"
import "./just/utils.just"
