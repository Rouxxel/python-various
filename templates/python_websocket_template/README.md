# WebSocket Template

A production-ready FastAPI template for building WebSocket backends with Docker support, logging, configuration management, input validation, and a minimal HTTP health check.

## Features

- **FastAPI + WebSocket**: Native WebSocket support with FastAPI
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Logging**: File and console logging with configurable levels
- **Health Check**: HTTP GET `/` for readiness (e.g. Docker health checks)
- **Configuration**: JSON-based configuration management via `config_loader`
- **Input Validation**: Pydantic message envelopes + `validators.py` helpers
- **Connection Management**: Shared `ConnectionManager` for broadcasting to many clients
- **Security**: Non-root user in Docker, input validation, encryption utilities
- **Development Ready**: Hot reload via start scripts

## Project Structure

```
python_websocket_template/
├── src/
│   ├── ws_endpoints/               # WebSocket route handlers
│   │   ├── ws_root.py              # Main WebSocket endpoint (/ws echo)
│   │   ├── specific_ws_group_1/
│   │   │   └── example_echo_ws.py      # Reference handler — structured echo
│   │   └── specific_ws_group_2/
│   │       └── example_broadcast_ws.py # Reference handler — broadcast / chat room
│   ├── api_endpoints/              # HTTP route definitions
│   │   └── root_endpoint.py            # Root / health-check endpoint
│   ├── core_specs/                 # Core configuration and static data
│   │   ├── configuration/
│   │   │   ├── config_file.json        # Network, logging, endpoint settings
│   │   │   └── config_loader.py        # Loads config_file.json → config_loader
│   │   └── data/
│   │       ├── general_data.json         # Static reference data
│   │       └── data_loader.py            # Loads general_data.json → data_loader
│   ├── models/
│   │   ├── models_example.py           # Pydantic model pattern (Base/Create/Update/Response)
│   │   └── ws_messages_example.py      # WebSocket message envelope models
│   ├── resources/                  # Database-related assets (placeholder)
│   │   ├── db/                         # Migration files (add when needed)
│   │   └── mock_db_jsons/              # Mock JSON tables (add when needed)
│   └── utils/
│       ├── custom_logger.py        # Logging configuration (log_handler)
│       ├── ws_connection_manager.py # Shared ConnectionManager (broadcast support)
│       ├── validators.py           # Email, password, phone, token, UUID validators
│       ├── en_de_crypt.py          # RSA encrypt/decrypt (requires .env keys)
│       ├── keys_generator.py       # One-off script to generate RSA key pairs
│       ├── secure_file_io.py       # Hardened atomic file read/write helpers
│       └── pycache_n_logs_deleter.py  # Dev utility to purge __pycache__ / logs
├── logs/                           # Log files (created automatically)
├── main.py                         # Application entry point
├── requirements.txt                # Python dependencies
├── start.sh / start.bat            # Dev setup and launch scripts
├── DOCKERFILE                      # Docker build configuration
├── docker-compose.yml              # Docker compose configuration
├── .env / .env.example             # Environment variables template
├── .dockerignore
├── .pylintrc
├── .gitignore
└── README.md
```

## Quick Start

### Option 1: Run with Python (Development)

1. **Clone and setup**:
   ```bash
   cd templates/python_websocket_template
   python -m venv venv
   source venv/bin/activate          # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env              # or copy .env on Windows
   # Edit .env if needed — set E_PRIVATE_KEY, E_PRIVATE_PASSWORD, E_PUBLIC_KEY
   # (run src/utils/keys_generator.py once to generate them if you use en_de_crypt.py)
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```
   Or use `start.bat` (Windows) / `start.sh` (Unix) for venv + install + run options.

4. **Connect**:
   - Health check: http://localhost:8000/
   - WebSocket (echo): ws://localhost:8000/ws
   - WebSocket (example structured echo): ws://localhost:8000/subsection/echo
   - WebSocket (example broadcast): ws://localhost:8000/subsection/broadcast
   - Docs: http://localhost:8000/docs

### Option 2: Run with Docker

```bash
cd templates/python_websocket_template
docker-compose up --build
```

Or manually:

```bash
docker build -t websocket-template -f DOCKERFILE .
docker run -p 8000:8000 --env-file .env websocket-template
```

## Configuration

### Environment Variables (.env)

```bash
# Server
SERVER_PORT=8000
HOST=0.0.0.0
RELOAD=false
WORKERS=1

# Logging
LOG_LEVEL=info

# RSA encryption keys (required by en_de_crypt.py)
E_PRIVATE_KEY=your_private_key_here
E_PRIVATE_PASSWORD=your_private_password_here
E_PUBLIC_KEY=your_public_key_here

# API metadata (read by main.py)
API_TITLE=WebSocket Template
API_VERSION=1.0.0
API_DESCRIPTION=A template for building WebSocket backends with FastAPI
```

### JSON Configuration (`config_file.json` + `config_loader`)

`config_loader.py` reads `config_file.json` at import time and exposes the result as `config_loader` (a dict). Every handler should pull its prefix, tag, and route from here rather than hard-coding them.

**Sections in `config_file.json`:**

| Section | Purpose |
|---|---|
| `defaults` | Shared paths and defaults |
| `logging` | Log level, directory, file name prefix |
| `network` | Uvicorn host, port, workers, reload |
| `endpoints` | Per-endpoint prefix, tag, and route (`endpoint_route` for HTTP, `ws_route` for WebSocket) |

**WebSocket endpoint config shape** (one entry per handler):

```json
"example_ws_endpoint_1": {
    "endpoint_prefix": "/subsection",
    "endpoint_tag": "tag_name",
    "ws_route": "/echo"
}
```

**Usage in a handler:**

```python
from fastapi import APIRouter, WebSocket
from src.core_specs.configuration.config_loader import config_loader

cfg = config_loader["endpoints"]["example_ws_endpoint_1"]

router = APIRouter(prefix=cfg["endpoint_prefix"], tags=[cfg["endpoint_tag"]])

@router.websocket(cfg["ws_route"])
async def my_ws(websocket: WebSocket):
    await websocket.accept()
    ...
```

### Static Data (`general_data.json` + `data_loader`)

`data_loader.py` works the same way as `config_loader` but loads `src/core_specs/data/general_data.json`. Use it for reference data that is not environment-specific (e.g. supported languages, lookup tables).

```python
from src.core_specs.data.data_loader import data_loader

languages = data_loader["languages"]
```

## Adding WebSocket Endpoints

Use the two example handlers as the canonical reference. They demonstrate every pattern the template expects:

| File | Role | Config key | Demonstrates |
|---|---|---|---|
| `specific_ws_group_1/example_echo_ws.py` | Structured echo (single client) | `example_ws_endpoint_1` | Inbound validation, validators, data_loader, typed replies |
| `specific_ws_group_2/example_broadcast_ws.py` | Broadcast / chat room (many clients) | `example_ws_endpoint_2` | Shared `ConnectionManager`, fan-out broadcast, disconnect cleanup |

Each file contains **one WebSocket endpoint only**. Add further endpoints in separate files within the same group folder so the code stays organized in folders rather than a single endless file.

**Steps to add a new endpoint group:**

1. Add an entry under `endpoints` in `config_file.json` with a `ws_route`.
2. Create message models in `src/models/` (follow `ws_messages_example.py`).
3. Copy `example_echo_ws.py` (single client) or `example_broadcast_ws.py` (multi-client) into a new file under `src/ws_endpoints/<your_group>/`.
4. Register the router in `main.py`:
   ```python
   from src.ws_endpoints.your_group.your_ws import router as your_ws_router
   app.include_router(your_ws_router)
   ```

**Example endpoints shipped with the template:**

| Protocol | Path | Description |
|---|---|---|
| `GET` | `/` | HTTP health check |
| `WS` | `/ws` | Plain text echo (minimal example) |
| `WS` | `/subsection/echo` | Structured, validated echo with typed replies |
| `WS` | `/subsection/broadcast` | Broadcast to all connected clients (chat room) |

## Message Models (`src/models/`)

A WebSocket carries a stream of discrete messages over one connection, so the template validates each frame against a typed envelope instead of a single request body.

`ws_messages_example.py` shows the recommended split:

| Class | Role |
|---|---|
| `EchoMessageIn` | What a client may send to the echo endpoint (validated per frame) |
| `ChatMessageIn` | What a client may send to the broadcast endpoint |
| `WsMessageOut` | The single server-to-client envelope (`type` + `data`) for every reply |

Keeping one outgoing shape with a `type` discriminator lets the client branch on `type` and lets you add new message kinds later without breaking existing clients.

`models_example.py` keeps the REST-style Base / Create / Update / Response Pydantic split, useful when a WebSocket service also persists entities or exposes companion HTTP routes.

## Utilities (`src/utils/`)

| Module | When to use |
|---|---|
| `custom_logger.py` | `log_handler` — use everywhere instead of `print` |
| `ws_connection_manager.py` | Shared `connection_manager` — register connections and broadcast to all clients |
| `validators.py` | `validate_email_format`, `validate_password_format`, `validate_phone_format`, token/UUID checks |
| `en_de_crypt.py` | `encrypt_in` / `decrypt_out` for RSA-encrypted message fields |
| `keys_generator.py` | Run once to generate `E_PRIVATE_KEY` / `E_PUBLIC_KEY` for `.env` |
| `secure_file_io.py` | Safe atomic file reads/writes with path confinement |
| `pycache_n_logs_deleter.py` | Dev cleanup script — set `ROOT_FOLDER` before running |

### Connection Manager

`ws_connection_manager.py` exposes a single shared `connection_manager` instance (the WebSocket analogue of a shared limiter). Import it; do not instantiate your own.

```python
from src.utils.ws_connection_manager import connection_manager

await connection_manager.connect(websocket)        # accept + register
await connection_manager.broadcast({"type": "x"})   # send to everyone
await connection_manager.send_personal(msg, ws)     # send to one client
connection_manager.disconnect(websocket)            # unregister on disconnect
```

The in-memory registry is sufficient for a single process. For multiple workers/replicas, back broadcasts with Redis pub/sub (or a similar broker) since connections live in different processes.

## Testing the WebSockets

### Minimal echo (`/ws`)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => ws.send('hello');
ws.onmessage = (e) => console.log(e.data);   // "Echo: hello"
```

### Structured echo (`/subsection/echo`)

Send JSON matching `EchoMessageIn`; receive a `WsMessageOut` envelope.

```javascript
const ws = new WebSocket('ws://localhost:8000/subsection/echo');
ws.onopen = () => ws.send(JSON.stringify({
  name: "Alice",
  message: "hi there",
  contact_email: "alice@gmail.com"  // optional, validated when present
}));
ws.onmessage = (e) => console.log(e.data);
// {"type":"echo","data":{"name":"Alice","message":"hi there"}}
```

### Broadcast / chat room (`/subsection/broadcast`)

Open the connection in two or more clients; a message from one is delivered to all.

```javascript
const ws = new WebSocket('ws://localhost:8000/subsection/broadcast');
ws.onopen = () => ws.send(JSON.stringify({ username: "Alice", text: "hello room" }));
ws.onmessage = (e) => console.log(e.data);
// {"type":"chat","data":{"username":"Alice","text":"hello room"}}
```

Invalid frames receive an `{"type":"error", ...}` envelope instead of dropping the connection. You can also use the interactive docs at http://localhost:8000/docs.

## Security Features

- **Input Validation**: Pydantic message envelopes validate every inbound frame + `validators.py` helpers
- **Encryption**: RSA utilities in `en_de_crypt.py` (keys from environment)
- **Non-root Docker**: Container runs as non-root user
- **Resilient Broadcast**: Stale connections are dropped so one dead socket cannot block delivery
- **Environment Variables**: Sensitive data via `.env`, never committed

## Logging

- **File Logging**: Timestamped log files in `logs/`
- **Console Logging**: Structured output for containers
- **Configurable Levels**: Set via `logging.logging_level` in `config_file.json`
- **Connection Logging**: Connect/disconnect and received frames logged via `log_handler`

## Docker Features

### Multi-stage Build
- **Builder stage**: Installs dependencies
- **Production stage**: Minimal runtime image
- **Security**: Non-root user execution
- **Health checks**: Built-in container health monitoring via `GET /`

### Docker Compose
- **Production**: Optimized for deployment
- **Services**: Ready for Redis, PostgreSQL integration (commented in compose file)
- **Volumes**: Persistent log storage

## Development

### Hot Reload

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Or use `start.bat` / `start.sh` and choose development mode.

### Adding Dependencies

```bash
pip install new-package
pip freeze > requirements.txt
```

## Deployment

1. Update environment variables for production.
2. For multiple replicas, move broadcast state to Redis pub/sub (see Connection Manager note).
3. Build: `docker build -t your-ws-api:latest .`
4. Deploy: `docker-compose up -d`

Compatible with AWS ECS/Fargate, Google Cloud Run, Azure Container Instances, Heroku, DigitalOcean App Platform, and similar. Ensure the platform/load balancer supports WebSocket upgrades and sticky sessions where applicable.

## Requirements

- Python 3.12+
- Docker (optional)
- Docker Compose (optional)

## Contributing

This is a template — customize it for your specific needs:

1. Update `config_file.json` and `.env`
2. Copy `example_echo_ws.py` / `example_broadcast_ws.py` and `ws_messages_example.py` as starting points
3. Implement your handlers and message models
4. Add tests
5. Update this README

## License

This template is provided as-is for educational and development purposes.
