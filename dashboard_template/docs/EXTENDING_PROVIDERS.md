# Extending Providers (Datadog, private databases, and others)

The template is designed so **you add provider clients in the backend service layer**, not in React routes. Feature flags and env vars tell the UI what sections to show; **your code** in `backend/app/services/` performs the actual API or database calls.

This guide covers providers that are **not shipped as turnkey integrations** but are straightforward to add using the same patterns as Supabase and Vercel.

---

## What is wired today vs what you implement

| Provider | Config / flags | Live client in repo | What you do for live data |
|----------|----------------|---------------------|---------------------------|
| **Mock data** | `DASHBOARD_DATA_MODE=mock` | Yes | Nothing — works out of the box |
| **Supabase** | `FEATURE_SUPABASE`, `SUPABASE_*` | Env + flags only | Query PostgREST or `supabase-py` in `services/live/` |
| **Vercel** | `FEATURE_VERCEL`, `VERCEL_*` | Env + flags only | Call Vercel REST API in `services/live/` or `services/providers/vercel.py` |
| **Render / Railway / custom host** | `FEATURE_HOST_HEALTH`, `HOSTING_PROVIDER`, `*_SERVICE_URL` | Partial — `services/hosting/` health/wake helpers | Wire wake route + call hosting service from infrastructure builder |
| **Costs (generic / ElevenLabs)** | `FEATURE_COSTS_MODULE` | Partial — `services/costs/` | Connect pricing APIs or DB usage tables |
| **Datadog** | `FEATURE_DATADOG`, `DATADOG_*` | Placeholder client | Extend `services/providers/datadog.py` |
| **Private DB** | `FEATURE_PRIVATE_DATABASE`, `DATABASE_URL` | Placeholder client | Extend `services/providers/database.py` |
| **Private API on VPN/VPS** | `MAIN_API_URL_*`, `CUSTOM_SERVICE_URL` | Generic HTTP health only | Query your API from placeholder builders |

**Important:** `DASHBOARD_DATA_MODE=live` currently delegates to `placeholder_analytics.py`, which returns empty/zero data until **you** replace the builders. The template gives you structure, flags, UI, and deploy configs — not production-ready provider SDK calls for every vendor.

---

## Connection patterns (choose one per data source)

### Pattern A — Managed Postgres (Supabase)

Best when: you already use Supabase or want hosted Postgres + auth + storage.

```bash
DASHBOARD_DATA_MODE=live
FEATURE_SUPABASE=true
SUPABASE_URL_TEST=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY_TEST=...
```

In `services/live/your_analytics.py`:

```python
from supabase import create_client
from app.config import settings

def _client(env: str):
    creds = settings.credentials_for(env)
    return create_client(creds.supabase_url, creds.supabase_service_role_key)
```

Use the **service role key only on the backend**, never in the frontend.

### Pattern B — Private PostgreSQL / MySQL (VPS, LAN, VPN)

Best when: database runs on a private server, homelab, or cloud VM without Supabase.

1. **Add dependency** (example PostgreSQL):

   ```bash
   # pyproject.toml or requirements.txt
   sqlalchemy>=2.0
   psycopg[binary]>=3.1
   ```

2. **Add env vars** to `backend/.env`:

   ```bash
   DATABASE_URL=postgresql+psycopg://user:pass@10.0.0.5:5432/analytics
   # Optional read replica
   DATABASE_URL_READ=postgresql+psycopg://readonly:pass@10.0.0.5:5432/analytics
   ```

3. **Network access**

   - Dashboard backend must reach the DB (same VPC, VPN, SSH tunnel, or firewall allowlist).
   - Do **not** expose the database to the public internet for dashboard queries.
   - Run the backend close to the DB (same private network) when possible.

4. **Implement queries** in `services/live/placeholder_analytics.py` (or split into `services/live/users.py`, etc.):

   ```python
   from sqlalchemy import create_engine, text
   import os

   engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

   def build_users(from_date, to_date):
       with engine.connect() as conn:
           row = conn.execute(
               text("SELECT COUNT(*) FROM users WHERE created_at BETWEEN :a AND :b"),
               {"a": from_date, "b": to_date},
           ).one()
       return {"total_users": row[0], ...}
   ```

5. **Infrastructure page — database section**

   - Either query `information_schema.tables` / `pg_stat_user_tables` for row counts, or
   - Keep Supabase section off (`FEATURE_SUPABASE=false`) and add a custom section in the infrastructure builder.

### Pattern C — Vercel (frontend hosting + analytics + deployments)

Best when: your product frontend is on Vercel.

```bash
FEATURE_VERCEL=true
VERCEL_API_TOKEN=...
VERCEL_PROJECT_ID_TEST=prj_...
VERCEL_PROJECT_ID_PROD=prj_...
```

Create `backend/app/services/providers/vercel.py`:

- Deployments: `GET https://api.vercel.com/v6/deployments?projectId=...`
- Web Analytics: Vercel Analytics API (see current Vercel docs for the endpoint your plan supports)

Call from `build_infrastructure()` when `settings.feature_vercel` is true. Return empty list + `notes[]` when disabled or on API error (never crash the dashboard).

**Frontend deploy:** set `VITE_DASHBOARD_API_URL` in Vercel project settings; see `frontend/vercel.json` and `deploy/vercel-frontend.md`.

### Pattern D — Datadog (metrics, logs, APM)

Best when: you already instrument services with Datadog and want infra/SRE panels in the dashboard.

Datadog is **not** a first-class flag in the template. Add it as an optional module:

1. **Env vars**

   ```bash
   FEATURE_DATADOG=false          # add to config.py when you implement
   DATADOG_API_KEY=...
   DATADOG_APP_KEY=...            # required for many read endpoints
   DATADOG_SITE=datadoghq.com     # or datadoghq.eu, us3.datadoghq.com, etc.
   ```

2. **Create** `backend/app/services/providers/datadog.py`

   ```python
   import httpx
   from app.config import settings

   BASE = f"https://api.{settings.datadog_site}/api/v1"

   async def query_metrics(query: str, from_ts: int, to_ts: int) -> dict:
       if not settings.datadog_api_key:
           return {"series": [], "notes": ["Datadog not configured"]}
       async with httpx.AsyncClient() as client:
           r = await client.get(
               f"{BASE}/query",
               params={"query": query, "from": from_ts, "to": to_ts},
               headers={
                   "DD-API-KEY": settings.datadog_api_key,
                   "DD-APPLICATION-KEY": settings.datadog_app_key,
               },
           )
           r.raise_for_status()
           return r.json()
   ```

3. **Expose in UI**

   - Add a feature flag `feature_datadog` in `config.py` and `GET /api/config/features`.
   - Add an infrastructure subsection or a dedicated `/metrics-ops` page that calls your Datadog-backed endpoint.
   - Follow the `notes[]` pattern when API keys are missing.

4. **Security**

   - Datadog keys stay on the backend only.
   - Scope API keys to read-only metrics/logs.

### Pattern E — Private HTTP API (custom backend on a server)

Best when: metrics live in **your** REST API on a VPS, not in a SaaS analytics product.

```bash
MAIN_API_URL_TEST=https://api-staging.internal.example.com
MAIN_API_URL_PROD=https://api.internal.example.com
FEATURE_HOST_HEALTH=true
HOSTING_PROVIDER=custom
CUSTOM_SERVICE_URL=https://api.internal.example.com/health
```

In live builders, use `httpx` to call your internal endpoints (with API key or mTLS). The dashboard backend acts as a **BFF** (backend-for-frontend) so the browser never holds internal credentials.

---

## Checklist: add any new provider

1. Add env vars to `backend/.env.example` (commented, with `# FEATURE_*`).
2. Add boolean flag to `app/config.py` and expose via `GET /api/config/features`.
3. Implement client in `app/services/providers/<name>.py`.
4. Call client from `app/services/live/*` builders (never from routers directly).
5. Return `notes[]` when disabled or misconfigured.
6. Document in `docs/PROVIDERS.md` (or this file).
7. Optional: add infrastructure section in `frontend/src/lib/infrastructureConfig.ts`.

---

## Deploying backend + frontend with providers

| Layer | Typical host | Connects to |
|-------|--------------|-------------|
| Frontend | Vercel, Netlify, Cloudflare Pages | Public backend URL via `VITE_DASHBOARD_API_URL` |
| Dashboard backend | Render, Railway, Fly, Docker on VPS | Private DB, Datadog, Vercel API, your internal APIs |
| Database | Supabase cloud, or Postgres on private server | Only from backend (never from browser) |

See `deploy/` for Render, Railway, Fly, Netlify, and Vercel frontend notes.

---

## Related docs

- [PROVIDERS.md](./PROVIDERS.md) — step-by-step for Supabase, Vercel, Render, Railway
- [CUSTOMIZATION.md](./CUSTOMIZATION.md) — fork workflow and replacing placeholder builders
- [MOCK_DATA.md](./MOCK_DATA.md) — mock payloads while providers are not wired
