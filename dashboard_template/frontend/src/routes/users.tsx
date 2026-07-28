/**
 * Users Route - Domain Placeholder
 * 
 * REPLACE THIS: This is a template for user analytics.
 * Customize table names, KPIs, and charts for your specific domain.
 * 
 * TODO:
 * - Update table names to match your database schema
 * - Customize KPI groups for your user metrics
 * - Add domain-specific charts
 * - Update API calls to use your live data
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { KpiGroupSection } from "../components/dashboard/KpiGroupSection";
import { ChartCard } from "../components/dashboard/ChartCard";
import { DataTable } from "../components/dashboard/DataTable";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

// TODO: Replace with your actual data fetching
const mockUserGrowthData = [
  { date: "Jan", value: 100 },
  { date: "Feb", value: 150 },
  { date: "Mar", value: 220 },
  { date: "Apr", value: 310 },
  { date: "May", value: 420 },
  { date: "Jun", value: 550 },
];

const mockUsers = [
  { id: 1, name: "User 1", email: "user1@example.com", status: "active", created_at: "2024-01-01" },
  { id: 2, name: "User 2", email: "user2@example.com", status: "active", created_at: "2024-01-02" },
  { id: 3, name: "User 3", email: "user3@example.com", status: "inactive", created_at: "2024-01-03" },
];

export default function Users() {
  // TODO: Uncomment when API is ready
  // const { dateRange } = useDateRange();
  // const { data: usersData, isLoading } = useUsers(dateRange.from, dateRange.to);

  return (
    <div className="p-6">
      <PageHeader
        title="Users"
        description="User analytics and engagement metrics"
      />

      {/* TODO: Customize KPI groups for your domain */}
      <MetricSection title="Registration Overview" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <KpiCard title="Total Users" value={550} trend={0.15} unit="users" />
          <KpiCard title="New Users" value={130} trend={0.08} unit="users" />
          <KpiCard title="Active Users" value={420} trend={0.12} unit="users" />
          <KpiCard title="Retention Rate" value={72.0} trend={0.05} unit="%" />
        </div>
      </MetricSection>

      <MetricSection title="Engagement" defaultOpen>
        <KpiGroupSection
          title="Session Volume"
          metrics={[
            { label: "Today", value: 150, unit: "sessions" },
            { label: "Week", value: 1050, unit: "sessions" },
            { label: "Month", value: 4200, unit: "sessions" },
          ]}
          formatChartValue={(v) => v.toLocaleString()}
        />
      </MetricSection>

      <MetricSection title="User Growth" defaultOpen>
        <ChartCard
          title="User Growth Over Time"
          description="New user registrations"
          descriptionTooltip="Shows trend of new user signups"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockUserGrowthData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="User List" defaultOpen>
        <DataTable
          columns={[
            { id: "id", header: "ID" },
            { id: "name", header: "Name" },
            { id: "email", header: "Email" },
            { 
              id: "status", 
              header: "Status",
              render: (row) => (
                <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                  row.status === "active" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                }`}>
                  {row.status}
                </span>
              )
            },
            { id: "created_at", header: "Created" },
          ]}
          data={mockUsers}
          exportable
          emptyMessage="No users found in the selected time range"
        />
      </MetricSection>
    </div>
  );
}
