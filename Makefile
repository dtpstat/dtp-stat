# Repce with your compose file
COMPOSE_FILE=docker-compose.example.yml

run:
	docker-compose -f $(COMPOSE_FILE) up -d
down:
	docker-compose -f $(COMPOSE_FILE) down
sh:
	docker-compose -f $(COMPOSE_FILE) exec -T web /bin/bash
build:
	docker-compose -f $(COMPOSE_FILE) build
test:
	docker-compose -f $(COMPOSE_FILE) exec -T web pytest
