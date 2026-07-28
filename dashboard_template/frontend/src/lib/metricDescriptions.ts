/**
 * Metric Descriptions
 * 
 * Replace these placeholder descriptions with your business-specific metric definitions.
 * Each metric can include title, description, formula, and guidance on good/bad values.
 */

export interface MetricDescription {
  title: string;
  description: string;
  formula?: string;
  good?: string;
  bad?: string;
}

export const metricDescriptions: Record<string, MetricDescription> = {
  // Overview metrics
  totalUsers: {
    title: "Total Users",
    description: "Total number of registered user accounts in your system",
    formula: "COUNT(users.id)",
    good: "Growing month over month",
    bad: "Declining or stagnant"
  },
  activeUsers: {
    title: "Active Users",
    description: "Number of users who have engaged with your app in the selected time period",
    formula: "COUNT(users WHERE last_activity >= time_period_start)",
    good: "High percentage of total users",
    bad: "Low engagement rate"
  },
  growthRate: {
    title: "Growth Rate",
    description: "Percentage change in user count compared to previous period",
    formula: "(current_users - previous_users) / previous_users * 100",
    good: "Positive and sustainable",
    bad: "Negative or volatile"
  },
  
  // Session metrics
  totalSessions: {
    title: "Total Sessions",
    description: "Total number of user sessions in the selected time period",
    formula: "COUNT(sessions.id)",
    good: "Consistent with user activity",
    bad: "Unexpected spikes or drops"
  },
  avgSessionDuration: {
    title: "Average Session Duration",
    description: "Average time users spend in a session",
    formula: "SUM(session_duration) / COUNT(sessions)",
    good: "Indicates engaging experience",
    bad: "May indicate UX issues"
  },
  
  // Activity metrics
  totalEvents: {
    title: "Total Events",
    description: "Total number of tracked events in the selected time period",
    formula: "COUNT(events.id)",
    good: "Consistent with expected usage",
    bad: "May indicate tracking issues"
  },
  
  // Cost metrics
  totalCost: {
    title: "Total Cost",
    description: "Total costs incurred in the selected time period",
    formula: "SUM(cost_amount)",
    good: "Within budget",
    bad: "Exceeding budget"
  },
  costPerUser: {
    title: "Cost Per User",
    description: "Average cost per active user",
    formula: "total_cost / active_users",
    good: "Decreasing over time",
    bad: "Increasing without revenue growth"
  },
  
  // AI/ML metrics (if applicable)
  generationSuccessRate: {
    title: "Generation Success Rate",
    description: "Percentage of successful AI generations",
    formula: "successful_generations / total_generations * 100",
    good: "Above 95%",
    bad: "Below 90%"
  },
  avgLatency: {
    title: "Average Latency",
    description: "Average time for AI generation requests",
    formula: "SUM(latency) / COUNT(requests)",
    good: "Under 2 seconds",
    bad: "Over 5 seconds"
  },
  
  // Infrastructuremetrics
  uptime: {
    title: "Uptime",
    description: "Percentage of time the service has been available",
    formula: "available_time / total_time * 100",
    good: "Above 99.9%",
    bad: "Below 99%"
  },
  responseTime: {
    title: "Average Response Time",
    description: "Average time for API responses",
    formula: "SUM(response_time) / COUNT(requests)",
    good: "Under 200ms",
    bad: "Over 500ms"
  }
};

export default metricDescriptions;
