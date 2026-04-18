COMPOSE ?= docker compose
SERVICE ?= forerunner
UID ?= $(shell id -u)
GID ?= $(shell id -g)
COMPOSE_ENV = UID=$(UID) GID=$(GID)

.PHONY: docker-build docker-up docker-down docker-run docker-help docker-init docker-check compose-config

# Build the container image for the forerunner service.
docker-build:
	$(COMPOSE_ENV) $(COMPOSE) build $(SERVICE)

# Start the service with the default compose command, rebuilding first.
docker-up:
	$(COMPOSE_ENV) $(COMPOSE) up --build $(SERVICE)

# Stop compose services and remove orphaned containers.
docker-down:
	$(COMPOSE) down --remove-orphans

# Run the forerunner container with an arbitrary CLI argument string.
docker-run:
	$(COMPOSE_ENV) $(COMPOSE) run --rm $(SERVICE) $(ARGS)

# Show CLI help through the containerized forerunner entrypoint.
docker-help:
	$(MAKE) docker-run ARGS="--help"

# Run the placeholder init command inside the container.
docker-init:
	$(MAKE) docker-run ARGS="init"

# Run the placeholder check command inside the container.
docker-check:
	$(MAKE) docker-run ARGS="check"

# Render the fully resolved Docker Compose configuration.
compose-config:
	$(COMPOSE) config
