/**
 * TypeScript Types
 * 
 * Type definitions matching backend Pydantic models.
 * These must be kept in sync with backend models.
 */

export interface Metric {
  title: string;
  value: number;
  trend: number;
  unit: string;
}

export interface ChartDataPoint {
  date: string;
  value: number;
}

export interface OverviewData {
  total_users: number;
  active_users: number;
  growth_rate: number;
  revenue: number;
  metrics: Metric[];
  charts: {
    growth_over_time: ChartDataPoint[];
    revenue_trend: ChartDataPoint[];
  };
}

export interface UserData {
  total_users: number;
  new_users: number;
  active_users: number;
  retention_rate: number;
  metrics: Metric[];
  charts: {
    user_growth: ChartDataPoint[];
  };
  table: UserTableRow[];
}

export interface UserTableRow {
  id: number;
  name: string;
  email: string;
  status: string;
  created_at: string;
}

export interface SessionData {
  total_sessions: number;
  avg_duration: number;
  metrics: Metric[];
  charts: {
    sessions_over_time: ChartDataPoint[];
  };
  table: SessionTableRow[];
}

export interface SessionTableRow {
  id: number;
  user_id: number;
  duration: number;
  created_at: string;
}

export interface ActivityData {
  total_events: number;
  events_by_type: Record<string, number>;
  timeline: ActivityTimelineItem[];
  table: ActivityTableRow[];
}

export interface ActivityTimelineItem {
  timestamp: string;
  event_type: string;
  user_id: number | null;
  description: string;
}

export interface ActivityTableRow {
  id: number;
  event_type: string;
  user_id: number | null;
  created_at: string;
}

export interface InfrastructureData {
  host_health: {
    status: string;
    response_time: number;
    uptime: number;
  };
  deployments: any[];
  storage: any[];
  database: {
    tables: DatabaseTable[];
  };
  notes: string[];
}

export interface DatabaseTable {
  name: string;
  row_count: number;
}

export interface CostsData {
  total_cost: number;
  cost_by_category: Record<string, number>;
  unit_economics: Record<string, number>;
  projections: CostProjection[];
  notes: string[];
}

export interface CostProjection {
  month: string;
  projected: number;
  actual: number | null;
}

export interface AiMetricsData {
  total_generations: number;
  success_rate: number;
  avg_latency: number;
  token_usage: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  charts: {
    generations_over_time: ChartDataPoint[];
    latency_trend: ChartDataPoint[];
  };
  notes: string[];
}

export interface Features {
  data_mode: "mock" | "live";
  features: {
    supabase: boolean;
    vercel: boolean;
    host_health: boolean;
    storage_metrics: boolean;
    costs_module: boolean;
    test_prod_switch: boolean;
  };
  hosting_provider: string;
}
