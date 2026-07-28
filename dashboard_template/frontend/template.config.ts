/**
 * Template Configuration
 *
 * Central configuration for the dashboard template.
 * Customize projectName, navItems, and other settings for your project.
 */

export interface NavItem {
  id: string;
  label: string;
  path: string;
  enabled: boolean;
  category?: "showcase" | "domain" | "infrastructure";
}

export interface TemplateConfig {
  projectName: string;
  templateVersion: string;
  navItems: NavItem[];
  features: {
    testProdSwitch: boolean;
  };
}

export const templateConfig: TemplateConfig = {
  projectName: "Analytics Dashboard",
  templateVersion: "1.0.0",

  navItems: [
    {
      id: "overview",
      label: "Overview",
      path: "/overview",
      enabled: true,
      category: "showcase",
    },
    {
      id: "metrics",
      label: "Metrics",
      path: "/metrics",
      enabled: true,
      category: "showcase",
    },
    {
      id: "charts",
      label: "Charts",
      path: "/charts",
      enabled: true,
      category: "showcase",
    },
    {
      id: "tables",
      label: "Tables",
      path: "/tables",
      enabled: true,
      category: "showcase",
    },
    {
      id: "users",
      label: "Users",
      path: "/users",
      enabled: false,
      category: "domain",
    },
    {
      id: "sessions",
      label: "Sessions",
      path: "/sessions",
      enabled: false,
      category: "domain",
    },
    {
      id: "activity",
      label: "Activity",
      path: "/activity",
      enabled: false,
      category: "domain",
    },
    {
      id: "costs",
      label: "Costs",
      path: "/costs",
      enabled: false,
      category: "domain",
    },
    {
      id: "ai",
      label: "AI Metrics",
      path: "/ai",
      enabled: false,
      category: "domain",
    },
    {
      id: "infrastructure",
      label: "Infrastructure",
      path: "/infrastructure",
      enabled: true,
      category: "infrastructure",
    },
  ],

  // UI-only flags; backend feature flags come from GET /api/config/features
  features: {
    testProdSwitch: false,
  },
};

export default templateConfig;
