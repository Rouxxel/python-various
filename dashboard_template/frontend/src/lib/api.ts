/**
 * API Client
 * 
 * Centralized API client functions for backend communication.
 */

const API_URL = import.meta.env.VITE_DASHBOARD_API_URL || "http://localhost:8001";

export interface FeaturesResponse {
  data_mode: "mock" | "live";
  features: {
    supabase: boolean;
    vercel: boolean;
    host_health: boolean;
    storage_metrics: boolean;
    costs_module: boolean;
    test_prod_switch: boolean;
    datadog?: boolean;
    private_database?: boolean;
  };
  hosting_provider: string;
}

export type Features = FeaturesResponse;

export async function fetchFeatures(): Promise<FeaturesResponse> {
  const response = await fetch(`${API_URL}/api/config/features`);
  if (!response.ok) {
    throw new Error("Failed to fetch features");
  }
  return response.json();
}

export interface OverviewResponse {
  total_users: number;
  active_users: number;
  growth_rate: number;
  revenue: number;
  metrics: Array<{
    title: string;
    value: number;
    trend: number;
    unit: string;
  }>;
  charts: {
    growth_over_time: Array<{ date: string; value: number }>;
    revenue_trend: Array<{ date: string; value: number }>;
  };
}

export async function fetchOverview(from: string, to: string): Promise<OverviewResponse> {
  const response = await fetch(`${API_URL}/api/overview?from_date=${from}&to_date=${to}`);
  if (!response.ok) {
    throw new Error("Failed to fetch overview");
  }
  return response.json();
}

export interface UsersResponse {
  total_users: number;
  new_users: number;
  active_users: number;
  retention_rate: number;
  metrics: Array<{
    title: string;
    value: number;
    trend: number;
    unit: string;
  }>;
  charts: {
    user_growth: Array<{ date: string; value: number }>;
  };
  table: Array<{
    id: number;
    name: string;
    email: string;
    status: string;
    created_at: string;
  }>;
}

export async function fetchUsers(from: string, to: string): Promise<UsersResponse> {
  const response = await fetch(`${API_URL}/api/users?from_date=${from}&to_date=${to}`);
  if (!response.ok) {
    throw new Error("Failed to fetch users");
  }
  return response.json();
}

export interface SessionsResponse {
  total_sessions: number;
  avg_duration: number;
  metrics: Array<{
    title: string;
    value: number;
    trend: number;
    unit: string;
  }>;
  charts: {
    sessions_over_time: Array<{ date: string; value: number }>;
  };
  table: Array<{
    id: number;
    user_id: number;
    duration: number;
    created_at: string;
  }>;
}

export async function fetchSessions(from: string, to: string): Promise<SessionsResponse> {
  const response = await fetch(`${API_URL}/api/sessions?from_date=${from}&to_date=${to}`);
  if (!response.ok) {
    throw new Error("Failed to fetch sessions");
  }
  return response.json();
}

export interface ActivityResponse {
  total_events: number;
  events_by_type: Record<string, number>;
  timeline: Array<{
    timestamp: string;
    event_type: string;
    user_id: number | null;
    description: string;
  }>;
  table: Array<{
    id: number;
    event_type: string;
    user_id: number | null;
    created_at: string;
  }>;
}

export async function fetchActivity(from: string, to: string): Promise<ActivityResponse> {
  const response = await fetch(`${API_URL}/api/activity?from_date=${from}&to_date=${to}`);
  if (!response.ok) {
    throw new Error("Failed to fetch activity");
  }
  return response.json();
}

export interface InfrastructureResponse {
  host_health: {
    status: string;
    response_time: number;
    uptime: number;
  };
  deployments: any[];
  storage: any[];
  database: {
    tables: Array<{
      name: string;
      row_count: number;
    }>;
  };
  notes: string[];
}

export async function fetchInfrastructure(): Promise<InfrastructureResponse> {
  const response = await fetch(`${API_URL}/api/infrastructure`);
  if (!response.ok) {
    throw new Error("Failed to fetch infrastructure");
  }
  return response.json();
}

export interface CostsResponse {
  total_cost: number;
  cost_by_category: Record<string, number>;
  unit_economics: Record<string, number>;
  projections: Array<{
    month: string;
    projected: number;
    actual: number | null;
  }>;
  notes: string[];
}

export async function fetchCosts(from: string, to: string): Promise<CostsResponse> {
  const response = await fetch(`${API_URL}/api/costs?from_date=${from}&to_date=${to}`);
  if (!response.ok) {
    throw new Error("Failed to fetch costs");
  }
  return response.json();
}

export interface AiMetricsResponse {
  total_generations: number;
  success_rate: number;
  avg_latency: number;
  token_usage: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  charts: {
    generations_over_time: Array<{ date: string; value: number }>;
    latency_trend: Array<{ date: string; value: number }>;
  };
  notes: string[];
}

export async function fetchAiMetrics(from: string, to: string): Promise<AiMetricsResponse> {
  const response = await fetch(`${API_URL}/api/ai?from_date=${from}&to_date=${to}`);
  if (!response.ok) {
    throw new Error("Failed to fetch AI metrics");
  }
  return response.json();
}
