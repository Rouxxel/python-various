/**
 * Infrastructure Configuration
 * 
 * Defines which sections appear on the Infrastructure page based on feature flags.
 */

import type { Features } from "./types";

export interface InfrastructureSection {
  id: string;
  title: string;
  description?: string;
  enabled: (features: Features) => boolean;
  priority: number;
}

export const infrastructureSections: InfrastructureSection[] = [
  {
    id: "host-health",
    title: "Host Health",
    description: "Health check for hosting provider",
    enabled: (features) => features.features.host_health,
    priority: 1,
  },
  {
    id: "web-analytics",
    title: "Web Analytics",
    description: "Web traffic and visitor analytics",
    enabled: (features) => features.features.vercel,
    priority: 2,
  },
  {
    id: "deployments",
    title: "Deployments",
    description: "Recent deployment history",
    enabled: (features) => features.features.vercel,
    priority: 3,
  },
  {
    id: "storage",
    title: "Storage",
    description: "Storage bucket metrics",
    enabled: (features) => features.features.storage_metrics,
    priority: 4,
  },
  {
    id: "database",
    title: "Database",
    description: "Database table counts and status",
    enabled: (features) => features.features.supabase,
    priority: 5,
  },
];

export function getEnabledSections(features: Features): InfrastructureSection[] {
  return infrastructureSections
    .filter((section) => section.enabled(features))
    .sort((a, b) => a.priority - b.priority);
}
