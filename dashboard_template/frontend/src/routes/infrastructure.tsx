/**
 * Infrastructure Route
 */

import { PageHeader } from "../components/PageHeader";
import { DatabaseSection } from "../components/infrastructure/DatabaseSection";
import { HostHealthSection } from "../components/infrastructure/HostHealthSection";
import { ProviderSection } from "../components/infrastructure/ProviderSection";
import { LoadingSkeleton } from "../components/dashboard/LoadingSkeleton";
import { useFeatures } from "../hooks/useFeatures";
import { getEnabledSections } from "../lib/infrastructureConfig";
import { useInfrastructure } from "../lib/queries";

export default function InfrastructurePage() {
  const { features, isLoading: featuresLoading } = useFeatures();
  const { data, isLoading, error, refetch, isFetching } = useInfrastructure();

  if (featuresLoading || isLoading) {
    return (
      <div className="p-6">
        <LoadingSkeleton type="chart" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6">
        <PageHeader
          title="Infrastructure"
          description="Provider health, deployments, and database status"
        />
        <p className="text-sm text-red-600">
          Failed to load infrastructure data. Is the backend running on port 8001?
        </p>
      </div>
    );
  }

  const enabledSections = features ? getEnabledSections(features) : [];

  return (
    <div className="p-6">
      <PageHeader
        title="Infrastructure"
        description="Provider modules demo — enable flags in backend/.env for live integrations"
      />

      {data.notes?.length > 0 && (
        <div className="mb-6 rounded-lg border border-yellow-200 bg-yellow-50 p-4 text-sm text-yellow-900">
          <ul className="list-disc space-y-1 pl-5">
            {data.notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </div>
      )}

      {enabledSections.some((section) => section.id === "host-health") && (
        <HostHealthSection data={data} />
      )}

      {enabledSections.some((section) => section.id === "deployments") && (
        <ProviderSection
          title="Deployments"
          items={data.deployments}
          emptyMessage="No deployments. Set FEATURE_VERCEL=true and VERCEL_API_TOKEN."
        />
      )}

      {enabledSections.some((section) => section.id === "storage") && (
        <ProviderSection
          title="Storage"
          items={data.storage}
          emptyMessage="No storage metrics. Set FEATURE_STORAGE_METRICS=true."
        />
      )}

      {enabledSections.some((section) => section.id === "database") && (
        <DatabaseSection data={data} />
      )}

      <button
        type="button"
        onClick={() => refetch()}
        disabled={isFetching}
        className="mt-4 rounded border px-3 py-1 text-sm hover:bg-gray-50 disabled:opacity-50"
      >
        {isFetching ? "Refreshing..." : "Refresh"}
      </button>
    </div>
  );
}
