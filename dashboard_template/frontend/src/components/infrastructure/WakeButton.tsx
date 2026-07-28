/**
 * Wake Button Component
 * 
 * Button to wake up sleeping hosting services (e.g., Render free tier).
 * Used in KpiCard action slot.
 */

import { useState } from "react";

interface WakeButtonProps {
  onWake: () => Promise<void>;
  isWaking?: boolean;
}

export function WakeButton({ onWake, isWaking = false }: WakeButtonProps) {
  const [localWaking, setLocalWaking] = useState(false);

  const handleClick = async () => {
    setLocalWaking(true);
    try {
      await onWake();
    } finally {
      setLocalWaking(false);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={localWaking || isWaking}
      className="rounded bg-blue-600 px-3 py-1 text-sm text-white hover:bg-blue-700 disabled:bg-gray-400"
    >
      {localWaking || isWaking ? "Waking..." : "Wake"}
    </button>
  );
}
