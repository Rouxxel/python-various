# Routes Documentation

This document explains the routing structure and how to add new pages to the dashboard.

## Routing Architecture

The dashboard uses TanStack Router for file-based routing. Routes are defined in `frontend/src/routes/` and automatically registered.

### How TanStack Router Works

TanStack Router uses file-based routing with code generation:

1. **Route files**: Create `.tsx` files in `frontend/src/routes/`
2. **Code generation**: Run `npx tsr generate` to generate `routeTree.gen.ts`
3. **Type safety**: The generated tree provides full TypeScript type safety

## Route List

| Route | Template Role | Default Nav | Data Source |
|-------|---------------|-------------|-------------|
| `/login` | Auth | Hidden | Backend (mock auth) |
| `/overview` | Showcase — summary KPIs + charts | Enabled | Mock data |
| `/metrics` | Showcase — KPI groups gallery | Enabled | Mock data |
| `/charts` | Showcase — chart types gallery | Enabled | Mock data |
| `/tables` | Showcase — DataTable patterns | Enabled | Mock data |
| `/infrastructure` | Provider modules demo | Enabled | Mock + optional live |
| `/users` | Domain placeholder | Disabled | Mock data |
| `/activity` | Domain placeholder | Disabled | Mock data |
| `/costs` | Domain placeholder | Disabled | Mock data |
| `/ai` | Domain placeholder | Disabled | Mock data |
| `/insights` | Domain placeholder | Disabled | Mock data |
| `/sessions` | Domain placeholder | Disabled | Mock data |

## Minimal Route Example

The simplest possible route:

```typescript
// frontend/src/routes/my-page.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/my-page')({
  component: MyPage
})

function MyPage() {
  return <div>Hello World</div>
}
```

## Route Structure

```
frontend/src/routes/
├── index.tsx              # Landing page (redirects to overview)
├── overview.tsx           # Overview showcase page
├── metrics.tsx            # Metrics gallery showcase
├── charts.tsx             # Charts gallery showcase
├── tables.tsx             # Tables gallery showcase
├── infrastructure.tsx    # Infrastructure monitoring
├── users.tsx              # Users domain placeholder
├── activity.tsx           # Activity domain placeholder
├── costs.tsx              # Costs domain placeholder
├── ai.tsx                 # AI metrics domain placeholder
├── insights.tsx           # Insights domain placeholder
└── sessions.tsx           # Sessions domain placeholder
```

## Adding a New Route

### Step 1: Create the route file

Create a new file in `frontend/src/routes/`:

```typescript
// frontend/src/routes/my-page.tsx
import { createFileRoute } from '@tanstack/react-router'
import { PageHeader } from '../components/PageHeader'
import { MetricSection } from '../components/dashboard/MetricSection'
import { KpiCard } from '../components/dashboard/KpiCard'

export const Route = createFileRoute('/my-page')({
  component: MyPage
})

function MyPage() {
  return (
    <div className="p-6">
      <PageHeader
        title="My Page"
        description="Page description"
      />
      
      <MetricSection title="My Metrics" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Metric 1" value={100} trend={0.05} unit="count" />
          <KpiCard title="Metric 2" value={200} trend={-0.02} unit="count" />
        </div>
      </MetricSection>
    </div>
  )
}
```

### Step 2: Add to navigation

Update `frontend/template.config.ts`:

```typescript
navItems: [
  {
    id: "my-page",
    label: "My Page",
    path: "/my-page",
    enabled: true,
    category: "domain"
  }
]
```

### Step 3: Add TypeScript types (if using API)

Update `frontend/src/lib/types.ts`:

```typescript
export interface MyPageResponse {
  metric1: number;
  metric2: number;
  trend: number;
}
```

### Step 4: Add API fetch function (if using API)

Update `frontend/src/lib/api.ts`:

```typescript
export async function fetchMyPageData(from: string, to: string): Promise<MyPageResponse> {
  const response = await fetch(`${API_URL}/api/my-page?from_date=${from}&to_date=${to}`);
  return response.json();
}
```

### Step 5: Add React Query hook (optional)

Create or update `frontend/src/lib/queries.ts`:

```typescript
export function useMyPageData(from: string, to: string) {
  return useQuery({
    queryKey: ['my-page', from, to],
    queryFn: () => fetchMyPageData(from, to)
  });
}
```

## Route Categories

Routes are organized into categories in `template.config.ts`:

- **showcase**: Template demonstration pages (overview, metrics, charts, tables)
- **domain**: Your custom domain pages (users, activity, costs, ai, etc.)
- **infrastructure**: Infrastructure monitoring page

## Route Patterns

### Showcase Routes

These demonstrate the design system with mock data. Keep them for reference even after customizing your dashboard.

**Examples**: `overview.tsx`, `metrics.tsx`, `charts.tsx`, `tables.tsx`

### Domain Placeholder Routes

These are templates for your specific domain. Customize them by:

1. Updating KPIs to match your metrics
2. Replacing mock data with live API calls
3. Updating charts to show your data
4. Customizing tables for your entities

**Examples**: `users.tsx`, `activity.tsx`, `costs.tsx`, `ai.tsx`, `insights.tsx`, `sessions.tsx`

### Infrastructure Route

The infrastructure page is provider-agnostic and modular. It shows hosting health, deployments, and storage metrics based on enabled features.

**Example**: `infrastructure.tsx`

## Common Page Patterns

### KPI-Only Page

```typescript
<PageHeader title="My Metrics" />
<MetricSection title="Overview">
  <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
    <KpiCard title="Metric" value={100} trend={0.05} unit="count" />
  </div>
</MetricSection>
```

### KPI + Chart Page

```typescript
<PageHeader title="My Analytics" />
<MetricSection title="Overview">
  <KpiCard title="Metric" value={100} trend={0.05} unit="count" />
</MetricSection>
<MetricSection title="Trend">
  <ChartCard title="Metric Over Time">
    <LineChart data={data} {...} />
  </ChartCard>
</MetricSection>
```

### KPI + Chart + Table Page

```typescript
<PageHeader title="My Data" />
<MetricSection title="Overview">
  <KpiCard title="Metric" value={100} trend={0.05} unit="count" />
</MetricSection>
<MetricSection title="Trend">
  <ChartCard title="Metric Over Time">
    <LineChart data={data} {...} />
  </ChartCard>
</MetricSection>
<MetricSection title="Details">
  <DataTable columns={columns} data={data} exportable />
</MetricSection>
```

## Data Fetching Patterns

### Mock Data (Development)

```typescript
const mockData = {
  metric: 100,
  trend: 0.05
};

function MyPage() {
  return <KpiCard value={mockData.metric} trend={mockData.trend} />
}
```

### React Query (Production)

```typescript
import { useMyPageData } from '../lib/queries';

function MyPage() {
  const { data, isLoading } = useMyPageData(from, to);
  
  if (isLoading) return <LoadingSkeleton />;
  
  return <KpiCard value={data.metric} trend={data.trend} />
}
```

### Feature-Guarded Routes

```typescript
import { useFeatures } from '../hooks/useFeatures';

function MyPage() {
  const { features } = useFeatures();
  
  if (!features.my_feature) {
    return <FeatureDisabledCard feature="My Page" />;
  }
  
  return <MyPageContent />;
}
```

## Best Practices

1. **Use MetricSection** for grouping related content
2. **Use KpiCard** for individual metrics with trends
3. **Use ChartCard** for all chart types (consistent layout)
4. **Use DataTable** for tabular data with export
5. **Add loading states** when fetching data
6. **Handle empty states** when no data is available
7. **Use feature flags** to conditionally enable features
8. **Keep showcase routes** for reference (disable in nav when ready)

## Troubleshooting

### Route not showing in sidebar

- Check `enabled: true` in `template.config.ts`
- Verify the path matches the route file
- Check for typos in the route ID

### Page not loading

- Check browser console for errors
- Verify all imports are correct
- Check that the route file is valid TypeScript

### Data not loading

- Verify API URL is set in `.env`
- Check backend is running
- Verify data format matches TypeScript types
- Check browser network tab for API errors
