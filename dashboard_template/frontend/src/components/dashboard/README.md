# Dashboard Components Catalog

Reusable UI components for the analytics dashboard.

## Components

### KpiCard

Single metric display with trend indicator and optional action slot.

**Props:**
- `title: string` - Metric name
- `value: number` - Metric value
- `trend?: number` - Trend percentage (positive/negative)
- `unit?: string` - Unit label (e.g., "users", "%", "USD")
- `format?: (value: number) => string` - Custom formatter
- `action?: ReactNode` - Optional action button (e.g., wake button)

**Usage:**
```tsx
<KpiCard
  title="Total Users"
  value={1250}
  trend={0.15}
  unit="users"
  action={<WakeButton />}
/>
```

**Pattern:** Use action slot for interactive elements like wake buttons, refresh, etc.

---

### KpiGroupSection

Grouped metrics with mini sparkline charts.

**Props:**
- `title: string` - Section title
- `metrics: Array<{label: string, value: number, unit: string}>` - Metric data
- `formatChartValue?: (value: number) => string` - Chart value formatter
- `onViewChart?: () => void` - Callback for "View chart" dialog

**Usage:**
```tsx
<KpiGroupSection
  title="Volume"
  metrics={[
    { label: "Today", value: 150, unit: "count" },
    { label: "Week", value: 1050, unit: "count" },
  ]}
  formatChartValue={fmtUsd}
/>
```

**Formatters:**
- `fmtPctChart` - Percentages (0.15 → "15%")
- `fmtUsd` - Currency (1000 → "$1,000")
- `fmtSecs` - Seconds (90 → "1m 30s")

---

### MetricSection

Collapsible section with refresh button and loading state.

**Props:**
- `title: string` - Section title
- `description?: string` - Optional description
- `children: ReactNode` - Section content
- `defaultOpen?: boolean` - Initial expanded state (default: true)
- `onRefresh?: () => Promise<void>` - Refresh callback
- `isLoading?: boolean` - Loading state
- `refreshable?: boolean` - Show refresh button (default: true)

**Usage:**
```tsx
<MetricSection title="Key Metrics" defaultOpen onRefresh={handleRefresh} isLoading={loading}>
  <KpiGroupSection {...} />
</MetricSection>
```

**Pattern:** Use for grouping related content, especially on pages with many sections. The collapsible UI helps manage information density, and the refresh button allows users to update data without page reload.

---

### ChartCard

Chart container with description tooltip.

**Props:**
- `title: string` - Chart title
- `description?: string` - Chart description
- `descriptionTooltip?: string` - Detailed tooltip text
- `children: ReactNode` - Chart component (Recharts)

**Usage:**
```tsx
<ChartCard
  title="Growth Over Time"
  description="User growth trend"
  descriptionTooltip="Shows new user signups over time"
>
  <LineChart data={data} {...} />
</ChartCard>
```

**Pattern:** All charts should be wrapped in ChartCard for consistent layout and tooltips.

---

### DataTable

Sortable, filterable data table with export.

**Props:**
- `columns: Array<{id: string, header: string, render?: (row) => ReactNode}>` - Column definitions
- `data: Array<any>` - Table data
- `exportable?: boolean` - Enable CSV export
- `emptyMessage?: string` - Custom empty state message

**Usage:**
```tsx
<DataTable
  columns={[
    { id: "name", header: "Name" },
    { id: "email", header: "Email" },
    { id: "status", header: "Status", render: (row) => <Badge>{row.status}</Badge> }
  ]}
  data={users}
  exportable
/>
```

**Pattern:** Use `render` for custom cell formatting (badges, links, etc.)

---

### LoadingSkeleton

Loading state placeholder.

**Props:**
- `type: "card" | "table" | "chart"` - Skeleton type

**Usage:**
```tsx
<LoadingSkeleton type="card" />
```

**Pattern:** Show while data is loading, replace with actual content when ready.

---

## Patterns

### Metric Descriptions

Use `metricDescriptions.ts` for detailed metric help text:

```typescript
export const metricDescriptions = {
  totalUsers: {
    title: "Total Users",
    description: "What this metric measures",
    formula: "Calculation formula",
    good: "What a good value looks like",
    bad: "What a bad value looks like"
  }
}
```

Access via `MetricDetailDialog` component on click/hover.

### Section State Management

Use `usePageSections` hook for collapsible sections:

```typescript
const { sections, toggleSection, expandAll, collapseAll } = usePageSections();
```

### Date Range Handling

Use `useDateRange` hook for date filtering:

```typescript
const { dateRange, setDateRange, presets } = useDateRange();
```

### Environment Switching

Use `useDataEnvironment` hook for test/prod switching:

```typescript
const { environment, setEnvironment, apiUrl } = useDataEnvironment();
```

## Best Practices

1. **Consistent Layout**: Always wrap charts in `ChartCard`, metrics in `KpiCard` or `KpiGroupSection`
2. **Loading States**: Use `LoadingSkeleton` while data loads
3. **Empty States**: Provide meaningful empty messages in `DataTable` and sections
4. **Tooltips**: Add `descriptionTooltip` to `ChartCard` for complex metrics
5. **Actions**: Use action slots in `KpiCard` for interactive elements
6. **Formatters**: Use provided formatters (`fmtPctChart`, `fmtUsd`, `fmtSecs`) for consistency

## Customization

To customize components:
1. Copy component to your project
2. Modify props and styling as needed
3. Keep the same interface for consistency
4. Update this README with your changes
