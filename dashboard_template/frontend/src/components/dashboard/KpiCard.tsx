import { ReactNode } from "react";

interface KpiCardProps {
  title: string;
  value: number;
  trend?: number;
  unit?: string;
  format?: (value: number) => string;
  action?: ReactNode;
}

export function KpiCard({
  title,
  value,
  trend,
  unit,
  format,
  action,
}: KpiCardProps) {
  const displayValue = format ? format(value) : value.toLocaleString();
  const trendLabel =
    trend !== undefined
      ? `${trend >= 0 ? "+" : ""}${(trend * 100).toFixed(1)}%`
      : null;

  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm font-medium text-gray-500">{title}</p>
        {action}
      </div>
      <p className="mt-2 text-2xl font-semibold text-gray-900">
        {displayValue}
        {unit && !format && (
          <span className="ml-1 text-sm font-normal text-gray-500">{unit}</span>
        )}
      </p>
      {trendLabel && (
        <p
          className={`mt-1 text-sm ${
            (trend ?? 0) >= 0 ? "text-green-600" : "text-red-600"
          }`}
        >
          {trendLabel}
        </p>
      )}
    </div>
  );
}
