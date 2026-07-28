# Architecture

System design, data flow, authentication, and environment handling.

## High-level architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + TypeScript + TanStack Router + Recharts             │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST
                     │
┌────────────────────▼────────────────────────────────────────┐
│                         Backend                              │
│  FastAPI + Pydantic + Uvicorn                              │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │ Supabase│ │ Vercel  │ │ Custom  │
    │ (DB)    │ │ (API)   │ │ (API)   │
    └─────────┘ └─────────┘ └─────────┘
```

## Data flow

### Request flow

```
User Action → Frontend Component → API Client → Backend Router → Data Source → Provider
                                                                                      │
                                                                                      ▼
                                                                                 Response
                                                                                      │
                                                                                      ▼
                                                                              Frontend UI Update
```

### Detailed flow

1. **User action** (click, navigation, date change)
2. **Frontend component** calls query hook
3. **Query hook** calls API client function
4. **API client** makes HTTP request to backend
5. **Backend router** validates request
6. **Data source** (mock or live) fetches data
7. **Provider** (Supabase, Vercel, etc.) returns data
8. **Backend** returns JSON response
9. **Frontend** updates UI with new data

### Example: Overview page load

```
1. User navigates to /overview
2. TanStack Router loads OverviewPage component
3. Component calls useQuery(['overview', from, to])
4. Query calls fetchOverview(from, to)
5. Fetch makes GET /api/overview?from_date=X&to_date=Y
6. Backend router receives request
7. Router calls data_source.get_overview(from, to)
8. If mock: loads from backend/app/mock_data/overview.json
9. If live: queries Supabase via analytics_data.build_overview()
10. Backend returns JSON with X-Data-Mode header
11. Frontend receives response and updates state
12. Component re-renders with new data
```

## Backend architecture

### Directory structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── server.py            # Production entry point
│   ├── config.py            # Settings and feature flags
│   ├── models/              # Pydantic models
│   ├── routers/             # API endpoints
│   ├── services/            # Business logic
│   │   ├── data_source.py   # Mock/Live factory
│   │   ├── live/            # Live data builders
│   │   └── mock_data/       # Mock JSON files
│   └── middleware/          # CORS, auth, etc.
└── tests/                   # Test suite
```

### Layer responsibilities

**Routers** (`app/routers/`):
- Define API endpoints
- Validate request parameters
- Call data source methods
- Return responses

**Data source** (`app/services/data_source.py`):
- Factory pattern for mock/live mode
- Unified interface for data access
- Abstracts provider details

**Live services** (`app/services/live/`):
- Implement actual data queries
- Call provider APIs (Supabase, Vercel)
- Transform provider data to internal models

**Mock data** (`app/mock_data/`):
- JSON files matching Pydantic models
- Structured for realistic scenarios
- Zero external dependencies

### Request processing

```
Request → Middleware (CORS, auth) → Router → Pydantic validation → Data source → Provider
                                                                                    │
                                                                                    ▼
                                                                              Response
```

### Middleware

**CORS**:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Auth** (in-memory):
```python
# Simple API key validation
if request.headers.get("X-API-Key") != settings.api_key:
    raise HTTPException(401)
```

**Environment header**:
```python
@app.middleware("http")
async def add_data_mode_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Data-Mode"] = settings.dashboard_data_mode
    return response
```

## Frontend architecture

### Directory structure

```
frontend/
├── src/
│   ├── main.tsx             # React entry point
│   ├── routes/              # Page components
│   ├── components/          # Reusable UI
│   │   └── dashboard/       # Dashboard-specific components
│   ├── lib/                 # Utilities
│   │   ├── api.ts           # API client
│   │   ├── types.ts         # TypeScript types
│   │   ├── mock-data.ts     # Frontend mock data
│   │   └── templateConfig.ts # Configuration
│   ├── hooks/               # Custom React hooks
│   └── styles/              # Global styles
└── public/                  # Static assets
```

### Component hierarchy

```
App
├── Sidebar (navigation)
├── TopBar (environment switcher, user menu)
└── Content Area
    └── Route Components
        ├── PageHeader
        ├── MetricSection
        │   ├── KpiGroupSection
        │   │   └── KpiCard
        │   └── ChartCard
        └── DataTable
```

### State management

**React Query** (TanStack Query):
- Server state (API responses)
- Caching and refetching
- Loading and error states

**React state**:
- UI state (modals, dropdowns)
- Form inputs
- Local component state

**URL state**:
- Date range (query params)
- Environment (test/prod)
- Route parameters

### Data fetching pattern

```typescript
// Query hook
const { data, isLoading, error } = useQuery({
    queryKey: ['overview', from, to],
    queryFn: () => fetchOverview(from, to),
    enabled: features.overview  // Feature flag
})

// API client
export async function fetchOverview(from: string, to: string) {
    const response = await fetch(`${API_URL}/api/overview?from_date=${from}&to_date=${to}`)
    if (!response.ok) throw new Error('Failed to fetch')
    return response.json()
}
```

## Authentication

### Current implementation (in-memory)

The template uses simple in-memory authentication suitable for internal dashboards:

**Backend**:
```python
# In middleware
api_key = request.headers.get("X-API-Key")
if api_key != settings.api_key:
    raise HTTPException(status_code=401, detail="Invalid API key")
```

**Frontend**:
```typescript
// In useAuth.tsx
const login = (credentials: any) => {
    // Any credentials work in mock mode
    localStorage.setItem('auth', JSON.stringify(credentials))
    return true
}
```

### Upgrade path (production)

For production dashboards, consider:

**OAuth 2.0** (Google, GitHub, etc.):
- Use auth provider (Auth0, Supabase Auth, Clerk)
- Replace in-memory auth with provider SDK
- Update backend to validate JWT tokens

**SSO** (Enterprise):
- Integrate with SAML or OIDC
- Use enterprise auth provider
- Update middleware for token validation

**Session-based**:
- Implement session cookies
- Add CSRF protection
- Use secure, http-only cookies

See `docs/CUSTOMIZATION.md` for auth upgrade instructions.

## Environment handling

### Backend environments

**Development**:
```bash
# backend/.env
DASHBOARD_DATA_MODE=mock
API_KEY=dev-key
FRONTEND_URL=http://localhost:5173
```

**Production**:
```bash
# backend/.env (production)
DASHBOARD_DATA_MODE=live
API_KEY=prod-secret-key
FRONTEND_URL=https://your-dashboard.com
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
```

### Frontend environments

**Development**:
```bash
# frontend/.env
VITE_DASHBOARD_API_URL=http://localhost:8000
```

**Production**:
```bash
# frontend/.env.production
VITE_DASHBOARD_API_URL=https://your-backend.com
```

### Test/Prod switch

Frontend can switch between test and production environments:

```typescript
// In useDataEnvironment hook
const [environment, setEnvironment] = useState<'test' | 'prod'>('test')

const apiUrl = environment === 'test' 
    ? import.meta.env.VITE_DASHBOARD_API_URL_TEST
    : import.meta.env.VITE_DASHBOARD_API_URL_PROD
```

UI toggle in TopBar allows switching without redeploying.

## Feature flags

### Backend flags

**File**: `backend/app/config.py`

```python
class Settings(BaseSettings):
    feature_supabase: bool = True
    feature_vercel: bool = False
    feature_host_health: bool = False
    feature_costs_module: bool = False
    feature_test_prod_switch: bool = True
```

**Environment variables**:
```bash
FEATURE_SUPABASE=true
FEATURE_VERCEL=false
```

### Frontend flags

**File**: `frontend/template.config.ts`

```typescript
export const templateConfig = {
    features: {
        vercel: false,
        costs: false,
        testProdSwitch: true
    }
}
```

### Flag usage

**Backend**:
```python
if settings.feature_vercel:
    # Include Vercel router
    app.include_router(vercel.router)
```

**Frontend**:
```typescript
{features.vercel && <VercelSection />}
```

## Type safety contract

### Backend → Frontend

**Rule**: Backend Pydantic models must match frontend TypeScript types exactly.

**Backend**:
```python
class OverviewResponse(BaseModel):
    total_users: int
    active_users: int
    growth_rate: float
```

**Frontend**:
```typescript
export interface OverviewResponse {
    total_users: number;
    active_users: number;
    growth_rate: number;
}
```

### Ensuring consistency

1. Update backend Pydantic model
2. Update frontend TypeScript type
3. Update mock data in both places
4. Test with both mock and live modes

### Optional: Type generation

For larger projects, consider code generation:
- Use `openapi-typescript` to generate types from OpenAPI spec
- Or use a tool to sync Pydantic models to TypeScript

## Deployment architecture

### Backend deployment

**Render**:
- Docker container with Python
- Environment variables from Render dashboard
- Auto-deploys on git push

**Railway**:
- Similar to Render
- Uses `deploy/railway.toml` config

**Custom**:
- Any hosting that supports Python/FastAPI
- Requires setting environment variables

### Frontend deployment

**Vercel** (recommended):
- Static build from `npm run build`
- Environment variable for API URL
- Auto-deploys on git push

**Netlify**:
- Similar to Vercel
- Uses `deploy/netlify.toml`

**Cloudflare Pages**:
- Edge deployment
- Global CDN

### Production considerations

- **Backend**: Use production entry point `app.server:app`
- **Frontend**: Build with `npm run build`
- **Environment**: Use production `.env` files
- **Security**: Rotate API keys, use HTTPS
- **Monitoring**: Add logging and error tracking

## Performance optimization

### Backend

- **Caching**: Cache expensive queries (Redis optional)
- **Pagination**: Use pagination for large datasets
- **Connection pooling**: Reuse database connections
- **Async**: Use async/await for I/O operations

### Frontend

- **React Query**: Automatic caching and deduplication
- **Code splitting**: Lazy load routes
- **Bundle size**: Tree-shake unused code
- **Image optimization**: Use next/image or similar

## Security considerations

### Backend

- **CORS**: Restrict to frontend domain
- **API keys**: Never expose in frontend
- **SQL injection**: Use parameterized queries
- **Rate limiting**: Add rate limiting middleware

### Frontend

- **XSS**: React auto-escapes, be careful with dangerouslySetInnerHTML
- **CSRF**: Use same-site cookies for auth
- **Env vars**: Never expose secrets in frontend builds
- **HTTPS**: Always use HTTPS in production

## Monitoring and observability

### Backend logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Fetching overview data")
```

### Error tracking

```python
try:
    result = data_source.get_overview()
except Exception as e:
    logger.error(f"Failed to fetch overview: {e}")
    raise
```

### Frontend error boundaries

```typescript
<ErrorBoundary fallback={<ErrorFallback />}>
    <App />
</ErrorBoundary>
```

## Scalability considerations

### Backend scaling

- **Horizontal**: Deploy multiple instances behind load balancer
- **Vertical**: Increase CPU/memory (Render/Railway plans)
- **Database**: Use managed database (Supabase scales automatically)

### Frontend scaling

- **CDN**: Deploy to edge network (Vercel, Cloudflare)
- **Caching**: Leverage browser caching and CDN caching
- **Static assets**: Use CDN for images, fonts
