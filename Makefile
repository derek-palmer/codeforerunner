IMAGE ?= codeforerunner-local
FORERUNNER_GOALS ?= $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
FORERUNNER_FLAGS ?=
ifeq ($(strip $(FORERUNNER_GOALS) $(FORERUNNER_FLAGS)),)
FORERUNNER_ARGS := doctor
else
FORERUNNER_ARGS := $(strip $(FORERUNNER_GOALS) $(FORERUNNER_FLAGS))
endif

.PHONY: docker-build forerunner docker-login-dhi

docker-login-dhi:
	docker login dhi.io

docker-build:
	docker compose build forerunner

forerunner: docker-build
	docker compose run --rm forerunner $(FORERUNNER_ARGS)

%:
	@:
