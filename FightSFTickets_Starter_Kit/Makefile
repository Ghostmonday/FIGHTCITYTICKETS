.PHONY: dev docker-up docker-down backend-dev frontend-dev test

dev: docker-up

docker-up:
	cp -n .env.template .env || true
	docker compose up --build

docker-down:
	docker compose down -v

backend-dev:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && uvicorn src.app:app --reload --port 8000

frontend-dev:
	cd frontend && npm install && npm run dev

test:
	cd backend && . .venv/bin/activate 2>/dev/null || true && pytest -q
