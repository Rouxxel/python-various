/**
 * Charts Route - Template Showcase
 * 
 * Demonstrates: ChartCard with various chart types (Line, Bar, Area, Pie)
 * Uses mock data only with neutral labels.
 */

import { PageHeader } from "../components/PageHeader";
import { MetricSection } from "../components/dashboard/MetricSection";
import { ChartCard } from "../components/dashboard/ChartCard";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

const mockLineData = [
  { date: "Jan", value: 1000 },
  { date: "Feb", value: 1200 },
  { date: "Mar", value: 1500 },
  { date: "Apr", value: 1800 },
  { date: "May", value: 2100 },
  { date: "Jun", value: 2500 },
];

const mockBarData = [
  { category: "Users", value: 2500 },
  { category: "Sessions", value: 4200 },
  { category: "Events", value: 15000 },
  { category: "Requests", value: 50000 },
];

const mockAreaData = [
  { date: "Jan", value1: 1000, value2: 800 },
  { date: "Feb", value1: 1200, value2: 950 },
  { date: "Mar", value1: 1500, value2: 1200 },
  { date: "Apr", value1: 1800, value2: 1400 },
  { date: "May", value1: 2100, value2: 1650 },
  { date: "Jun", value1: 2500, value2: 1900 },
];

const mockPieData = [
  { name: "Desktop", value: 400 },
  { name: "Mobile", value: 300 },
  { name: "Tablet", value: 200 },
  { name: "Other", value: 100 },
];

export default function Charts() {
  return (
    <div className="p-6">
      <PageHeader
        title="Charts Showcase"
        description="Examples of different chart types and configurations"
      />

      <MetricSection title="Line Charts" defaultOpen>
        <ChartCard
          title="Growth Over Time"
          description="Trend line showing growth"
          descriptionTooltip="Line charts are best for showing trends over time"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={mockLineData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Bar Charts" defaultOpen>
        <ChartCard
          title="Category Comparison"
          description="Bar chart comparing categories"
          descriptionTooltip="Bar charts are best for comparing values across categories"
        >
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockBarData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Area Charts" defaultOpen>
        <ChartCard
          title="Multi-series Comparison"
          description="Area chart comparing two metrics"
          descriptionTooltip="Area charts are best for showing volume and comparing multiple series"
        >
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={mockAreaData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="value1" stackId="1" stroke="#3b82f6" fill="#3b82f6" />
              <Area type="monotone" dataKey="value2" stackId="1" stroke="#10b981" fill="#10b981" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>

      <MetricSection title="Pie Charts" defaultOpen>
        <ChartCard
          title="Distribution"
          description="Pie chart showing distribution"
          descriptionTooltip="Pie charts are best for showing parts of a whole"
        >
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={mockPieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {mockPieData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </MetricSection>
    </div>
  );
}
