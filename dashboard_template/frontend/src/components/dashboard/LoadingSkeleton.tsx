interface LoadingSkeletonProps {
  type: "card" | "table" | "chart";
}

export function LoadingSkeleton({ type }: LoadingSkeletonProps) {
  const height = type === "chart" ? "h-64" : type === "table" ? "h-48" : "h-24";
  return <div className={`animate-pulse rounded-lg bg-gray-200 ${height}`} />;
}
