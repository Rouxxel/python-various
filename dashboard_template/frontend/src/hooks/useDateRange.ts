import { useMemo, useState } from "react";

export interface DateRange {
  from: string;
  to: string;
}

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

export function useDateRange(initialDays = 30) {
  const [dateRange, setDateRange] = useState<DateRange>(() => {
    const to = new Date();
    const from = new Date();
    from.setDate(to.getDate() - initialDays);
    return { from: formatDate(from), to: formatDate(to) };
  });

  const presets = useMemo(
    () => [
      { label: "7 days", days: 7 },
      { label: "30 days", days: 30 },
      { label: "90 days", days: 90 },
    ],
    []
  );

  const applyPreset = (days: number) => {
    const to = new Date();
    const from = new Date();
    from.setDate(to.getDate() - days);
    setDateRange({ from: formatDate(from), to: formatDate(to) });
  };

  return { dateRange, setDateRange, presets, applyPreset };
}
