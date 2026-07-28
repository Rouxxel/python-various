/**
 * Generic Provider Section Component
 */

import { MetricSection } from "../dashboard/MetricSection";
import { DataTable } from "../dashboard/DataTable";

interface ProviderSectionProps {
  title: string;
  description?: string;
  items?: Array<Record<string, unknown>>;
  emptyMessage?: string;
  data?: {
    deployments?: Array<Record<string, unknown>>;
    storage?: Array<Record<string, unknown>>;
    metrics?: Array<{ label: string; value: number; unit: string }>;
  };
  notes?: string[];
}

export function ProviderSection({
  title,
  description,
  items,
  emptyMessage = "No data available",
  data,
  notes = [],
}: ProviderSectionProps) {
  const rows = items ?? data?.deployments ?? data?.storage ?? [];

  return (
    <MetricSection title={title} description={description} defaultOpen>
      {rows.length > 0 ? (
        <DataTable
          columns={Object.keys(rows[0]).map((key) => ({
            id: key,
            header: key.replace(/_/g, " "),
          }))}
          data={rows}
          exportable
        />
      ) : (
        <p className="text-sm text-gray-500">{emptyMessage}</p>
      )}

      {notes.length > 0 && (
        <div className="mt-4 rounded-lg bg-blue-50 p-4 text-sm text-blue-800">
          <strong>Note:</strong> {notes.join(" ")}
        </div>
      )}
    </MetricSection>
  );
}
