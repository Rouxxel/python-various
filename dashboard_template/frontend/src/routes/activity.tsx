/**
 * Activity Route - Domain Placeholder
 * 
 * REPLACE THIS: This is a template for activity/events analytics.
 * Customize event types, KPIs, and charts for your specific domain.
 * 
 * TODO:
 * - Update event types to match your tracking schema
 * - Customize KPI groups for your activity metrics
 * - Add domain-specific charts (funnels, cohorts, etc.)
 * - Update API calls to use your live data
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { ChartCard } from "../components/dashboard/ChartCard";
import { DataTable } from "../components/dashboard/DataTable";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// TODO: Replace with your actual data fetching
const mockEventsByType = [
  { type: "page_view", count: 5000 },
  { type: "click", count: 3200 },
  { type: "form_submit", count: 450 },
  { type: "user_signup", count: 130 },
  { type: "purchase", count: 85 },
];

const mockEvents = [
  { id: 1, event_type: "user_signup", user_id: 1, description: "New user registered", created_at: "2024-01-01T10:00:00" },
  { id: 2, event_type: "page_view", user_id: 1, description: "Viewed /dashboard", created_at: "2024-01-01T10:05:00" },
  { id: 3, event_type: "click", user_id: 1, description: "Clicked 'Export' button", created_at: "2024-01-01T10:10:00" },
  { id: 4, event_type: "deploy", user_id: null, description: "Deployment #1234", created_at: "2024-01-01T11:00:00" },
  { id: 5, event_type: "error", user_id: 2, description: "API timeout", created_at: "2024-01-01T12:00:00" },
];

export default function Activity() {
  // TODO: Uncomment when API is ready
  // const { dateRange } = useDateRange();
  // const { data: activityData, isLoading } = useActivity(dateRange.from, dateRange.to);

  return (
    <div className="p-6">
      <PageHeader
        title="Activity"
        description="Events and user activity tracking"
      />

      {/* TODO: Customize KPI groups for your domain */}
      <MetricSection title="Event Overview" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Total Events" value={8885} trend={0.12} unit="events" />
          <KpiCard title="Unique Users" value={420} trend={0.08} unit="users" />
          <KpiCard title="Avg Events/User" value={21.1} trend={0.05} unit="events" />
          <KpiCard title="Error Rate" value={0.5} trend={-0.15} unit="%" />
        </div>
      </MetricSection>

      <MetricSection title="Events by Type" defaultOpen>
        <ChartCard
          title="Event Distribution"
          description="Breakdown of events by type"
          descriptionTooltip="Shows which event types are most common"
        >
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockEventsByType} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="type" type="category" width={100} />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Recent Events" defaultOpen>
        <DataTable
          columns={[
            { id: "id", header: "ID" },
            { id: "event_type", header: "Event Type" },
            { id: "description", header: "Description" },
            { id: "user_id", header: "User ID" },
            { id: "created_at", header: "Created" },
          ]}
          data={mockEvents}
          exportable
          emptyMessage="No events found in the selected time range"
        />
      </MetricSection>
    </div>
  );
}
