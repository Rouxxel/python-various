# Customization Guide

End-to-end guide for forking this template for your application.

## Step 1: Rename project in template config

**File**: `frontend/template.config.ts`

Update the project name and branding:

```typescript
export const templateConfig = {
    projectName: "Your App Name",
    projectLogo: "/your-logo.svg",  // optional
    // ...
}
```

Also update:
- `package.json` name field
- Backend FastAPI `title` in `backend/app/main.py`
- Page `<title>` meta tags if needed

## Step 2: Choose data mode (mock → live)

**File**: `backend/.env`

Start with mock mode for development:

```bash
DASHBOARD_DATA_MODE=mock
```

When ready for live data:

```bash
DASHBOARD_DATA_MODE=live
```

Mock mode requires zero external services. Live mode requires provider credentials.

## Step 3: Enable features in .env

**File**: `backend/.env.example` → copy to `backend/.env`

Uncomment and configure the features you need:

```bash
# Required for all modes
API_KEY=your-secret-key
FRONTEND_URL=http://localhost:5173

# Database (optional if mock)
FEATURE_SUPABASE=true
SUPABASE_URL=your-project-url
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Vercel (optional)
FEATURE_VERCEL=false
# VERCEL_PROJECT_ID=
# VERCEL_TOKEN=

# Hosting health (optional)
FEATURE_HOST_HEALTH=false
HOSTING_PROVIDER=render
# RENDER_SERVICE_URL=

# Costs module (optional)
FEATURE_COSTS_MODULE=false
# COSTS_UNIT_PRICE=
# COSTS_UNIT_NAME=
```

See [PROVIDERS.md](PROVIDERS.md) for detailed setup instructions per provider.

## Step 4: Replace placeholder builders one page at a time

### Backend: Replace data builders

**Location**: `backend/app/services/live/`

Each placeholder file has TODO comments. For example, in `placeholder_analytics.py`:

```python
def build_users(from_date: datetime, to_date: datetime) -> UsersResponse:
    # TODO: Replace with your actual user query
    # Example: query your database for user metrics
    
    # Expected tables/columns:
    # - users: id, created_at, status, last_active
    
    return UsersResponse(
        total_users=0,  # Your query result
        active_users=0,
        # ...
    )
```

**Steps**:
1. Identify the tables/columns your data source has
2. Write the query (SQL, API call, etc.)
3. Map results to the Pydantic response model
4. Test with `DASHBOARD_DATA_MODE=live`

### Frontend: Update metric descriptions

**File**: `frontend/src/lib/metricDescriptions.ts`

Replace placeholder descriptions with your business logic:

```typescript
export const metricDescriptions = {
    totalUsers: {
        title: "Total Users",
        description: "Total number of registered user accounts",
        formula: "COUNT(users.id)",
        good: "Growing month over month",
        bad: "Declining or stagnant"
    },
    // ... your metrics
}
```

## Step 5: Update sidebar navigation

**File**: `frontend/template.config.ts`

Customize the navigation for your needs:

```typescript
navItems: [
    // Keep showcase routes for reference, or remove
    { id: "overview", label: "Overview", path: "/overview", icon: "layout-dashboard", enabled: true },
    
    // Your custom pages
    { id: "users", label: "Users", path: "/users", icon: "users", enabled: true },
    { id: "revenue", label: "Revenue", path: "/revenue", icon: "dollar-sign", enabled: true },
    
    // Hide showcase routes when ready
    { id: "metrics", label: "Metrics Gallery", path: "/metrics", icon: "bar-chart", enabled: false },
    { id: "charts", label: "Charts Gallery", path: "/charts", icon: "line-chart", enabled: false },
]
```

## Step 6: Deploy backend + frontend

### Backend deployment

Choose a provider (Render, Railway, Fly, etc.):

**Render** (see `deploy/render.yaml`):
```bash
# Connect your repo to Render
# Set environment variables in Render dashboard
# Deploy
```

**Railway** (see `deploy/railway.toml`):
```bash
railway login
railway init
railway up
```

### Frontend deployment

**Vercel** (recommended):
```bash
cd frontend
npm run build
vercel deploy
```

Set `VITE_DASHBOARD_API_URL` to your backend URL.

## Step 7: Remove showcase routes from nav

Once your custom pages are working, hide the showcase routes:

```typescript
// In templateConfig.ts
navItems: [
    // Your pages
    { id: "users", label: "Users", path: "/users", icon: "users", enabled: true },
    
    // Showcase routes - set enabled: false
    { id: "overview", label: "Overview", path: "/overview", icon: "layout-dashboard", enabled: false },
    { id: "metrics", label: "Metrics Gallery", path: "/metrics", icon: "bar-chart", enabled: false },
]
```

Keep the files for reference - they demonstrate all UI patterns.

## Step 8: Test and iterate

### Testing checklist

- [ ] Mock mode works locally with zero credentials
- [ ] Live mode works with your database
- [ ] All custom pages load without errors
- [ ] Metric descriptions are accurate
- [ ] Navigation shows only your pages
- [ ] Frontend builds successfully
- [ ] Backend tests pass
- [ ] Production deployment works

### Common issues

**Empty charts in live mode**:
- Verify backend credentials are correct
- Check backend logs for query errors
- Ensure data format matches TypeScript types

**CORS errors**:
- Verify `FRONTEND_URL` in backend `.env`
- Check backend CORS middleware configuration

**Build failures**:
- Ensure all dependencies are installed
- Check TypeScript types match backend responses
- Verify environment variables are set

## Advanced customization

### Adding authentication

The template uses in-memory auth (any credentials work). For production:

1. Replace `useAuth.tsx` with your auth provider
2. Add OAuth/SSO integration
3. Update backend middleware to validate tokens
4. See your auth provider's documentation

### Custom themes

**Tailwind config** (`tailwind.config.js`):
```javascript
theme: {
    extend: {
        colors: {
            brand: {
                50: '#f0f9ff',
                500: '#0ea5e9',
                900: '#0c4a6e',
            }
        }
    }
}
```

**CSS variables** (in your CSS):
```css
:root {
    --color-primary: #0ea5e9;
    --color-secondary: #6366f1;
}
```

### Adding new providers

1. Create service module in `backend/app/services/`
2. Add feature flag in `backend/app/config.py`
3. Add environment variables to `.env.example`
4. Document in `docs/PROVIDERS.md`
5. Add UI section if needed

## Type Safety Contract

**Rule**: Backend Pydantic models must match frontend TypeScript types.

### Backend (Pydantic Models)

Location: `backend/app/models/` or inline in routers

```python
from pydantic import BaseModel

class UsersResponse(BaseModel):
    total_users: int
    active_users: int
    new_signups: int
    trend: float
```

### Frontend (TypeScript Types)

Location: `frontend/src/lib/types.ts`

```typescript
export interface UsersResponse {
    total_users: number;
    active_users: number;
    new_signups: number;
    trend: number;
}
```

### Maintaining Consistency

When adding a new endpoint:

1. **Define Pydantic model** in backend
2. **Define TypeScript interface** in frontend with matching fields
3. **Use the types** in your React components
4. **Test** that the data flows correctly

### Common Pitfalls

- **Snake case vs camel case**: Backend uses snake_case (`total_users`), frontend can use camelCase (`totalUsers`) - map in the API layer
- **Optional fields**: Mark as `Optional[T]` in Pydantic and `field?: T` in TypeScript
- **Nested objects**: Ensure nested structures match on both sides
- **Date formats**: Use ISO 8601 strings consistently

### Validation

The backend validates incoming data via Pydantic. The frontend should validate user input before sending.

## Getting help

- Check [README.md](../README.md) for overview
- Check [backend/README.md](../backend/README.md) for API details
- Check [frontend/README.md](../frontend/README.md) for component docs
- Check [PROVIDERS.md](PROVIDERS.md) for provider setup
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design

## Time estimate

- **Clone and run mock mode**: 5-10 minutes
- **Enable one provider (e.g., Supabase)**: 30-60 minutes
- **Replace one page with live data**: 1-2 hours
- **Full customization for production**: 1-2 days
