import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  RouterProvider,
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from "@tanstack/react-router";
import { Sidebar } from "./components/Sidebar";
import { DevBanner } from "./components/DevBanner";
import { DataEnvironmentProvider } from "./hooks/useDataEnvironment";
import { templateConfig } from "../template.config";
import "./index.css";

import OverviewPage from "./routes/overview";
import MetricsPage from "./routes/metrics";
import ChartsPage from "./routes/charts";
import TablesPage from "./routes/tables";
import UsersPage from "./routes/users";
import SessionsPage from "./routes/sessions";
import ActivityPage from "./routes/activity";
import CostsPage from "./routes/costs";
import AiPage from "./routes/ai";
import InfrastructurePage from "./routes/infrastructure";
import InsightsPage from "./routes/insights";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
    },
  },
});

function RootLayout() {
  React.useEffect(() => {
    document.title = templateConfig.projectName;
  }, []);

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <DevBanner />
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

const rootRoute = createRootRoute({
  component: RootLayout,
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({ to: "/overview" });
  },
});

const routeDefinitions = [
  { path: "/overview", component: OverviewPage },
  { path: "/metrics", component: MetricsPage },
  { path: "/charts", component: ChartsPage },
  { path: "/tables", component: TablesPage },
  { path: "/users", component: UsersPage },
  { path: "/sessions", component: SessionsPage },
  { path: "/activity", component: ActivityPage },
  { path: "/costs", component: CostsPage },
  { path: "/ai", component: AiPage },
  { path: "/infrastructure", component: InfrastructurePage },
  { path: "/insights", component: InsightsPage },
] as const;

const childRoutes = routeDefinitions.map(({ path, component }) =>
  createRoute({
    getParentRoute: () => rootRoute,
    path,
    component,
  })
);

const routeTree = rootRoute.addChildren([indexRoute, ...childRoutes]);

const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <DataEnvironmentProvider>
        <RouterProvider router={router} />
      </DataEnvironmentProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
