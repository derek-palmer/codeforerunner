COMPOSE ?= docker compose
SERVICE ?= forerunner
UID ?= $(shell id -u)
GID ?= $(shell id -g)
COMPOSE_ENV = env UID=$(UID) GID=$(GID)

.PHONY: build up down run help init check compose-config uv-run uvx-run uv-sync uv-test uv-lint uv-format-check package-build package-check package-verify

# Build the container image for the forerunner service.
build:
	$(COMPOSE_ENV) $(COMPOSE) build $(SERVICE)

# Start the service with the default compose command, rebuilding first.
up:
	$(COMPOSE_ENV) $(COMPOSE) up --build $(SERVICE)

# Stop compose services and remove orphaned containers.
down:
	$(COMPOSE) down --remove-orphans

# Run the forerunner container with an arbitrary CLI argument string.
run:
	$(COMPOSE_ENV) $(COMPOSE) run --rm $(SERVICE) $(ARGS)

# Run uv inside the containerized development environment.
uv-run:
	$(COMPOSE_ENV) $(COMPOSE) run --rm --entrypoint uv $(SERVICE) $(ARGS)

# Run uvx inside the containerized development environment.
uvx-run:
	$(COMPOSE_ENV) $(COMPOSE) run --rm --entrypoint uvx $(SERVICE) $(ARGS)

# Sync development dependencies through containerized uv.
uv-sync:
	$(MAKE) uv-run ARGS="sync --dev"

# Run tests through containerized uv.
uv-test:
	$(MAKE) uv-run ARGS="run pytest"

# Run Ruff lint checks through containerized uv.
uv-lint:
	$(MAKE) uv-run ARGS="run ruff check ."

# Check Ruff formatting through containerized uv.
uv-format-check:
	$(MAKE) uv-run ARGS="run ruff format --check ."

# Build package distributions through containerized uv.
package-build:
	$(MAKE) uv-run ARGS="build"

# Validate existing package distributions through containerized uvx.
package-check:
	$(MAKE) uvx-run ARGS="twine check dist/*"

# Run the local package verification flow used before publishing.
package-verify: uv-test uv-lint uv-format-check package-build package-check

# Show CLI help through the containerized forerunner entrypoint.
help:
	$(MAKE) run ARGS="--help"

# Run the placeholder init command inside the container.
init:
	$(MAKE) run ARGS="init"

# Run the placeholder check command inside the container.
check:
	$(MAKE) run ARGS="check"

# Render the fully resolved Docker Compose configuration.
compose-config:
	$(COMPOSE_ENV) $(COMPOSE) config
