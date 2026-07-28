/**
 * Metrics Route - Template Showcase
 * 
 * Demonstrates: KpiCard with different units, KpiGroupSection with formatters
 * Uses mock data only with neutral labels.
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { KpiCard } from "../components/dashboard/KpiCard";
import { KpiGroupSection } from "../components/dashboard/KpiGroupSection";

// Formatters
const fmtPct = (v: number) => `${(v * 100).toFixed(1)}%`;
const fmtUsd = (v: number) => `$${v.toLocaleString()}`;
const fmtSecs = (v: number) => {
  const mins = Math.floor(v / 60);
  const secs = Math.floor(v % 60);
  return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
};

export default function Metrics() {
  return (
    <div className="p-6">
      <PageHeader
        title="Metrics Showcase"
        description="Examples of different metric types and formatters"
      />

      <MetricSection title="Count Metrics" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard title="Total Users" value={2500} trend={0.15} unit="users" />
          <KpiCard title="Sessions" value={4200} trend={0.08} unit="sessions" />
          <KpiCard title="Events" value={15000} trend={0.12} unit="events" />
          <KpiCard title="Requests" value={50000} trend={0.05} unit="requests" />
        </div>
      </MetricSection>

      <MetricSection title="Percentage Metrics" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard title="Growth Rate" value={15.0} trend={0.02} unit="%" format={fmtPct} />
          <KpiCard title="Retention" value={72.0} trend={0.05} unit="%" format={fmtPct} />
          <KpiCard title="Success Rate" value={98.5} trend={0.01} unit="%" format={fmtPct} />
          <KpiCard title="Uptime" value={99.9} trend={0.0} unit="%" format={fmtPct} />
        </div>
      </MetricSection>

      <MetricSection title="Currency Metrics" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard title="Revenue" value={52000} trend={0.12} unit="USD" format={fmtUsd} />
          <KpiCard title="Costs" value={4500} trend={-0.05} unit="USD" format={fmtUsd} />
          <KpiCard title="Profit" value={47500} trend={0.15} unit="USD" format={fmtUsd} />
          <KpiCard title="ARPU" value={20.8} trend={0.03} unit="USD" format={fmtUsd} />
        </div>
      </MetricSection>

      <MetricSection title="Time Metrics" defaultOpen>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KpiCard title="Avg Session" value={300} trend={0.08} unit="seconds" format={fmtSecs} />
          <KpiCard title="Response Time" value={150} trend={-0.10} unit="ms" />
          <KpiCard title="Load Time" value={1.2} trend={-0.15} unit="seconds" />
          <KpiCard title="Uptime" value={99.9} trend={0.0} unit="%" format={fmtPct} />
        </div>
      </MetricSection>

      <MetricSection title="Grouped Metrics" defaultOpen>
        <KpiGroupSection
          title="User Engagement"
          metrics={[
            { label: "Daily Active", value: 500, unit: "users" },
            { label: "Weekly Active", value: 1200, unit: "users" },
            { label: "Monthly Active", value: 2500, unit: "users" },
          ]}
          formatChartValue={(v) => v.toLocaleString()}
        />

        <KpiGroupSection
          title="Session Duration"
          metrics={[
            { label: "Average", value: 300, unit: "seconds" },
            { label: "Median", value: 240, unit: "seconds" },
            { label: "95th Percentile", value: 600, unit: "seconds" },
          ]}
          formatChartValue={fmtSecs}
        />

        <KpiGroupSection
          title="Conversion Funnel"
          metrics={[
            { label: "Views", value: 10000, unit: "views" },
            { label: "Signups", value: 500, unit: "users" },
            { label: "Purchases", value: 50, unit: "purchases" },
          ]}
          formatChartValue={(v) => v.toLocaleString()}
        />
      </MetricSection>
    </div>
  );
}
