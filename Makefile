run:
	docker-compose up
sh:
	docker-compose exec web /bin/bash
build:
	docker-compose build
test:
	docker-compose exec web pytest
