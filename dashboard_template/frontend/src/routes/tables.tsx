/**
 * Tables Route - Template Showcase
 * 
 * Demonstrates: DataTable with various column types, sorting, filtering
 * Uses mock data only with neutral labels.
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { DataTable } from "../components/dashboard/DataTable";

const mockUsers = [
  { id: 1, name: "User 1", email: "user1@example.com", status: "active", created_at: "2024-01-01" },
  { id: 2, name: "User 2", email: "user2@example.com", status: "active", created_at: "2024-01-02" },
  { id: 3, name: "User 3", email: "user3@example.com", status: "inactive", created_at: "2024-01-03" },
  { id: 4, name: "User 4", email: "user4@example.com", status: "active", created_at: "2024-01-04" },
  { id: 5, name: "User 5", email: "user5@example.com", status: "pending", created_at: "2024-01-05" },
];

const mockSessions = [
  { id: 1, user_id: 1, duration: 300, created_at: "2024-01-01T10:00:00" },
  { id: 2, user_id: 2, duration: 450, created_at: "2024-01-01T11:00:00" },
  { id: 3, user_id: 1, duration: 200, created_at: "2024-01-02T09:00:00" },
  { id: 4, user_id: 3, duration: 350, created_at: "2024-01-02T14:00:00" },
  { id: 5, user_id: 4, duration: 280, created_at: "2024-01-03T10:00:00" },
];

const mockEvents = [
  { id: 1, event_type: "user_signup", user_id: 1, created_at: "2024-01-01T10:00:00" },
  { id: 2, event_type: "page_view", user_id: 1, created_at: "2024-01-01T10:05:00" },
  { id: 3, event_type: "click", user_id: 1, created_at: "2024-01-01T10:10:00" },
  { id: 4, event_type: "deploy", user_id: null, created_at: "2024-01-01T11:00:00" },
  { id: 5, event_type: "error", user_id: 2, created_at: "2024-01-01T12:00:00" },
];

export default function Tables() {
  return (
    <div className="p-6">
      <PageHeader
        title="Tables Showcase"
        description="Examples of data tables with sorting, filtering, and export"
      />

      <MetricSection title="User Table" defaultOpen>
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
                  row.status === "active" ? "bg-green-100 text-green-800" :
                  row.status === "inactive" ? "bg-gray-100 text-gray-800" :
                  "bg-yellow-100 text-yellow-800"
                }`}>
                  {row.status}
                </span>
              )
            },
            { id: "created_at", header: "Created" },
          ]}
          data={mockUsers}
          exportable
        />
      </MetricSection>

      <MetricSection title="Session Table" defaultOpen>
        <DataTable
          columns={[
            { id: "id", header: "ID" },
            { id: "user_id", header: "User ID" },
            { id: "duration", header: "Duration (s)" },
            { id: "created_at", header: "Created" },
          ]}
          data={mockSessions}
          exportable
        />
      </MetricSection>

      <MetricSection title="Events Table" defaultOpen>
        <DataTable
          columns={[
            { id: "id", header: "ID" },
            { id: "event_type", header: "Event Type" },
            { id: "user_id", header: "User ID" },
            { id: "created_at", header: "Created" },
          ]}
          data={mockEvents}
          exportable
          emptyMessage="No events found in the selected time range"
        />
      </MetricSection>

      <MetricSection title="Empty State Example" defaultOpen>
        <DataTable
          columns={[
            { id: "id", header: "ID" },
            { id: "name", header: "Name" },
          ]}
          data={[]}
          emptyMessage="No data available - this demonstrates the empty state"
        />
      </MetricSection>
    </div>
  );
}
