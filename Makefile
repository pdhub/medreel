.PHONY: up down logs test e2e

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose exec api python -m pytest -q -p no:cacheprovider

e2e:
	docker compose exec api python tests/end_to_end/e2e.py http://localhost:8000
