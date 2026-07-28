interface MetricItem {
  label: string;
  value: number;
  unit: string;
}

interface KpiGroupSectionProps {
  title: string;
  metrics: MetricItem[];
  formatChartValue?: (value: number) => string;
}

export function KpiGroupSection({
  title,
  metrics,
  formatChartValue = (value) => value.toLocaleString(),
}: KpiGroupSectionProps) {
  return (
    <div>
      <h3 className="mb-3 text-sm font-medium text-gray-700">{title}</h3>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-lg border bg-gray-50 p-4">
            <p className="text-sm text-gray-500">{metric.label}</p>
            <p className="mt-1 text-xl font-semibold">
              {formatChartValue(metric.value)}{" "}
              <span className="text-sm font-normal text-gray-500">
                {metric.unit}
              </span>
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
