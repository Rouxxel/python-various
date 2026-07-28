/**
 * AI Metrics Route - Domain Placeholder
 * 
 * REPLACE THIS: This is a template for AI/ML metrics analytics.
 * Customize metrics, models, and charts for your specific AI use cases.
 * 
 * TODO:
 * - Update metrics to match your AI/ML operations
 * - Add model-specific tracking (if multiple models)
 * - Add domain-specific charts (latency distribution, error rates, etc.)
 * - Update API calls to use your live data
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { ChartCard } from "../components/dashboard/ChartCard";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// TODO: Replace with your actual data fetching
const mockGenerationsData = [
  { date: "Jan", value: 5000 },
  { date: "Feb", value: 6200 },
  { date: "Mar", value: 7800 },
  { date: "Apr", value: 9100 },
  { date: "May", value: 10500 },
  { date: "Jun", value: 12000 },
];

const mockLatencyData = [
  { date: "Jan", value: 850 },
  { date: "Feb", value: 820 },
  { date: "Mar", value: 790 },
  { date: "Apr", value: 760 },
  { date: "May", value: 740 },
  { date: "Jun", value: 720 },
];

export default function AiMetrics() {
  // TODO: Uncomment when API is ready
  // const { dateRange } = useDateRange();
  // const { data: aiData, isLoading } = useAiMetrics(dateRange.from, dateRange.to);

  return (
    <div className="p-6">
      <PageHeader
        title="AI Metrics"
        description="AI/ML generation metrics and performance"
      />

      {/* TODO: Customize KPI groups for your domain */}
      <MetricSection title="Generation Overview" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Total Generations" value={12000} trend={0.15} unit="generations" />
          <KpiCard title="Success Rate" value={98.5} trend={0.01} unit="%" />
          <KpiCard title="Avg Latency" value={720} trend={-0.05} unit="ms" />
          <KpiCard title="Total Tokens" value={2400000} trend={0.12} unit="tokens" />
        </div>
      </MetricSection>

      <MetricSection title="Token Usage" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <KpiCard title="Input Tokens" value={1440000} trend={0.14} unit="tokens" />
          <KpiCard title="Output Tokens" value={960000} trend={0.10} unit="tokens" />
          <KpiCard title="Cost per 1K Tokens" value={0.02} trend={0.0} unit="USD" />
        </div>
      </MetricSection>

      <MetricSection title="Generations Over Time" defaultOpen>
        <ChartCard
          title="Generation Trend"
          description="AI generations over time"
          descriptionTooltip="Shows the trend of AI generation requests"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockGenerationsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Latency Trend" defaultOpen>
        <ChartCard
          title="Response Latency"
          description="Average response time over time"
          descriptionTooltip="Shows the trend of AI model response times"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockLatencyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>
    </div>
  );
}
