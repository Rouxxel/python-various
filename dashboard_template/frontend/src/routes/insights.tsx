/**
 * Insights Route - Domain Placeholder
 * 
 * REPLACE THIS: This is a template for insights/analytics.
 * Customize insights, KPIs, and charts for your specific domain.
 * 
 * TODO:
 * - Update insights to match your analytics needs
 * - Customize KPI groups for your insights metrics
 * - Add domain-specific charts
 * - Update API calls to use your live data
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { ChartCard } from "../components/dashboard/ChartCard";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// TODO: Replace with your actual data fetching
const mockInsightData = [
  { date: "Jan", value: 75 },
  { date: "Feb", value: 82 },
  { date: "Mar", value: 78 },
  { date: "Apr", value: 85 },
  { date: "May", value: 90 },
  { date: "Jun", value: 88 },
];

export default function Insights() {
  return (
    <div className="p-6">
      <PageHeader
        title="Insights"
        description="Key insights and analytics"
      />

      {/* TODO: Customize KPI groups for your domain */}
      <MetricSection title="Overview" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Insight Score" value={88} trend={0.05} unit="score" />
          <KpiCard title="Trend" value={12} trend={0.08} unit="%" />
          <KpiCard title="Engagement" value={75} trend={0.03} unit="%" />
          <KpiCard title="Retention" value={82} trend={0.02} unit="%" />
        </div>
      </MetricSection>

      <MetricSection title="Trends" defaultOpen>
        <ChartCard
          title="Insight Trend"
          description="Insight score over time"
          descriptionTooltip="Shows the trend of your key insights"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockInsightData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>
    </div>
  );
}
