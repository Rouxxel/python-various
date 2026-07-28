/**
 * Query Hooks
 * 
 * React Query hooks for API calls, aligned with feature flags.
 */

import { useQuery } from "@tanstack/react-query";
import { useFeatures } from "../hooks/useFeatures";
import {
  fetchOverview,
  fetchUsers,
  fetchSessions,
  fetchActivity,
  fetchInfrastructure,
  fetchCosts,
  fetchAiMetrics,
} from "./api";

export function useOverview(from: string, to: string) {
  return useQuery({
    queryKey: ["overview", from, to],
    queryFn: () => fetchOverview(from, to),
  });
}

export function useUsers(from: string, to: string) {
  return useQuery({
    queryKey: ["users", from, to],
    queryFn: () => fetchUsers(from, to),
  });
}

export function useSessions(from: string, to: string) {
  return useQuery({
    queryKey: ["sessions", from, to],
    queryFn: () => fetchSessions(from, to),
  });
}

export function useActivity(from: string, to: string) {
  return useQuery({
    queryKey: ["activity", from, to],
    queryFn: () => fetchActivity(from, to),
  });
}

export function useInfrastructure() {
  return useQuery({
    queryKey: ["infrastructure"],
    queryFn: fetchInfrastructure,
  });
}

export function useCosts(from: string, to: string) {
  const { features } = useFeatures();
  
  return useQuery({
    queryKey: ["costs", from, to],
    queryFn: () => fetchCosts(from, to),
    enabled: features?.features.costs_module ?? true,
  });
}

export function useAiMetrics(from: string, to: string) {
  return useQuery({
    queryKey: ["ai", from, to],
    queryFn: () => fetchAiMetrics(from, to),
  });
}
