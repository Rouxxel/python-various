/**
 * Database Section Component
 * 
 * Displays database table counts and status.
 */

import { MetricSection } from "../dashboard/MetricSection";
import { DataTable } from "../dashboard/DataTable";

interface DatabaseSectionProps {
  data: {
    database: {
      tables: Array<{
        name: string;
        row_count: number;
      }>;
    };
    notes: string[];
  };
}

export function DatabaseSection({ data }: DatabaseSectionProps) {
  const { database, notes } = data;

  return (
    <MetricSection title="Database" defaultOpen>
      <DataTable
        columns={[
          { id: "name", header: "Table Name" },
          { id: "row_count", header: "Row Count" },
        ]}
        data={database.tables}
        exportable
      />

      {notes.length > 0 && (
        <div className="mt-4 rounded-lg bg-blue-50 p-4 text-sm text-blue-800">
          <strong>Note:</strong> {notes.join(" ")}
        </div>
      )}
    </MetricSection>
  );
}
