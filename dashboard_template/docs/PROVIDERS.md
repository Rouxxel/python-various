# Provider Setup Guide

Configuration instructions for each supported provider.

> **Read first:** [EXTENDING_PROVIDERS.md](./EXTENDING_PROVIDERS.md) explains what is **scaffolded** (env vars, flags, UI) vs what **you implement** (API/DB clients in `services/live/`). Supabase and Vercel sections below describe configuration; live API calls are your responsibility unless you copy implementations from your product codebase.

## Datadog (extension — not built-in)

Use Datadog when metrics and logs already live in Datadog and you want SRE-style panels in this dashboard.

1. Add `DATADOG_API_KEY`, `DATADOG_APP_KEY`, and `DATADOG_SITE` to backend env (never frontend).
2. Implement `app/services/providers/datadog.py` using Datadog HTTP API.
3. Add `FEATURE_DATADOG` to `config.py` and wire an infrastructure or ops endpoint.
4. Full walkthrough: [EXTENDING_PROVIDERS.md](./EXTENDING_PROVIDERS.md#pattern-d--datadog-metrics-logs-apm).

## Private databases (PostgreSQL / MySQL on VPS or VPN)

The template does **not** require Supabase. For a database on a private server:

1. Set `DATABASE_URL` (SQLAlchemy/psycopg connection string) on the **dashboard backend only**.
2. Ensure network path: backend container/VM → DB (VPC, VPN, or firewall rule).
3. Implement queries in `app/services/live/placeholder_analytics.py` (or split modules).
4. Set `FEATURE_SUPABASE=false` if you are not using Supabase at all.
5. Full walkthrough: [EXTENDING_PROVIDERS.md](./EXTENDING_PROVIDERS.md#pattern-b--private-postgresql--mysql-vps-lan-vpn).

## Hosting Providers

### Render

Render is a popular hosting platform with a free tier that spins down after inactivity.

#### Wake Limitations

- **Free tier spin-down**: Services spin down after 15 minutes of inactivity
- **Wake time**: First request after spin-down may take 30-60 seconds
- **Wake endpoint**: Use the wake button in Infrastructure page to wake the service
- **Limitations**: Wake only works if the service URL is accessible

#### Setup

1. **Create a Render service**
   - Go to [render.com](https://render.com)
   - Create a new web service
   - Deploy your backend

2. **Configure backend**
   ```bash
   # In backend/.env
   HOSTING_PROVIDER=render
   MAIN_API_URL_TEST=https://your-service.onrender.com
   MAIN_API_URL_PROD=https://your-service.onrender.com
   FEATURE_HOST_HEALTH=true
   ```

3. **Wake button**
   - The Infrastructure page includes a wake button
   - Click to wake the service before it spins down
   - Monitor response time to confirm wake success

### Railway

Railway is a platform for deploying applications with built-in databases.

#### Wake Limitations

- Railway services generally stay awake (no free tier spin-down)
- Wake button may still be used for health checks
- Response times are typically faster than Render free tier

#### Setup

1. **Create a Railway service**
   - Go to [railway.app](https://railway.app)
   - Create a new project
   - Deploy your backend

2. **Configure backend**
   ```bash
   # In backend/.env
   HOSTING_PROVIDER=railway
   MAIN_API_URL_TEST=https://your-service.railway.app
   MAIN_API_URL_PROD=https://your-service.railway.app
   FEATURE_HOST_HEALTH=true
   ```

### Custom/Other

For custom hosting providers, use the generic hosting service.

#### Setup

```bash
# In backend/.env
HOSTING_PROVIDER=custom
MAIN_API_URL_TEST=https://your-custom-url.com
MAIN_API_URL_PROD=https://your-custom-url.com
FEATURE_HOST_HEALTH=true
```

The generic service performs simple HTTP health checks.

### Railway Deployment

Railway provides a deployment configuration in `deploy/railway.toml`.

#### Setup

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize Railway project**
   ```bash
   cd dashboard_template/backend
   railway init
   railway up
   ```

3. **Configure environment variables**
   - Set required variables in Railway dashboard
   - See `deploy/railway.toml` for the complete list

#### Environment Variables

**Minimum (mock mode):**
- `API_KEY` - Secret API key
- `FRONTEND_URL` - Frontend URL for CORS

**Full (live mode):**
- All minimum vars above
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `VERCEL_PROJECT_ID` - Vercel project ID (optional)
- `VERCEL_TOKEN` - Vercel API token (optional)
- `COSTS_UNIT_PRICE` - Price per unit (optional)
- `COSTS_UNIT_NAME` - Unit name (optional)

### Fly.io (Community-Contributed)

Fly.io provides a deployment configuration in `deploy/fly.toml`. This is a community-contributed stub configuration.

**Note:** Fly.io support is maintained by the community. Please test thoroughly and contribute improvements.

#### Setup

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Launch app**
   ```bash
   cd dashboard_template/backend
   fly launch
   fly deploy
   ```

3. **Configure environment variables**
   ```bash
   fly secrets set API_KEY=your-key FRONTEND_URL=your-url
   ```

#### Environment Variables

**Minimum (mock mode):**
- `API_KEY` - Secret API key
- `FRONTEND_URL` - Frontend URL for CORS

**Full (live mode):**
- All minimum vars above
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `VERCEL_PROJECT_ID` - Vercel project ID (optional)
- `VERCEL_TOKEN` - Vercel API token (optional)
- `COSTS_UNIT_PRICE` - Price per unit (optional)
- `COSTS_UNIT_NAME` - Unit name (optional)

## Docker (Local Development)

Docker provides a containerized development environment for local development and testing.

### Setup

1. **Build and start services**
   ```bash
   cd backend
   cp .env.example .env   # if needed
   docker compose up -d
   ```

2. **View logs**
   ```bash
   cd backend
   docker compose logs -f backend
   ```

3. **Stop services**
   ```bash
   cd backend
   docker compose down
   ```

### Environment Variables

Configure environment variables in `backend/docker-compose.yml` or use `backend/.env`:

**Minimum (mock mode):**
- `API_KEY` - Secret API key
- `FRONTEND_URL` - Frontend URL for CORS

**Full (live mode):**
- All minimum vars above
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `VERCEL_PROJECT_ID` - Vercel project ID (optional)
- `VERCEL_TOKEN` - Vercel API token (optional)
- `COSTS_UNIT_PRICE` - Price per unit (optional)
- `COSTS_UNIT_NAME` - Unit name (optional)

### Services

The `backend/docker-compose.yml` includes:

- **backend**: Python FastAPI backend on port 8001

### Development Workflow

For development with hot-reload, mount the backend directory as a volume (already configured in `backend/docker-compose.yml`).

## Supabase (Database + Storage)

Supabase provides the database and storage backend for live data mode.

### Setup

1. **Create a Supabase project**
   - Go to [supabase.com](https://supabase.com)
   - Create a new project
   - Wait for database to be ready

2. **Get credentials**
   - Project URL: Settings → API → Project URL
   - Service role key: Settings → API → service_role (secret)

3. **Configure backend**
   ```bash
   # In backend/.env
   FEATURE_SUPABASE=true
   SUPABASE_URL=your-project-url
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```

4. **Create tables** (if starting from scratch)
   - Use Supabase SQL Editor
   - See backend service files for expected table schemas
   - Example: `users`, `events`, `sessions`

### What it provides (when you implement live builders)

- Database queries for analytics pages
- Storage bucket metrics (optional)
- Table row counts on Infrastructure page

**Note:** Env vars and feature flags are ready; add `supabase-py` or PostgREST calls in `services/live/` — see [EXTENDING_PROVIDERS.md](./EXTENDING_PROVIDERS.md).

### Troubleshooting

- **Connection refused**: Check URL and key are correct
- **Permission denied**: Use service_role key, not anon key
- **Table not found**: Create tables in Supabase first

## Vercel (Deployments + Web Analytics)

Vercel provides deployment history and web analytics data.

### Setup

1. **Get project ID**
   - Go to Vercel dashboard
   - Select your project
   - Copy Project ID from Settings → General

2. **Create access token**
   - Go to Settings → Tokens
   - Create new token
   - Copy the token

3. **Configure backend**
   ```bash
   # In backend/.env
   FEATURE_VERCEL=true
   VERCEL_PROJECT_ID=your-project-id
   VERCEL_TOKEN=your-access-token
   VERCEL_TEAM_ID=your-team-id  # optional, for team accounts
   ```

### What it provides (when you implement live builders)

- Deployment history (Vercel REST API)
- Web analytics (Vercel Analytics API — plan-dependent)
- Project metadata

**Note:** Configure tokens below, then implement API calls in `services/providers/vercel.py` — see [EXTENDING_PROVIDERS.md](./EXTENDING_PROVIDERS.md).

### Troubleshooting

- **401 Unauthorized**: Check token is valid and has correct permissions
- **Project not found**: Verify project ID is correct
- **Rate limited**: Vercel API has rate limits

## Render (Backend Hosting + Health)

Render provides backend hosting and wake/sleep functionality for free tier.

### Setup

1. **Deploy backend to Render**
   - Connect your GitHub repo to Render
   - Use `deploy/render.yaml` as blueprint
   - Set environment variables in Render dashboard

2. **Get service URL**
   - After deployment, copy the service URL
   - Example: `https://your-backend.onrender.com`

3. **Configure backend**
   ```bash
   # In backend/.env
   FEATURE_HOST_HEALTH=true
   HOSTING_PROVIDER=render
   RENDER_SERVICE_URL=https://your-backend.onrender.com
   ```

### What it provides

- Health check status
- Wake/sleep functionality (for free tier spin-down)
- Deployment status
- Service metrics

### Free tier notes

- Render free tier spins down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds
- Use wake endpoint to proactively wake the service

### Troubleshooting

- **Service always sleeping**: Upgrade to paid tier or use wake endpoint
- **Health check failing**: Check service logs for errors
- **Wake not working**: Verify service URL is correct

## Railway (Backend Hosting + Health)

Railway provides alternative backend hosting with similar functionality.

### Setup

1. **Deploy backend to Railway**
   ```bash
   railway login
   railway init
   railway up
   ```

2. **Get service URL**
   - Railway dashboard → your service → URL
   - Example: `https://your-backend.up.railway.app`

3. **Configure backend**
   ```bash
   # In backend/.env
   FEATURE_HOST_HEALTH=true
   HOSTING_PROVIDER=railway
   RAILWAY_SERVICE_URL=https://your-backend.up.railway.app
   ```

### What it provides

- Health check status
- Wake functionality
- Deployment status
- Service metrics

### Troubleshooting

- **Connection refused**: Check service URL is correct
- **Service not starting**: Check Railway logs for errors
- **Wake not working**: Verify Railway service is accessible

## Fly.io (Backend Hosting - Stub)

Fly.io is an alternative hosting provider. Currently a stub in the template.

### Setup

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy**
   ```bash
   fly launch
   fly deploy
   ```

3. **Configure backend**
   ```bash
   # In backend/.env
   FEATURE_HOST_HEALTH=true
   HOSTING_PROVIDER=fly
   FLY_SERVICE_URL=https://your-app.fly.dev
   ```

### Status

Community-contributed optional. See `deploy/fly.toml` for configuration stub.

## Generic hosting (Custom URL)

For custom hosting solutions or self-hosted backends.

### Setup

1. **Configure backend**
   ```bash
   # In backend/.env
   FEATURE_HOST_HEALTH=true
   HOSTING_PROVIDER=custom
   CUSTOM_SERVICE_URL=https://your-backend.example.com
   ```

### What it provides

- Basic health check via HTTP ping
- No provider-specific features

## Costs Module (Third-party pricing)

Optional cost tracking for external services (e.g., ElevenLabs, OpenAI).

### Generic pricing

```bash
# In backend/.env
FEATURE_COSTS_MODULE=true
COSTS_UNIT_PRICE=0.01
COSTS_UNIT_NAME="API call"
COSTS_CURRENCY="USD"
```

### ElevenLabs (example)

```bash
ELEVENLABS_API_KEY=your-api-key
ELEVENLABS_CHARACTER_COST=0.00015  # per character
```

### What it provides

- Cost tracking and projections
- Unit economics calculations
- Provider-specific pricing models

## Frontend hosting (Vercel / Netlify / Cloudflare Pages)

### Vercel (recommended)

```bash
cd frontend
npm run build
vercel deploy
```

Set `VITE_DASHBOARD_API_URL` to your backend URL.

### Netlify

```bash
cd frontend
npm run build
netlify deploy --prod
```

Add environment variable in Netlify dashboard.

### Cloudflare Pages

```bash
cd frontend
npm run build
wrangler pages publish dist
```

## Environment variable reference

### Required for all modes

```bash
API_KEY=your-secret-key
FRONTEND_URL=http://localhost:5173
```

### Database (Supabase)

```bash
FEATURE_SUPABASE=true
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Vercel

```bash
FEATURE_VERCEL=true
VERCEL_PROJECT_ID=your-project-id
VERCEL_TOKEN=your-access-token
VERCEL_TEAM_ID=your-team-id  # optional
```

### Hosting health

```bash
FEATURE_HOST_HEALTH=true
HOSTING_PROVIDER=render  # or railway, fly, custom
RENDER_SERVICE_URL=https://your-backend.onrender.com
RAILWAY_SERVICE_URL=https://your-backend.up.railway.app
FLY_SERVICE_URL=https://your-app.fly.dev
CUSTOM_SERVICE_URL=https://your-backend.example.com
```

### Costs

```bash
FEATURE_COSTS_MODULE=true
COSTS_UNIT_PRICE=0.01
COSTS_UNIT_NAME="API call"
COSTS_CURRENCY="USD"
```

### Data mode

```bash
DASHBOARD_DATA_MODE=mock  # or live
```

## Security best practices

- Never commit `.env` files to version control
- Use service role keys only on backend, never frontend
- Rotate API keys regularly
- Use different keys for test and production
- Limit API key permissions to minimum required
