/**
 * EnvironmentSwitcher Component
 * 
 * Switch between test and production environments.
 * Only shown when feature_test_prod_switch is enabled.
 */

import { useFeatures } from "../hooks/useFeatures";

export function EnvironmentSwitcher() {
  const { features } = useFeatures();

  // Hide if feature is disabled
  if (!features?.features.test_prod_switch) {
    return null;
  }

  return (
    <div className="flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm">
      <span className="text-gray-600">Environment:</span>
      <select className="rounded border border-gray-300 px-2 py-1 text-sm">
        <option value="test">Test</option>
        <option value="prod">Production</option>
      </select>
    </div>
  );
}
