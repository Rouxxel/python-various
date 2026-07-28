# Analytics Dashboard Template

A reusable, provider-agnostic analytics dashboard template with mock data, optional integrations, and placeholder UI patterns. Clone this template, enable the integrations you need, replace placeholders with real data, and have a working dashboard in hours — not weeks.

## Use this template

### GitHub Template

Click the **"Use this template"** button above to create a new repository from this template.

### Manual Clone

```bash
git clone https://github.com/your-username/analytics-dashboard-template.git my-dashboard
cd my-dashboard
```

### Quick Start with degit (one-liner)

```bash
npx degit your-username/analytics-dashboard-template my-dashboard
cd my-dashboard
```

## Using this as a template

1. **Clone or use this template**
   ```bash
   git clone <your-repo-url> my-dashboard
   cd my-dashboard
   ```

2. **Configure the project**
   - Edit `frontend/template.config.ts` (project name, navigation)
   - Copy `backend/.env.example` to `backend/.env` and set required variables
   - Copy `frontend/.env.example` to `frontend/.env` and set `VITE_DASHBOARD_API_URL`

3. **Run with mock data** (zero external services required)
   ```bash
   # Terminal 1 — backend
   cd backend && uv sync && uv run python -m app.main

   # Terminal 2 — frontend
   cd frontend && npm install && npm run dev
   ```

   Open http://localhost:5173 — backend API at http://localhost:8001

4. **Verify provider config** (before enabling live mode)
   ```bash
   scripts/check-providers.ps1   # Windows
   scripts/check-providers.sh    # macOS/Linux
   ```

5. **Enable live data** (when ready)
   - Set `DASHBOARD_DATA_MODE=live` in `backend/.env`
   - Configure provider credentials (Supabase, Vercel, etc.)
   - Extend placeholders in `backend/app/services/providers/` and `services/live/`

## Feature matrix

### Feature flags (backend)

Configure in `backend/.env` — exposed to the frontend via `GET /api/config/features`:

| Feature Flag | Default | Description |
|-------------|---------|-------------|
| `FEATURE_SUPABASE` | `true` | Show database/storage sections; **you** wire Supabase queries in live mode |
| `FEATURE_VERCEL` | `false` | Show deployments/analytics sections; **you** wire Vercel API in live mode |
| `FEATURE_HOST_HEALTH` | `false` | Host health + wake UI; uses `services/hosting/` helpers |
| `FEATURE_STORAGE_METRICS` | `false` | Storage bucket metrics (intended for Supabase) |
| `FEATURE_COSTS_MODULE` | `false` | Costs page and `/api/costs` |
| `FEATURE_TEST_PROD_SWITCH` | `true` | Test/prod environment switcher in the UI |
| `FEATURE_DATADOG` | `false` | Datadog metrics extension (placeholder client in repo) |
| `FEATURE_PRIVATE_DATABASE` | `false` | Private Postgres/MySQL via `DATABASE_URL` |

### Page availability (mock vs live)

This table describes **whether each page renders** in mock mode or after you implement live builders — **not** that each SaaS vendor powers every page automatically.

| Page | Mock mode (default) | Live mode (after you implement builders) |
|------|---------------------|------------------------------------------|
| Overview, Metrics, Charts, Tables | ✅ mock JSON | ✅ your DB/API queries |
| Infrastructure | ✅ mock + setup `notes[]` | ✅ optional Vercel, Supabase, host health |
| Users, Activity, Sessions, AI, Costs | ✅ mock JSON | ✅ your domain queries |
| Test/Prod switch | ✅ UI (if flag on) | ✅ uses `SUPABASE_*` / `VERCEL_*` per env |

**Third-party integrations (Datadog, private Postgres on a VPS, etc.):** not built-in — see [docs/EXTENDING_PROVIDERS.md](docs/EXTENDING_PROVIDERS.md).

### Provider integration status (honest summary)

| Provider | Env / flags in template | Turnkey live API client in repo |
|----------|-------------------------|----------------------------------|
| Mock data | ✅ | ✅ |
| Supabase | ✅ | ⚠️ connection check + optional table counts (`uv sync --extra supabase`) |
| Vercel | ✅ | ⚠️ deployments fetch when token set |
| Render / Railway / custom host | ✅ | ⚠️ health/wake helpers |
| Datadog | ✅ | ⚠️ validate + query placeholders |
| Private PostgreSQL/MySQL | ✅ | ⚠️ connection check (`uv sync --extra database`) |

## Customization entry points

- **`frontend/template.config.ts`**: Project name and navigation
- **`frontend/package.json`**: Frontend dependencies and scripts
- **`backend/.env.example`**: Environment variables and feature flags
- **`backend/app/services/live/`**: Replace placeholder data builders with your queries
- **`frontend/src/lib/metricDescriptions.ts`**: Customize metric help text

## What you must replace vs what works out of the box

### Works out of the box (mock mode)
- All UI components and layouts
- Mock data for every page
- Navigation and routing
- Authentication (in-memory, suitable for internal dashboards)
- Responsive design and theming

### You must replace (for live data)
- Backend data builders in `app/services/live/` (connect to your database)
- Environment variables in `.env` (your credentials)
- Metric descriptions in `metricDescriptions.ts` (your business logic)
- Optional: Navigation items (remove showcase routes, add your pages)

## Template versioning

Template version: `1.0.0` (see `CHANGELOG.md` for release notes)

When upgrading to a new template version:
1. Check `CHANGELOG.md` for breaking changes
2. Backup your custom data builders
3. Merge template updates carefully
4. Test your custom integrations

## Documentation

- **[Implementation Plan](DASHBOARD_TEMPLATE_PLAN.md)** - Phase-by-phase template development
- **[Customization Guide](docs/CUSTOMIZATION.md)** - End-to-end fork this template for your app
- **[Provider Setup](docs/PROVIDERS.md)** - Render, Railway, Vercel, Supabase, Docker setup
- **[Extending Providers](docs/EXTENDING_PROVIDERS.md)** - Datadog, private databases, custom APIs
- **[Testing Guide](docs/TESTING.md)** - Testing procedures and quality checks
- **[Routes Documentation](docs/ROUTES.md)** - Routing structure and how to add pages
- **[Mock Data](docs/MOCK_DATA.md)** - Structure of mock payloads and how to extend
- **[Architecture](docs/ARCHITECTURE.md)** - Diagrams, data flow, auth, environment header

## Project structure

```
.
├── backend/                 # FastAPI backend with mock/live data modes
│   ├── app/
│   │   ├── services/       # Data layer (mock + live providers)
│   │   ├── routers/        # API endpoints
│   │   ├── tools/          # CLI utilities (print_features)
│   │   └── config.py       # Feature flags and settings
│   ├── tests/              # Backend tests
│   ├── Dockerfile          # Container image
│   ├── docker-compose.yml  # Local backend via Docker
│   ├── .dockerignore
│   └── README.md           # Backend documentation
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── routes/         # Page components
│   │   ├── lib/            # Utilities, config, types
│   │   └── hooks/          # Custom React hooks
│   ├── vercel.json         # Vercel deployment config
│   └── README.md           # Frontend documentation
├── docs/                   # Supplementary documentation
│   ├── CUSTOMIZATION.md    # Forking guide
│   ├── PROVIDERS.md        # Provider setup instructions
│   ├── TESTING.md          # Testing procedures
│   ├── ROUTES.md           # Routing documentation
│   ├── MOCK_DATA.md        # Mock data structure
│   └── ARCHITECTURE.md     # System architecture
├── deploy/                 # Deployment configs
│   ├── render.yaml         # Render blueprint
│   ├── railway.toml        # Railway configuration
│   ├── fly.toml            # Fly.io configuration
│   ├── netlify.toml        # Netlify configuration
│   └── cloudflare-pages.md # Cloudflare Pages guide
├── scripts/                # Utility scripts
│   └── type_check.py       # Type safety checker
├── DASHBOARD_TEMPLATE_PLAN.md  # Implementation plan
└── README.md               # This file
```

## Quick start (mock mode)

### Windows (PowerShell)

```powershell
# Terminal 1: Backend
cd backend
uv sync
uv run python -m app.main

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

### macOS / Linux

```bash
# Terminal 1: Backend
cd backend
uv sync
uv run python -m app.main

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` and login with any credentials (mock auth).

## Mock vs Live Mode

The template supports two data modes:

- **Mock mode** (default): Uses structured mock data from the backend. No external services required. Perfect for development, UI testing, and demos.
- **Live mode**: Queries real data from your providers (Supabase, Vercel, etc.). Requires provider credentials and configuration. Use for production dashboards.

Switch modes by setting `DASHBOARD_DATA_MODE=mock` or `DASHBOARD_DATA_MODE=live` in `backend/.env`.

## Test/Prod Switch

The template includes an optional test/prod environment switcher (controlled by `FEATURE_TEST_PROD_SWITCH`). When enabled, users can toggle between test and production environments in the UI. This is useful for comparing data across environments without redeploying.

## Deployment

### Backend Deployment

**Render** (recommended):
- See `deploy/render.yaml` for a complete blueprint
- Set environment variables in Render dashboard
- Deploy automatically on push

**Railway**:
- See `deploy/railway.toml` for configuration
- Use Railway CLI: `railway up`

**Docker**:
- See `backend/docker-compose.yml` for local backend via Docker
- See `backend/Dockerfile` for container configuration

### Frontend Deployment

**Vercel** (recommended):
- See `frontend/vercel.json` for build configuration
- Set `VITE_DASHBOARD_API_URL` to your backend URL
- Deploy automatically on push

**Netlify**:
- See `deploy/netlify.toml` for configuration
- Set `VITE_DASHBOARD_API_URL` in site settings

**Cloudflare Pages**:
- See `deploy/cloudflare-pages.md` for instructions
- Set `VITE_DASHBOARD_API_URL` in Pages settings

## License

See [LICENSE](LICENSE) file for details.
