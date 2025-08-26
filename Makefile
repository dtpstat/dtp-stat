.PHONY: all up down clean sh build test

# Replace with your compose file
COMPOSE_FILE=docker-compose.example.yml

up:
	docker compose -f $(COMPOSE_FILE) up -d
down:
	docker compose -f $(COMPOSE_FILE) down
clean:
	docker compose -f $(COMPOSE_FILE) down -v
sh:
	docker compose -f $(COMPOSE_FILE) exec -it web /bin/bash
build:
	docker compose -f $(COMPOSE_FILE) build
test:
	docker compose -f $(COMPOSE_FILE) exec -it web pytest

all: build up