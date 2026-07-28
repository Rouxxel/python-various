# Routes

This directory contains all page routes for the dashboard. Routes are organized by their role in the template.

## Route categories

### Template showcase routes

These routes demonstrate the UI component library and design system. They use mock data only and neutral labels. Keep these routes enabled to showcase the template's capabilities.

- **`/overview`** - Summary KPIs + charts (default landing page)
  - Demonstrates: PageHeader, MetricSection, KpiGroupSection, ChartCard
  - Data source: Mock

- **`/metrics`** - KPI groups gallery
  - Demonstrates: All KPI patterns (volume, rates, currency, timing, mixed units)
  - Data source: Mock

- **`/charts`** - Chart types gallery
  - Demonstrates: Line, area, bar, pie/donut, stacked area charts
  - Data source: Mock

- **`/tables`** - DataTable patterns
  - Demonstrates: Sorting, filtering, CSV export, custom render columns, empty states
  - Data source: Mock

- **`/infrastructure`** - Provider modules demo
  - Demonstrates: Host health, deployments, storage, database metrics
  - Data source: Mock + optional live

### Domain placeholder routes

These routes provide starting points for common dashboard patterns. Replace the backend data builders with your actual queries. Default to hidden in navigation.

- **`/users`** - User analytics placeholder
  - Demonstrates: Registration overview, engagement metrics, growth charts, retention tables
  - Data source: Mock → Replace with your user data

- **`/activity`** - Activity/events placeholder
  - Demonstrates: Event timeline, activity feed, event type breakdowns
  - Data source: Mock → Replace with your activity data

- **`/costs`** - Cost tracking placeholder
  - Demonstrates: Spend totals, unit economics, projections
  - Data source: Mock → Replace with your cost data
  - Feature flag: `FEATURE_COSTS_MODULE`

- **`/ai`** - AI/ML metrics placeholder (optional)
  - Demonstrates: Generation success rate, latency, token usage, pipeline timing
  - Data source: Mock → Replace with your AI metrics

### Example routes (optional)

Domain-specific examples from the original implementation. These are moved to `examples/` or feature-flagged by default.

- **`/examples/*`** - Beeing-specific or domain-specific examples
  - Use as reference for implementing similar patterns
  - Default: Hidden from navigation

## Placeholder page anatomy

All placeholder pages follow a consistent structure:

```typescript
import { createFileRoute } from '@tanstack/react-router'
import { PageHeader } from '../components/dashboard/PageHeader'
import { MetricSection } from '../components/dashboard/MetricSection'
import { KpiGroupSection } from '../components/dashboard/KpiGroupSection'
import { ChartCard } from '../components/dashboard/ChartCard'
import { DataTable } from '../components/dashboard/DataTable'

export const Route = createFileRoute('/my-page')({
  component: MyPage
})

function MyPage() {
  const { dateRange } = useDateRange()
  
  return (
    <div className="space-y-6">
      {/* Page header with title and description */}
      <PageHeader 
        title="My Page" 
        description="Description of what this page shows"
      />
      
      {/* Collapsible metric section */}
      <MetricSection title="Key Metrics" defaultOpen>
        <KpiGroupSection
          title="Overview"
          metrics={metrics}
          formatChartValue={fmtUsd}
        />
      </MetricSection>
      
      {/* Chart section */}
      <MetricSection title="Trends">
        <ChartCard title="Growth Over Time" description="...">
          <MyChart data={chartData} />
        </ChartCard>
      </MetricSection>
      
      {/* Data table */}
      <MetricSection title="Recent Items">
        <DataTable 
          columns={columns}
          data={tableData}
          exportable
        />
      </MetricSection>
    </div>
  )
}
```

### Component order

1. **PageHeader** - Title and description at the top
2. **MetricSection** - Collapsible sections grouping related content
3. **KpiGroupSection** - KPI cards with mini charts
4. **ChartCard** - Charts with consistent layout and tooltips
5. **DataTable** - Tabular data with sorting and export

## Route file convention

### Standard routes

Use `createFileRoute` with the route path:

```typescript
export const Route = createFileRoute('/my-page')({
  component: MyPage
})
```

### Example routes

Use one of these conventions:

1. **Commented out in main routes directory**
   ```typescript
   // export const Route = createFileRoute('/examples/beeing/wellness')({
   //   component: WellnessPage
   // })
   ```

2. **Moved to `examples/` subdirectory**
   ```
   src/routes/examples/beeing/wellness.tsx
   ```

3. **Feature-flagged component**
   ```typescript
   export const Route = createFileRoute('/wellness')({
     component: () => features.wellness ? <WellnessPage /> : <FeatureDisabled />
   })
   ```

## Adding a new route

1. Create file in `src/routes/` with appropriate name
2. Use `createFileRoute` with the path
3. Implement component following placeholder anatomy
4. Add to `templateConfig.ts` navItems
5. Add backend endpoint if needed
6. Add TypeScript types in `types.ts`
7. Add mock data in `mock-data.ts`

## Route tree generation

TanStack Router generates `routeTree.gen.ts` automatically. Do not edit this file manually.

If routes are not appearing:
1. Restart the dev server
2. Check file names match route paths
3. Verify `createFileRoute` usage is correct
4. Clear `.tanstack-router` cache if needed

## Route-specific hooks

Some routes may use custom hooks:

- **`usePageSections`** - For pages with multiple collapsible sections
- **`useDateRange`** - For pages with date filtering
- **`useDataEnvironment`** - For pages that need test/prod switching

Import from `src/hooks/` as needed.
