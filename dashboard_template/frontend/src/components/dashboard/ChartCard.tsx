import { ReactNode } from "react";

interface ChartCardProps {
  title: string;
  description?: string;
  descriptionTooltip?: string;
  children: ReactNode;
}

export function ChartCard({
  title,
  description,
  descriptionTooltip,
  children,
}: ChartCardProps) {
  return (
    <div className="rounded-lg border bg-white p-4 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-medium text-gray-900">{title}</h3>
        {description && (
          <p className="text-sm text-gray-500" title={descriptionTooltip}>
            {description}
          </p>
        )}
      </div>
      {children}
    </div>
  );
}
