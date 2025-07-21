# Tiny Backspace

A FastAPI backend that streams autonomous coding agent progress via Server-Sent Events (SSE).

## Features

- POST `/code`: Streams real-time updates as an agent (dummy for now) works on a GitHub repo based on your prompt
- Modular structure for easy extension
- Logging with Loguru
- Ready for E2B sandbox integration

## Install dependencies

```sh
pip install -r requirements.txt
```

## Run the app

```sh
uvicorn app.main:app --reload
```

## Endpoints

- `POST /code` — SSE stream of agent progress (send JSON: `{ "repoUrl": "...", "prompt": "..." }`)
- `GET /stream-dummy` — Dummy SSE stream for testing

## E2B SDK Setup

- Install with `pip install e2b` (already in requirements.txt)
- See https://docs.e2b.dev/ for API key and sandbox setup

## Structure

- `app/main.py` — FastAPI app entrypoint
- `app/api/routes.py` — API endpoints
- `app/services/` — Agent and sandbox logic
- `app/utils/` — SSE helpers
- `app/logging_config.py` — Logging setup

---

_Replace the dummy agent and sandbox logic with real implementations as you build further!_
