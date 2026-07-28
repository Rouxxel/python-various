/**
 * Overview Route - Template Showcase
 * 
 * Demonstrates: PageHeader, MetricSection, KpiCard, KpiGroupSection, ChartCard
 * Uses mock data only with neutral labels.
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { KpiGroupSection } from "../components/dashboard/KpiGroupSection";
import { ChartCard } from "../components/dashboard/ChartCard";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const mockGrowthData = [
  { date: "Jan", value: 1000 },
  { date: "Feb", value: 1200 },
  { date: "Mar", value: 1500 },
  { date: "Apr", value: 1800 },
  { date: "May", value: 2100 },
  { date: "Jun", value: 2500 },
];

const mockRevenueData = [
  { date: "Jan", value: 35000 },
  { date: "Feb", value: 38000 },
  { date: "Mar", value: 42000 },
  { date: "Apr", value: 45000 },
  { date: "May", value: 48000 },
  { date: "Jun", value: 52000 },
];

export default function Overview() {
  return (
    <div className="p-6">
      <PageHeader
        title="Overview"
        description="Key metrics and performance indicators for your application"
      />

      <MetricSection title="Key Metrics" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            title="Total Users"
            value={2500}
            trend={0.15}
            unit="users"
          />
          <KpiCard
            title="Active Users"
            value={1250}
            trend={0.08}
            unit="users"
          />
          <KpiCard
            title="Growth Rate"
            value={15.0}
            trend={0.02}
            unit="%"
          />
          <KpiCard
            title="Revenue"
            value={52000}
            trend={0.12}
            unit="USD"
          />
        </div>
      </MetricSection>

      <MetricSection title="Volume Metrics" defaultOpen>
        <KpiGroupSection
          title="Session Volume"
          metrics={[
            { label: "Today", value: 150, unit: "sessions" },
            { label: "Week", value: 1050, unit: "sessions" },
            { label: "Month", value: 4200, unit: "sessions" },
          ]}
          formatChartValue={(v) => `$${v.toLocaleString()}`}
        />
      </MetricSection>

      <MetricSection title="Trends" defaultOpen>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <ChartCard
            title="User Growth"
            description="New user signups over time"
            descriptionTooltip="Shows the trend of new user registrations"
          >
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockGrowthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="Revenue Trend"
            description="Monthly revenue over time"
            descriptionTooltip="Shows revenue growth across months"
          >
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={mockRevenueData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </MetricSection>
    </div>
  );
}
