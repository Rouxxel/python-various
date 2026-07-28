/**
 * useFeatures Hook
 * 
 * Hook for fetching and managing feature flags.
 */

import { useQuery } from "@tanstack/react-query";
import { fetchFeatures, type Features } from "../lib/api";

export function useFeatures() {
  const {
    data: features,
    isLoading,
    error,
  } = useQuery<Features>({
    queryKey: ["features"],
    queryFn: fetchFeatures,
    refetchInterval: 60000, // Refresh every minute
  });

  return {
    features,
    isLoading,
    error,
    dataMode: features?.data_mode,
    isMockMode: features?.data_mode === "mock",
  };
}
