/**
 * Sidebar Component
 * 
 * Navigation sidebar powered by templateConfig.navItems.
 * Filters items by enabled status and highlights active route.
 */

import { Link, useLocation } from "@tanstack/react-router";
import { cn } from "../lib/utils";
import { templateConfig } from "../../template.config";

export function Sidebar() {
  const location = useLocation();
  const navItems = templateConfig.navItems.filter((item) => item.enabled);

  // Group nav items by category
  const showcaseItems = navItems.filter((item) => item.category === "showcase");
  const domainItems = navItems.filter((item) => item.category === "domain");
  const infrastructureItems = navItems.filter((item) => item.category === "infrastructure");
  const otherItems = navItems.filter((item) => !item.category);

  return (
    <div className="flex h-full w-64 flex-col border-r bg-gray-50">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-lg font-semibold">{templateConfig.projectName}</h1>
      </div>
      <nav className="flex-1 space-y-4 p-4">
        {showcaseItems.length > 0 && (
          <div>
            <h3 className="mb-2 px-3 text-xs font-semibold uppercase text-gray-500">
              Template Showcase
            </h3>
            <div className="space-y-1">
              {showcaseItems.map((item) => (
                <SidebarItem key={item.id} item={item} location={location} />
              ))}
            </div>
          </div>
        )}

        {domainItems.length > 0 && (
          <div>
            <h3 className="mb-2 px-3 text-xs font-semibold uppercase text-gray-500">
              Your Domain
            </h3>
            <div className="space-y-1">
              {domainItems.map((item) => (
                <SidebarItem key={item.id} item={item} location={location} />
              ))}
            </div>
          </div>
        )}

        {infrastructureItems.length > 0 && (
          <div>
            <h3 className="mb-2 px-3 text-xs font-semibold uppercase text-gray-500">
              Infrastructure
            </h3>
            <div className="space-y-1">
              {infrastructureItems.map((item) => (
                <SidebarItem key={item.id} item={item} location={location} />
              ))}
            </div>
          </div>
        )}

        {otherItems.length > 0 && (
          <div className="space-y-1">
            {otherItems.map((item) => (
              <SidebarItem key={item.id} item={item} location={location} />
            ))}
          </div>
        )}
      </nav>
      <div className="border-t p-4">
        <div className="text-xs text-gray-500">
          Template v1.0.0
        </div>
      </div>
    </div>
  );
}

function SidebarItem({ item, location }: { item: any; location: any }) {
  const isActive = location.pathname === item.path;
  return (
    <Link
      key={item.id}
      to={item.path}
      className={cn(
        "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
        isActive
          ? "bg-white text-gray-900 shadow-sm"
          : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
      )}
    >
      {item.label}
    </Link>
  );
}
