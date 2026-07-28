import { ReactNode, useState } from "react";

interface MetricSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
  defaultOpen?: boolean;
  onRefresh?: () => Promise<void>;
  isLoading?: boolean;
  refreshable?: boolean;
}

export function MetricSection({
  title,
  description,
  children,
  defaultOpen = true,
  onRefresh,
  isLoading = false,
  refreshable = false,
}: MetricSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  const handleRefresh = async () => {
    if (onRefresh) {
      await onRefresh();
    }
  };

  return (
    <section className="mb-8 rounded-lg border bg-white shadow-sm">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <div>
          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            className="text-left text-lg font-medium text-gray-900"
          >
            {title}
          </button>
          {description && (
            <p className="mt-1 text-sm text-gray-500">{description}</p>
          )}
        </div>
        {refreshable && (
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isLoading}
            className="rounded border px-3 py-1 text-sm hover:bg-gray-50 disabled:opacity-50"
          >
            {isLoading ? "Refreshing..." : "Refresh"}
          </button>
        )}
      </div>
      {open && <div className="p-4">{children}</div>}
    </section>
  );
}
