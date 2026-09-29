# RPC API Template (Python)

A FastAPI template for a **small, local RPC-style HTTP + JSON backend** — aimed at review UIs and similar tools — with **Server-Sent Events (SSE)** for long agent runs. This is **not** a resource-oriented REST API.

## RPC vs REST (what this template assumes)

| REST-style | This template (RPC-style) |
|------------|---------------------------|
| `GET /reviews/42` | `POST /rpc/invoke` with `{ "method": "getExampleRunStatus", "params": { "run_id": "..." } }` |
| Nouns in URLs, HTTP verbs carry meaning | **Procedures** (`startExampleAgentRun`, `cancelExampleRun`) |
| Stateless resource representations | **Actions** + job state in your services |
| Polling for progress | **SSE** stream: `GET /rpc/streamExampleAgentRun?run_id=...` |

You can expose procedures in two ways:

1. **Gateway** — `POST /rpc/invoke` dispatches by `method` name (`src/rpc/rpc_registry.py`).
2. **Explicit action URLs** — e.g. `POST /rpc/startExampleAgentRun` for clients that prefer one endpoint per operation.

Both call the same service layer (`src/resources/agent_run_service.py`).

## Features

- FastAPI + Uvicorn (same stack as `python_rest_api_template`)
- Procedure registry with typed params (Pydantic)
- Example long-running **agent run** with cancel + event log
- **SSE streaming** for live UI updates
- Config-driven routes (`config_loader`), rate limiting, logging, optional Redis
- Docker / docker-compose (copied from REST template)

## Project structure

```
python_rpc_api_template/
├── main.py
├── src/
│   ├── rpc_endpoints/
│   │   ├── root_endpoint.py              # GET / health + procedure list
│   │   └── procedures/
│   │       ├── invoke_procedure.py       # POST /rpc/invoke
│   │       ├── start_agent_run_procedure.py
│   │       └── stream_agent_run_procedure.py  # SSE
│   ├── rpc/
│   │   └── rpc_registry.py             # Register new procedures here
│   ├── models/
│   │   └── rpc_models.py
│   ├── resources/
│   │   └── agent_run_service.py          # Replace with real agent logic
│   ├── core_specs/                       # config + static data (same pattern as REST)
│   └── utils/                            # logger, limiter, validators, etc.
```

## Quick start

```bash
cd templates/python_rpc_api_template
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env.local   # optional keys for en_de_crypt
python main.py
```

- Health: http://localhost:8000/
- Docs: http://localhost:8000/docs

## Example flow (review UI)

**1. Start a run (invoke gateway)**

```bash
curl -s -X POST http://localhost:8000/rpc/invoke \
  -H "Content-Type: application/json" \
  -d '{"method":"startExampleAgentRun","params":{"review_id":"rev-1","prompt":"Check security"}}'
```

**2. Or explicit action URL**

```bash
curl -s -X POST http://localhost:8000/rpc/startExampleAgentRun \
  -H "Content-Type: application/json" \
  -d '{"review_id":"rev-1","prompt":"Check security"}'
```

**3. Stream events (SSE)**

```bash
curl -N "http://localhost:8000/rpc/streamExampleAgentRun?run_id=<RUN_ID>"
```

**4. Poll status (invoke)**

```bash
curl -s -X POST http://localhost:8000/rpc/invoke \
  -H "Content-Type: application/json" \
  -d '{"method":"getExampleRunStatus","params":{"run_id":"<RUN_ID>"}}'
```

**5. Cancel**

```bash
curl -s -X POST http://localhost:8000/rpc/invoke \
  -H "Content-Type: application/json" \
  -d '{"method":"cancelExampleRun","params":{"run_id":"<RUN_ID>"}}'
```

Registered procedures (see `GET /` or `rpc_registry.py`):

- `ping`
- `listExampleRuns`
- `startExampleAgentRun`
- `getExampleRunStatus`
- `cancelExampleRun`

## Adding a new procedure

1. Add param/result models in `src/models/rpc_models.py` (if needed).
2. Implement business logic in `src/resources/` (keep routers thin).
3. Register an async handler in `src/rpc/rpc_registry.py`.
4. Optional: add a dedicated `src/rpc_endpoints/procedures/<name>_procedure.py` and an entry in `config_file.json` + `main.py`.
5. If the procedure is long-running, emit events from the service and add or extend an SSE route.

## Configuration

Same as the REST template: `src/core_specs/configuration/config_file.json` + `.env`. Endpoint prefixes and rate limits live under `endpoints` in the JSON config.

## When to use this template vs `python_rest_api_template`

| Use **RPC template** | Use **REST template** |
|----------------------|-------------------------|
| Local tool / review UI | Public or multi-client HTTP API |
| Named operations + streaming jobs | CRUD on resources |
| Single frontend owns the contract | HTTP caching, standard REST clients |

## License

Template provided as-is for education and development.
