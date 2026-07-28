# Frontend

React + TypeScript frontend for the analytics dashboard template. Built with TanStack Router, Recharts, and Tailwind CSS.

## Adding a new dashboard page

Follow this step-by-step guide to add a new page:

1. **Create route file** in `src/routes/`
   ```typescript
   // src/routes/my-page.tsx
   import { createFileRoute } from '@tanstack/react-router'
   import { PageHeader } from '../components/dashboard/PageHeader'
   import { MetricSection } from '../components/dashboard/MetricSection'
   
   export const Route = createFileRoute('/my-page')({
     component: MyPage
   })
   
   function MyPage() {
     return (
       <div>
         <PageHeader title="My Page" description="Page description" />
         <MetricSection title="My Metrics">
           {/* Your content */}
         </MetricSection>
       </div>
     )
   }
   ```

2. **Add sidebar link** in `frontend/template.config.ts`
   ```typescript
   navItems: [
       { id: "my-page", label: "My Page", path: "/my-page", icon: "chart", enabled: true }
   ]
   ```

3. **Add API fetch function** in `src/lib/api.ts`
   ```typescript
   export async function fetchMyPageData(from: string, to: string): Promise<MyPageResponse> {
       const response = await fetch(`${API_URL}/api/my-page?from_date=${from}&to_date=${to}`);
       return response.json();
   }
   ```

4. **Add TypeScript type** in `src/lib/types.ts`
   ```typescript
   export interface MyPageResponse {
       metric: string;
       value: number;
   }
   ```

5. **Add query hook** (optional, for data fetching)
   ```typescript
   // In your component or a separate hooks file
   const { data, isLoading } = useQuery({
       queryKey: ['my-page', from, to],
       queryFn: () => fetchMyPageData(from, to)
   })
   ```

6. **Add mock payload** in `src/lib/mock-data.ts` (for development)
   ```typescript
   export const mockMyPageData: MyPageResponse = {
       metric: "example",
       value: 100
   }
   ```

## UI building blocks

The frontend provides reusable components for common dashboard patterns.

### Core components

**Location**: `src/components/dashboard/`

- **`KpiCard`** - Single metric display with trend indicator
  - Props: `title`, `value`, `trend`, `unit`, `format`, `action` (slot)
  - Use for: Individual KPIs with optional action buttons

- **`KpiGroupSection`** - Grouped metrics with mini sparkline charts
  - Props: `title`, `metrics[]`, `formatChartValue`
  - Use for: Related metrics (e.g., "Today / Week / Month")
  - `formatChartValue` examples: `fmtPctChart`, `fmtUsd`, `fmtSecs`

- **`MetricSection`** - Collapsible section with refresh button
  - Props: `title`, `description`, `children`, `defaultOpen`, `onRefresh`, `isLoading`, `refreshable`
  - Use for: Grouping related content, expandable sections

- **`ChartCard`** - Chart container with description tooltip
  - Props: `title`, `description`, `children`, `descriptionTooltip`
  - Use for: All chart types, provides consistent layout

- **`DataTable`** - Sortable, filterable data table
  - Props: `columns[]`, `data`, `exportable`, `emptyMessage`
  - Use for: Tabular data with export functionality

- **`LoadingSkeleton`** - Loading state placeholder
  - Props: `type` (card, table, chart)
  - Use for: Consistent loading states

### Layout components

**Location**: `src/components/`

- **`Sidebar`** - Navigation sidebar with category grouping
  - Props: (uses templateConfig internally)
  - Use for: Main application navigation

- **`PageHeader`** - Page title and description header
  - Props: `title`, `description`, `actions`
  - Use for: Page-level headers

- **`DevBanner`** - Development mode banner
  - Props: (uses features internally)
  - Use for: Showing data mode and disabled features

- **`EnvironmentSwitcher`** - Test/prod environment toggle
  - Props: (uses features internally)
  - Use for: Switching between test and production environments

### Auth components

**Location**: `src/components/auth/`

- **`LoginPage`** - Login form with mock authentication
  - Props: (none)
  - Use for: User authentication page

### Metric descriptions

**Location**: `src/lib/metricDescriptions.ts`

Pattern for hover/click help text:
```typescript
export const metricDescriptions = {
    myMetric: {
        title: "My Metric",
        description: "What this metric measures and why it matters",
        formula: "Calculation formula (optional)",
        good: "What a good value looks like",
        bad: "What a bad value looks like"
    }
}
```

Used by `MetricDetailDialog` for detailed metric explanations.

### Custom hooks

**Location**: `src/hooks/`

- **`usePageSections`** - Manage collapsible section state
  - Returns: `sections`, `toggleSection`, `expandAll`, `collapseAll`
  - Use for: Pages with multiple expandable sections

- **`useDateRange`** - Manage date range selection
  - Returns: `dateRange`, `setDateRange`, `presets`
  - Use for: Pages with date filtering

- **`useDataEnvironment`** - Switch between test/prod environments
  - Returns: `environment`, `setEnvironment`, `apiUrl`
  - Use for: Pages that need test/prod switching

- **`useFeatures`** - Fetch and access feature flags
  - Returns: `features`, `isLoading`, `error`
  - Use for: Conditionally rendering features based on flags

- **`useAuth`** - Authentication state management
  - Returns: `user`, `login`, `logout`, `isAuthenticated`
  - Use for: Protecting routes and managing user sessions

## Sidebar / navigation configuration

Navigation is centralized in `frontend/template.config.ts`:

```typescript
export const templateConfig = {
    navItems: [
        {
            id: "overview",
            label: "Overview",
            path: "/overview",
            icon: "layout-dashboard",
            enabled: true
        },
        // ... more items
    ]
}
```

**Properties**:
- `id`: Unique identifier
- `label`: Display text
- `path`: Route path
- `icon`: Lucide icon name
- `enabled`: Show/hide in sidebar

The `Sidebar` component filters `navItems` by `enabled` and renders the navigation.

## How to hide a page without deleting files

To hide a page from navigation while keeping the files:

1. **Set `enabled: false`** in `templateConfig.ts`
   ```typescript
   { id: "my-page", label: "My Page", path: "/my-page", icon: "chart", enabled: false }
   ```

2. **Set feature flag** (if using feature flags)
   ```typescript
   enabled: features.myPageFeature
   ```

3. **Optional: Add feature guard** in the route component
   ```typescript
   if (!features.myPageFeature) {
       return <FeatureDisabledCard feature="My Page" />
   }
   ```

The route remains accessible via direct URL but hidden from navigation.

## Theming / branding

Customize the look and feel:

### App title and logo

**Location**: `frontend/template.config.ts`
```typescript
export const templateConfig = {
    projectName: "My Dashboard",
    projectLogo: "/logo.svg"  // optional
}
```

### Accent colors

**Location**: `tailwind.config.js` or CSS variables
```javascript
theme: {
    extend: {
        colors: {
            primary: {
                50: '#f0f9ff',
                // ... your color scale
            }
        }
    }
}
```

### Page titles

Update `<title>` meta tags in `index.html` or use a layout component:
```typescript
useEffect(() => {
    document.title = `${templateConfig.projectName} - ${pageTitle}`
}, [pageTitle])
```

## Component catalog

See `src/components/dashboard/README.md` for a complete component catalog with:
- Screenshots or ASCII layouts
- Props documentation
- Usage examples
- Best practices

## Troubleshooting

### CORS errors

**Symptoms**: Browser console shows CORS errors, API calls fail

**Solutions**:
- Verify `VITE_DASHBOARD_API_URL` in `.env` matches backend URL
- Check backend CORS configuration in `app/main.py`
- Ensure `FRONTEND_URL` in backend `.env` matches your frontend URL
- Ensure both services are running on correct ports

### 401 Unauthorized errors

**Symptoms**: API calls return 401 status, login fails

**Solutions**:
- Verify `API_KEY` is set in backend `.env`
- Check that your frontend is sending the API key in headers
- Verify authentication middleware configuration
- Try logging out and logging in again

### Empty charts or missing data

**Symptoms**: Charts render but show no data, tables are empty

**Solutions**:
- Check browser console for API errors
- Verify backend is returning data (check backend logs)
- Check data format matches TypeScript types
- Try mock mode to isolate the issue (`DASHBOARD_DATA_MODE=mock`)
- Verify feature flags are enabled for the data you need

### Wrong environment (test vs prod)

**Symptoms**: Data from wrong environment, API calls to wrong URL

**Solutions**:
- Check `VITE_DASHBOARD_API_URL` is set correctly
- Verify test/prod switch is using the right URL
- Check `useDataEnvironment` hook usage
- Verify `MAIN_API_URL_TEST` and `MAIN_API_URL_PROD` in backend `.env`

### Build errors

**Symptoms**: `npm run build` fails, TypeScript errors

**Solutions**:
- Ensure all dependencies are installed: `npm install`
- Check TypeScript types match backend responses
- Verify all imports are correct
- Check for missing environment variables
- Run `npm run type-check` for specific TypeScript errors

### Development server issues

**Symptoms**: Frontend won't start, port conflicts

**Solutions**:
- Check if port 5173 is already in use
- Kill existing processes: `npx kill-port 5173`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check for syntax errors in your code

## Development

Start the frontend in development mode:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`

## Build for production

```bash
npm run build
npm run preview
```

Build output goes to `dist/` folder.

## Type safety

**Rule**: Backend Pydantic models ↔ frontend `types.ts` must match

When adding or modifying API responses:
1. Update backend Pydantic model
2. Update frontend TypeScript type in `types.ts`
3. Update mock data to match both

This ensures type safety across the full stack.
