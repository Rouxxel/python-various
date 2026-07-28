/**
 * Costs Route - Domain Placeholder
 * 
 * REPLACE THIS: This is a template for cost analytics.
 * Customize cost categories, pricing models, and projections for your specific domain.
 * 
 * TODO:
 * - Update cost categories to match your infrastructure
 * - Configure pricing models in backend (see app/services/costs/)
 * - Add domain-specific cost breakdowns
 * - Update API calls to use your live data
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { ChartCard } from "../components/dashboard/ChartCard";
import { DataTable } from "../components/dashboard/DataTable";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useFeatures } from "../hooks/useFeatures";

// TODO: Replace with your actual data fetching
const mockCostTrendData = [
  { month: "Jan", projected: 4000, actual: 4200 },
  { month: "Feb", projected: 4000, actual: 4100 },
  { month: "Mar", projected: 4200, actual: 4300 },
  { month: "Apr", projected: 4200, actual: 4150 },
  { month: "May", projected: 4500, actual: 4600 },
  { month: "Jun", projected: 4500, actual: 4750 },
];

const mockCostByCategory = [
  { category: "Hosting", amount: 2500 },
  { category: "Database", amount: 800 },
  { category: "Storage", amount: 450 },
  { category: "Bandwidth", amount: 600 },
  { category: "Other", amount: 400 },
];

const mockUnitEconomics = [
  { metric: "Cost per User", value: 8.64, unit: "USD" },
  { metric: "Cost per Request", value: 0.002, unit: "USD" },
  { metric: "Cost per GB", value: 0.15, unit: "USD" },
];

export default function Costs() {
  const { features } = useFeatures();
  // TODO: Uncomment when API is ready
  // const { dateRange } = useDateRange();
  // const { data: costsData, isLoading } = useCosts(dateRange.from, dateRange.to);
  
  // Guard with feature flag
  if (!features?.features.costs_module) {
    return (
      <div className="p-6">
        <PageHeader
          title="Costs"
          description="Cost analytics and projections"
        />
        <div className="rounded-lg bg-yellow-50 p-6 text-yellow-800">
          <h3 className="mb-2 font-semibold">Costs Module Disabled</h3>
          <p className="text-sm">
            To enable costs analytics, set <code>FEATURE_COSTS_MODULE=true</code> in your backend environment variables
            and configure your pricing models in <code>app/services/costs/</code>.
          </p>
        </div>
      </div>
    );
  }

  // TODO: Uncomment when API is ready
  // const { data: costsData, isLoading } = useCosts(dateRange.from, dateRange.to);

  return (
    <div className="p-6">
      <PageHeader
        title="Costs"
        description="Cost analytics and projections"
      />

      {/* TODO: Customize KPI groups for your domain */}
      <MetricSection title="Cost Overview" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Total Cost" value={4750} trend={0.05} unit="USD" />
          <KpiCard title="vs Budget" value={-250} trend={-0.05} unit="USD" />
          <KpiCard title="Cost per User" value={8.64} trend={-0.02} unit="USD" />
          <KpiCard title="Projected Monthly" value={4800} trend={0.03} unit="USD" />
        </div>
      </MetricSection>

      <MetricSection title="Cost Trend" defaultOpen>
        <ChartCard
          title="Monthly Costs"
          description="Projected vs actual costs over time"
          descriptionTooltip="Compare projected budget to actual spending"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockCostTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="projected" stroke="#9ca3af" strokeDasharray="5 5" name="Projected" />
              <Line type="monotone" dataKey="actual" stroke="#3b82f6" strokeWidth={2} name="Actual" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Cost by Category" defaultOpen>
        <DataTable
          columns={[
            { id: "category", header: "Category" },
            { id: "amount", header: "Amount (USD)" },
            { 
              id: "percentage", 
              header: "% of Total",
              render: (row) => `${((row.amount / 4750) * 100).toFixed(1)}%`
            },
          ]}
          data={mockCostByCategory}
          exportable
          emptyMessage="No cost data available"
        />
      </MetricSection>

      <MetricSection title="Unit Economics" defaultOpen>
        <DataTable
          columns={[
            { id: "metric", header: "Metric" },
            { id: "value", header: "Value" },
            { id: "unit", header: "Unit" },
          ]}
          data={mockUnitEconomics}
          exportable
          emptyMessage="No unit economics data available"
        />
      </MetricSection>
    </div>
  );
}
