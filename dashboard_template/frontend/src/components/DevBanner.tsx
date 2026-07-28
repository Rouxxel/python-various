/**
 * DevBanner Component
 * 
 * Development banner showing data mode and disabled features.
 */

import { useQuery } from "@tanstack/react-query";
import { fetchFeatures } from "../lib/api";

export function DevBanner() {
  const { data: features } = useQuery({
    queryKey: ["features"],
    queryFn: fetchFeatures,
    refetchInterval: 60000, // Refresh every minute
  });

  if (!features || import.meta.env.PROD) {
    return null;
  }

  const disabledFeatures = Object.entries(features.features)
    .filter(([_, enabled]) => !enabled)
    .map(([name]) => name);

  return (
    <div className="border-b bg-yellow-50 px-4 py-2 text-sm">
      <div className="flex items-center gap-4">
        <span className="font-medium text-yellow-800">
          {features.data_mode === "mock" ? "Mock data mode" : "Live data mode"}
        </span>
        {disabledFeatures.length > 0 && (
          <span className="text-yellow-700">
            Disabled: {disabledFeatures.join(", ")}
          </span>
        )}
        {features.hosting_provider !== "none" && (
          <span className="text-yellow-700">
            Hosting: {features.hosting_provider}
          </span>
        )}
      </div>
    </div>
  );
}
