/**
 * Sessions Route - Domain Placeholder
 * 
 * REPLACE THIS: This is a template for session/request analytics.
 * Customize session metrics, KPIs, and charts for your specific domain.
 * 
 * TODO:
 * - Update session metrics to match your tracking schema
 * - Customize KPI groups for your session metrics
 * - Add domain-specific charts (session duration, bounce rate, etc.)
 * - Update API calls to use your live data
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { ChartCard } from "../components/dashboard/ChartCard";
import { DataTable } from "../components/dashboard/DataTable";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// TODO: Replace with your actual data fetching
const mockSessionData = [
  { date: "Jan", value: 4200 },
  { date: "Feb", value: 4800 },
  { date: "Mar", value: 5200 },
  { date: "Apr", value: 5800 },
  { date: "May", value: 6200 },
  { date: "Jun", value: 6800 },
];

const mockSessions = [
  { id: 1, user_id: 1, duration: 300, created_at: "2024-01-01T10:00:00" },
  { id: 2, user_id: 2, duration: 450, created_at: "2024-01-01T11:00:00" },
  { id: 3, user_id: 1, duration: 200, created_at: "2024-01-02T09:00:00" },
  { id: 4, user_id: 3, duration: 350, created_at: "2024-01-02T14:00:00" },
  { id: 5, user_id: 4, duration: 280, created_at: "2024-01-03T10:00:00" },
];

export default function Sessions() {
  // TODO: Uncomment when API is ready
  // const { dateRange } = useDateRange();
  // const { data: sessionsData, isLoading } = useSessions(dateRange.from, dateRange.to);

  return (
    <div className="p-6">
      <PageHeader
        title="Sessions"
        description="Session and request analytics"
      />

      {/* TODO: Customize KPI groups for your domain */}
      <MetricSection title="Session Overview" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Total Sessions" value={6800} trend={0.12} unit="sessions" />
          <KpiCard title="Avg Duration" value={316} trend={0.05} unit="seconds" />
          <KpiCard title="Bounce Rate" value={35.0} trend={-0.08} unit="%" />
          <KpiCard title="Pages/Session" value={4.2} trend={0.03} unit="pages" />
        </div>
      </MetricSection>

      <MetricSection title="Session Trend" defaultOpen>
        <ChartCard
          title="Sessions Over Time"
          description="Session volume trend"
          descriptionTooltip="Shows the trend of sessions over time"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockSessionData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Recent Sessions" defaultOpen>
        <DataTable
          columns={[
            { id: "id", header: "ID" },
            { id: "user_id", header: "User ID" },
            { id: "duration", header: "Duration (s)" },
            { id: "created_at", header: "Created" },
          ]}
          data={mockSessions}
          exportable
          emptyMessage="No sessions found in the selected time range"
        />
      </MetricSection>
    </div>
  );
}
