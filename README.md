# Tiny Backspace

A FastAPI backend that streams autonomous coding agent progress via Server-Sent Events (SSE).

## Features

- POST `/code`: Streams real-time updates as an agent (dummy for now) works on a GitHub repo based on your prompt
- Modular structure for easy extension
- Logging with Loguru
- Ready for E2B sandbox integration

## Setting up the Environment

To ensure a clean and reproducible environment for your project, it's highly recommended to use a virtual environment (venv). This approach helps to isolate project dependencies from the system Python environment and ensures that all dependencies are consistently installed across different environments.

To create a virtual environment, run:

```sh
python -m venv venv
```

Then, activate the virtual environment:

```sh
source venv/bin/activate
```

On Windows, use `venv\Scripts\activate` instead.

## Install dependencies

Once the virtual environment is activated, install the project dependencies:

```sh
pip install -r requirements.txt
```

## Run the app

To run the application, use:

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
