# WebSocket Template

A production-ready FastAPI template for building WebSocket backends with Docker support, logging, and a minimal HTTP health check.

## Features

- **FastAPI + WebSocket**: Native WebSocket support with FastAPI
- **Docker Support**: Multi-stage Dockerfile and docker-compose for easy deployment
- **Logging**: File and console logging
- **Health Check**: HTTP GET `/` for readiness (e.g. Docker health checks)
- **Configuration**: JSON-based configuration and env vars
- **Development Ready**: Hot reload via start scripts

## Project Structure

```
websocket_template/
├── src/
│   ├── ws_endpoints/           # WebSocket route handlers
│   │   └── ws_root.py          # Main WebSocket endpoint
│   ├── core_specs/             # Configuration and data
│   │   ├── configuration/     # JSON config and loaders
│   │   └── data/              # Data files and loaders
│   └── utils/                 # Utilities
│       └── custom_logger.py   # Logging setup
├── logs/                      # Log files (created automatically)
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── DOCKERFILE                 # Docker build configuration
├── docker-compose.yml         # Docker Compose configuration
├── .env.example               # Environment variables template
├── .dockerignore
├── .pylintrc
├── start.bat                  # Windows dev startup
├── start.sh                   # Unix dev startup
└── README.md                  # This file
```

## Quick Start

### Option 1: Run with Python (Development)

1. **Setup**:
   ```bash
   cd templates/websocket_template
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment**:
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

3. **Run**:
   ```bash
   python main.py
   ```
   Or use `start.bat` (Windows) / `start.sh` (Unix) for venv + install + run options.

4. **Connect**:
   - Health: http://localhost:8000/
   - WebSocket: ws://localhost:8000/ws
   - Docs: http://localhost:8000/docs

### Option 2: Run with Docker

```bash
cd templates/websocket_template
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

# API
API_TITLE=WebSocket Template
API_VERSION=1.0.0
API_DESCRIPTION=A template for building WebSocket backends with FastAPI
```

### JSON Configuration

See `src/core_specs/configuration/config_file.json` for:
- Network (host, port, reload, workers)
- Logging (level, dir, file name)
- WebSocket route path

## Adding WebSocket Endpoints

1. **New WebSocket handler** in `src/ws_endpoints/` (e.g. `ws_echo.py`):
   ```python
   from fastapi import APIRouter, WebSocket, WebSocketDisconnect
   from src.utils.custom_logger import log_handler

   router = APIRouter()

   @router.websocket("/ws/custom")
   async def websocket_custom(websocket: WebSocket):
       await websocket.accept()
       try:
           while True:
               data = await websocket.receive_text()
               log_handler.info(f"Received: {data}")
               await websocket.send_text(f"Echo: {data}")
       except WebSocketDisconnect:
           log_handler.info("Client disconnected")
   ```

2. **Register in `main.py`**:
   ```python
   from src.ws_endpoints.ws_echo import router as ws_custom_router
   app.include_router(ws_custom_router)
   ```

## Testing the WebSocket

From browser console or a WebSocket client:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => ws.send(JSON.stringify({ type: 'ping' }));
ws.onmessage = (e) => console.log(e.data);
```

Or use the interactive docs at http://localhost:8000/docs and try the WebSocket endpoint.

## Requirements

- Python 3.12+
- Docker / Docker Compose (optional)

## License

This template is provided as-is for educational and development purposes.
