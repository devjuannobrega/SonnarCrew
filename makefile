# Makefile para Code Analysis Agent
# Facilita comandos Docker e desenvolvimento

# Variáveis
IMAGE_NAME = code-analysis-agent
TAG = latest
CONTAINER_NAME = code-analysis-api

# Help
.PHONY: help
help:
	@echo "Code Analysis Agent - Comandos Docker"
	@echo "====================================="
	@echo ""
	@echo "Build:"
	@echo "  build          Build da imagem Docker"
	@echo "  build-prod     Build para produção"
	@echo "  build-dev      Build para desenvolvimento"
	@echo ""
	@echo "Execução:"
	@echo "  run            Executar container"
	@echo "  run-dev        Executar em modo desenvolvimento"
	@echo "  up             Subir todos os serviços (docker-compose)"
	@echo "  down           Parar todos os serviços"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  logs           Mostrar logs do container"
	@echo "  shell          Abrir shell no container"
	@echo "  test           Testar a aplicação"
	@echo ""
	@echo "Limpeza:"
	@echo "  clean          Limpar containers parados"
	@echo "  clean-all      Limpar containers e imagens"

# Build commands
.PHONY: build
build:
	docker build -t $(IMAGE_NAME):$(TAG) .

.PHONY: build-prod
build-prod:
	docker build -t $(IMAGE_NAME):prod -t $(IMAGE_NAME):latest .

.PHONY: build-dev
build-dev:
	docker build -t $(IMAGE_NAME):dev .

# Run commands
.PHONY: run
run:
	docker run -d \
		--name $(CONTAINER_NAME) \
		-p 8000:8000 \
		-e DB_HOST=host.docker.internal \
		-e DB_PASSWORD=251081 \
		$(IMAGE_NAME):$(TAG)

.PHONY: run-dev
run-dev:
	docker run -it --rm \
		--name $(CONTAINER_NAME)-dev \
		-p 8000:8000 \
		-v "$(PWD):/app" \
		-e DB_HOST=host.docker.internal \
		-e DB_PASSWORD=251081 \
		-e ENVIRONMENT=development \
		$(IMAGE_NAME):$(TAG)

# Docker Compose commands
.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: up-build
up-build:
	docker-compose up -d --build

# Development commands
.PHONY: logs
logs:
	docker logs -f $(CONTAINER_NAME)

.PHONY: shell
shell:
	docker exec -it $(CONTAINER_NAME) /bin/bash

.PHONY: test
test:
	docker run --rm \
		-e DB_HOST=host.docker.internal \
		-e DB_PASSWORD=251081 \
		$(IMAGE_NAME):$(TAG) \
		python -m pytest tests/ -v

# Cleanup commands
.PHONY: clean
clean:
	docker container prune -f
	docker image prune -f

.PHONY: clean-all
clean-all:
	docker stop $(CONTAINER_NAME) || true
	docker rm $(CONTAINER_NAME) || true
	docker rmi $(IMAGE_NAME):$(TAG) || true
	docker container prune -f
	docker image prune -a -f

# Status commands
.PHONY: status
status:
	@echo "Containers:"
	@docker ps -a --filter name=$(CONTAINER_NAME)
	@echo ""
	@echo "Imagens:"
	@docker images $(IMAGE_NAME)

# Quick development workflow
.PHONY: dev
dev: build-dev run-dev