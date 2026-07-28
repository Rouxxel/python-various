/**
 * Host Health Section Component
 * 
 * Displays hosting provider health check status.
 */

import { KpiCard } from "../dashboard/KpiCard";
import { MetricSection } from "../dashboard/MetricSection";
import { ChartCard } from "../dashboard/ChartCard";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface HostHealthSectionProps {
  data: {
    host_health: {
      status: string;
      response_time: number;
      uptime: number;
    };
    notes: string[];
  };
}

const mockUptimeData = [
  { time: "00:00", uptime: 99.9 },
  { time: "04:00", uptime: 99.8 },
  { time: "08:00", uptime: 99.9 },
  { time: "12:00", uptime: 100.0 },
  { time: "16:00", uptime: 99.9 },
  { time: "20:00", uptime: 99.8 },
];

export function HostHealthSection({ data }: HostHealthSectionProps) {
  const { host_health, notes } = data;

  return (
    <MetricSection title="Host Health" defaultOpen>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <KpiCard
          title="Status"
          value={host_health.status === "healthy" ? 1 : 0}
          unit={host_health.status}
          format={(v) => (v === 1 ? "Healthy" : "Unhealthy")}
        />
        <KpiCard
          title="Response Time"
          value={host_health.response_time}
          unit="ms"
        />
        <KpiCard
          title="Uptime"
          value={host_health.uptime}
          unit="%"
        />
      </div>

      <ChartCard
        title="Uptime Trend"
        description="Host uptime over last 24 hours"
        descriptionTooltip="Shows uptime percentage over time"
      >
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={mockUptimeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis domain={[99, 100]} />
            <Tooltip />
            <Line type="monotone" dataKey="uptime" stroke="#10b981" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      {notes.length > 0 && (
        <div className="mt-4 rounded-lg bg-blue-50 p-4 text-sm text-blue-800">
          <strong>Note:</strong> {notes.join(" ")}
        </div>
      )}
    </MetricSection>
  );
}
