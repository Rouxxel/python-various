# Backend

FastAPI backend for the analytics dashboard template. Supports mock mode (zero external services) and live mode with optional provider integrations.

## Project structure

```
backend/
├── app/
│   ├── core_specs/
│   │   └── configuration/
│   │       ├── config_file.json    # Logging, network, routes, mock paths
│   │       └── config_loader.py    # Loads JSON → config_loader dict
│   ├── routers/                    # API route handlers (paths from config)
│   ├── services/
│   │   ├── data_source.py          # Mock vs live abstraction
│   │   ├── live/                   # Live data builders
│   │   ├── providers/              # Supabase, Vercel, Datadog, etc.
│   │   ├── hosting/                # Render/Railway health + wake
│   │   └── costs/
│   ├── mock_data/                  # JSON payloads for mock mode
│   ├── utils/
│   │   ├── custom_logger.py        # log_handler (from python_various_utils pattern)
│   │   └── secure_file_io.py       # Safe JSON/file reads for mock data
│   ├── config.py                   # Secrets + feature flags from .env
│   ├── main.py                     # Dev entry (reload)
│   └── server.py                   # Production entry
├── logs/                           # Created at runtime
├── tests/
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

### Configuration split

| Source | Purpose |
|--------|---------|
| `config_file.json` + `config_loader` | App title, port defaults, log paths, API route prefixes, mock file map |
| `backend/.env` + `app.config.settings` | API keys, Supabase/Vercel credentials, feature flags, `DASHBOARD_DATA_MODE` |

## API Endpoints

The backend provides the following API endpoints:

| Router | Method | Path | Description |
|--------|--------|------|-------------|
| config | GET | `/api/config/features` | Feature flags and configuration |
| config | GET | `/api/config/env` | Environment configuration (sanitized) |
| health | GET | `/api/health` | Health check endpoint |
| overview | GET | `/api/overview` | Overview page metrics |
| metrics | GET | `/api/metrics` | Metrics gallery data |
| charts | GET | `/api/charts` | Charts gallery data |
| tables | GET | `/api/tables` | Tables gallery data |
| infrastructure | GET | `/api/infrastructure` | Infrastructure metrics |
| users | GET | `/api/users` | Users domain placeholder |
| activity | GET | `/api/activity` | Activity domain placeholder |
| costs | GET | `/api/costs` | Costs domain placeholder |
| ai | GET | `/api/ai` | AI metrics domain placeholder |
| insights | GET | `/api/insights` | Insights domain placeholder |
| sessions | GET | `/api/sessions` | Sessions domain placeholder |

## Mock vs live data

The backend operates in two modes controlled by `DASHBOARD_DATA_MODE` in `.env`:

- **`mock`** (default): Returns structured mock data from `app/mock_data/`. No external services required. Perfect for development and UI testing.
- **`live`**: Queries real data sources (Supabase, Vercel, etc.) via `app/services/live/`. Requires provider credentials.

### Switching modes

```bash
# In backend/.env
DASHBOARD_DATA_MODE=mock  # Use mock data
DASHBOARD_DATA_MODE=live  # Use live data
```

### When to use each mode

- **Mock mode**: Initial development, UI design, testing without credentials, demos
- **Live mode**: Production dashboards, real analytics, when you have database access

## How to add a new API endpoint

Follow this checklist to add a new endpoint:

1. **Define Pydantic model** in `app/models/` (or inline in router)
   ```python
   from pydantic import BaseModel
   
   class MyDataResponse(BaseModel):
       metric: str
       value: float
       trend: float
   ```

2. **Create data builder function** in `app/services/live/` (for live mode)
   ```python
   # app/services/live/my_analytics.py
   def build_my_data(from_date: datetime, to_date: datetime) -> MyDataResponse:
       # Your query logic here
       return MyDataResponse(metric="example", value=100, trend=0.05)
   ```

3. **Add mock data** in `app/mock_data/` (for mock mode)
   ```python
   # app/mock_data/my_data.json
   {
       "metric": "example",
       "value": 100,
       "trend": 0.05
   }
   ```

4. **Add router endpoint** in `app/routers/`
   ```python
   # app/routers/my_data.py
   from fastapi import APIRouter
   from app.services.data_source import get_data_source
   
   router = APIRouter()
   
   @router.get("/my-data", response_model=MyDataResponse)
   async def get_my_data(from_date: datetime, to_date: datetime):
       data_source = get_data_source()
       return data_source.get_my_data(from_date, to_date)
   ```

5. **Register router** in `app/main.py`
   ```python
   from app.routers import my_data
   app.include_router(my_data.router, prefix="/api", tags=["my_data"])
   ```

6. **Add TypeScript type** in `frontend/src/lib/types.ts`
   ```typescript
   export interface MyDataResponse {
       metric: string;
       value: number;
       trend: number;
   }
   ```

7. **Add fetch function** in `frontend/src/lib/api.ts`
   ```typescript
   export async function fetchMyData(from: string, to: string): Promise<MyDataResponse> {
       const response = await fetch(`${API_URL}/api/my-data?from_date=${from}&to_date=${to}`);
       return response.json();
   }
   ```

## Environment Variables

### Required Environment Variables

These variables are required for all modes:

| Variable | Description | Example |
|----------|-------------|---------|
| `API_KEY` | Secret API key for authentication | `your-secret-api-key` |
| `FRONTEND_URL` | Frontend URL for CORS configuration | `http://localhost:5173` |
| `DASHBOARD_BACKEND_HOST` | Backend host address | `127.0.0.1` |
| `DASHBOARD_BACKEND_PORT` | Backend port | `8001` |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | `INFO` |
| `DASHBOARD_DATA_MODE` | Data mode: `mock` or `live` | `mock` |

### Optional Environment Variables (Feature-Flagged)

These variables are only used when their corresponding feature flag is enabled:

| Feature Flag | Environment Variables | Description |
|-------------|----------------------|-------------|
| `FEATURE_SUPABASE` | `SUPABASE_URL_TEST`, `SUPABASE_ANON_KEY_TEST`, `SUPABASE_SERVICE_ROLE_KEY_TEST`, `SUPABASE_URL_PROD`, `SUPABASE_ANON_KEY_PROD`, `SUPABASE_SERVICE_ROLE_KEY_PROD` | Supabase database credentials for test and production environments |
| `FEATURE_VERCEL` | `VERCEL_BASE_URL`, `VERCEL_API_TOKEN`, `VERCEL_TEAM_ID`, `VERCEL_TEAM_URL`, `VERCEL_PROJECT_ID_TEST`, `VERCEL_PROJECT_NAME_TEST`, `VERCEL_PROJECT_ID_PROD`, `VERCEL_PROJECT_NAME_PROD` | Vercel API credentials and project IDs |
| `FEATURE_HOST_HEALTH` | `HOSTING_PROVIDER`, `RENDER_SERVICE_URL`, `RAILWAY_SERVICE_URL`, `FLY_SERVICE_URL`, `CUSTOM_SERVICE_URL`, `MAIN_API_URL_TEST`, `MAIN_API_URL_PROD` | Hosting provider configuration for health checks |
| `FEATURE_COSTS_MODULE` | `COSTS_UNIT_PRICE`, `COSTS_UNIT_NAME`, `COSTS_CURRENCY` | Cost tracking configuration |
| `FEATURE_STORAGE_METRICS` | (no specific vars, uses Supabase) | Storage bucket metrics (uses Supabase credentials) |

### External Provider Variables (Optional)

| Variable | Description | Used By |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | External AI services |
| `DEEPGRAM_API_KEY` | Deepgram API key | Speech recognition services |
| `DASHBOARD_ALLOWED_EMAILS` | Comma-separated list of allowed emails for authentication | Email-based auth |

## Optional provider modules

The backend includes optional integrations with third-party services. Each is controlled by a feature flag and environment variables.

### Supabase (database + storage)

**Feature flag**: `FEATURE_SUPABASE` (default `true` in live mode)

**Environment variables**:
```bash
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**What it provides**:
- Database queries for live data
- Storage bucket metrics
- Table row counts

**Disabling**: Set `FEATURE_SUPABASE=false` in `.env`

### Vercel (deployments + Web Analytics)

**Feature flag**: `FEATURE_VERCEL` (default `false`)

**Environment variables**:
```bash
VERCEL_PROJECT_ID=your-project-id
VERCEL_TEAM_ID=your-team-id  # optional
VERCEL_TOKEN=your-auth-token
```

**What it provides**:
- Deployment history
- Web analytics data
- Project metadata

**Disabling**: Set `FEATURE_VERCEL=false` in `.env`

### Render / Railway / Fly (host health + wake)

**Feature flag**: `FEATURE_HOST_HEALTH` (default `false`)

**Environment variables**:
```bash
HOSTING_PROVIDER=render  # or "railway", "fly", "custom"
RENDER_SERVICE_URL=your-service-url  # for Render
RAILWAY_SERVICE_URL=your-service-url  # for Railway
```

**What it provides**:
- Health check status
- Wake/sleep functionality (for free tier spin-down)
- Hosting provider-specific notes

**Disabling**: Set `FEATURE_HOST_HEALTH=false` in `.env`

### Third-party cost modules

**Feature flag**: `FEATURE_COSTS_MODULE` (default `false`)

**Environment variables**:
```bash
# Generic pricing (example)
COSTS_UNIT_PRICE=0.01
COSTS_UNIT_NAME="API call"
```

**What it provides**:
- Cost tracking and projections
- Unit economics calculations
- Optional provider-specific pricing (ElevenLabs, etc.)

**Disabling**: Set `FEATURE_COSTS_MODULE=false` in `.env`

## Disabling a module

To completely disable an optional module:

1. **Set feature flag to false** in `backend/.env`
   ```bash
   FEATURE_VERCEL=false
   ```

2. **Comment out router include** in `app/main.py` (optional, for cleaner logs)
   ```python
   # from app.routers import vercel
   # app.include_router(vercel.router, prefix="/api", tags=["vercel"])
   ```

3. **Hide sidebar link** in frontend `templateConfig.ts`
   ```typescript
   navItems: [
       // { id: "vercel", label: "Vercel", path: "/infrastructure", enabled: false }
   ]
   ```

Disabled modules return empty payloads with informational `notes[]` arrays explaining how to enable them.

## Architecture

```
Request → Middleware (CORS, auth) → Router → Data Layer → Mock or Live
                                                    │
                                                    ├─ MockDataSource
                                                    │  └─ app/mock_data/*.json
                                                    │
                                                    └─ LiveDataSource
                                                       └─ app/services/live/*.py
                                                          └─ Supabase, Vercel, etc.
```

### Data layer abstraction

The `app/services/data_source.py` module provides a unified interface:

- `get_data_source()` factory function returns `MockDataSource` or `LiveDataSource`
- Both implement the same interface: `get_overview()`, `get_users()`, etc.
- Routers call `data_source.method()` without knowing the mode

### Environment header

All API responses include an `X-Data-Mode` header:
- `mock` - Data from mock payloads
- `live` - Data from real providers

## Troubleshooting

### Mock works, live returns empty

- Check `DASHBOARD_DATA_MODE=live` in `.env`
- Verify provider credentials are set
- Check provider-specific feature flags are enabled
- Review backend logs for connection errors

### Feature enabled but env missing

- The endpoint will return 501 or empty payload with `notes[]`
- Check `.env.example` for required variables
- Ensure feature flag is set correctly

### CORS errors

- Verify `FRONTEND_URL` in `.env` matches your frontend origin
- Check CORS middleware configuration in `app/main.py`

### 401 Unauthorized

- Check API key configuration if using auth
- Verify in-memory auth credentials (mock mode uses any credentials)

## Testing

Run backend tests:

```bash
cd backend
uv run pytest
```

Run specific test suites:

```bash
uv run pytest -m "not integration"  # Unit tests only
uv run pytest tests/test_mock_mode.py  # Mock mode tests
uv run pytest tests/test_feature_flags.py  # Feature flag tests
```

### Template-specific tests

The template includes tests for mock mode and feature flags:

- `test_mock_mode.py` - Verifies all endpoints return valid mock data without external services
- `test_feature_flags.py` - Tests feature flag configuration and default values

To run with mock mode:

```bash
DASHBOARD_DATA_MODE=mock uv run pytest tests/test_mock_mode.py
```

## Development

Start the backend in development mode:

```bash
cd backend
uv sync
uv run python -m app.main
```

The API will be available at `http://localhost:8001`

API documentation: `http://localhost:8001/docs`

## Production

### Production Entry Point

**Production entry point**: `app.server:app`

The production entry point is defined in `backend/app/server.py` and uses the production-ready Uvicorn configuration with proper host binding and port handling.

**Development entry point**: `app.main:app`

The development entry point is defined in `backend/app/main.py` and includes additional debugging features like auto-reload.

### Deploy with Uvicorn

```bash
uvicorn app.server:app --host 0.0.0.0 --port $PORT
```

## Deployment

### Environment Variables

The backend supports two deployment configurations:

#### Minimum Configuration (Mock Mode)

For development and demos without external services:

```bash
# Required
API_KEY=your-secret-api-key
FRONTEND_URL=https://your-frontend.vercel.app

# Data mode
DASHBOARD_DATA_MODE=mock
```

#### Full Configuration (Live Mode)

For production with all integrations enabled:

```bash
# Required (same as minimum)
API_KEY=your-secret-api-key
FRONTEND_URL=https://your-frontend.vercel.app
DASHBOARD_BACKEND_HOST=127.0.0.1
DASHBOARD_BACKEND_PORT=8001
LOG_LEVEL=INFO

# Data mode
DASHBOARD_DATA_MODE=live

# Database (required for live mode)
FEATURE_SUPABASE=true
SUPABASE_URL_TEST=https://your-project.supabase.co
SUPABASE_ANON_KEY_TEST=your-anon-key
SUPABASE_SERVICE_ROLE_KEY_TEST=your-service-role-key
SUPABASE_URL_PROD=https://your-project.supabase.co
SUPABASE_ANON_KEY_PROD=your-anon-key
SUPABASE_SERVICE_ROLE_KEY_PROD=your-service-role-key

# Vercel integration (optional)
FEATURE_VERCEL=true
VERCEL_BASE_URL=https://vercel.com
VERCEL_API_TOKEN=your-vercel-token
VERCEL_TEAM_ID=your-team-id
VERCEL_TEAM_URL=your-team-url
VERCEL_PROJECT_ID_TEST=your-project-id
VERCEL_PROJECT_NAME_TEST=your-project-name
VERCEL_PROJECT_ID_PROD=your-project-id
VERCEL_PROJECT_NAME_PROD=your-project-name

# Hosting health (optional)
FEATURE_HOST_HEALTH=true
HOSTING_PROVIDER=render
RENDER_SERVICE_URL=https://your-service.onrender.com
RAILWAY_SERVICE_URL=https://your-service.railway.app
FLY_SERVICE_URL=https://your-service.fly.dev
CUSTOM_SERVICE_URL=https://your-custom-url.com
MAIN_API_URL_TEST=https://your-test-api.com
MAIN_API_URL_PROD=https://your-prod-api.com

# Costs module (optional)
FEATURE_COSTS_MODULE=true
COSTS_UNIT_PRICE=0.01
COSTS_UNIT_NAME=request
COSTS_CURRENCY=USD

# External providers (optional)
OPENROUTER_API_KEY=your-openrouter-key
DEEPGRAM_API_KEY=your-deepgram-key

# Authentication (optional)
DASHBOARD_ALLOWED_EMAILS=user@example.com,admin@example.com

# Feature flags
FEATURE_SUPABASE=true
FEATURE_VERCEL=false
FEATURE_HOST_HEALTH=false
FEATURE_STORAGE_METRICS=false
FEATURE_COSTS_MODULE=false
FEATURE_TEST_PROD_SWITCH=true
```

### Render Deployment

See `deploy/render.yaml` for a complete Render blueprint. The blueprint includes all environment variables with descriptions.

## Frontend Deployment

The frontend requires `VITE_DASHBOARD_API_URL` to be set to point to your backend API.

### Vercel

Set `VITE_DASHBOARD_API_URL` in Vercel project settings:
- Go to Project Settings → Environment Variables
- Add: `VITE_DASHBOARD_API_URL` = `https://your-backend.onrender.com`
- See `frontend/vercel.json` for build configuration

### Netlify

Set `VITE_DASHBOARD_API_URL` in Netlify site settings:
- Go to Site Settings → Environment Variables
- Add: `VITE_DASHBOARD_API_URL` = `https://your-backend.onrender.com`
- See `deploy/netlify.toml` for build configuration

### Cloudflare Pages

Set `VITE_DASHBOARD_API_URL` in Cloudflare Pages dashboard:
- Go to Pages → Your Project → Settings → Environment Variables
- Add: `VITE_DASHBOARD_API_URL` = `https://your-backend.onrender.com`
- See `deploy/cloudflare-pages.md` for deployment instructions

**Note:** All platforms automatically expose environment variables prefixed with `VITE_` to the frontend build process.

## Production

Production entry point: `app.server:app`

Deploy with:
```bash
uvicorn app.server:app --host 0.0.0.0 --port $PORT
```

See `deploy/` folder for provider-specific deployment configs.
