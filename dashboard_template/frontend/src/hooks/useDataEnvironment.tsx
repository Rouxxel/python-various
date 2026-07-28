import { createContext, useContext, useMemo, useState, ReactNode } from "react";

type Environment = "test" | "prod";

interface DataEnvironmentContextValue {
  environment: Environment;
  setEnvironment: (env: Environment) => void;
}

const DataEnvironmentContext = createContext<DataEnvironmentContextValue | null>(
  null
);

export function DataEnvironmentProvider({ children }: { children: ReactNode }) {
  const [environment, setEnvironment] = useState<Environment>("test");
  const value = useMemo(
    () => ({ environment, setEnvironment }),
    [environment]
  );
  return (
    <DataEnvironmentContext.Provider value={value}>
      {children}
    </DataEnvironmentContext.Provider>
  );
}

export function useDataEnvironment() {
  const context = useContext(DataEnvironmentContext);
  if (!context) {
    throw new Error("useDataEnvironment must be used within DataEnvironmentProvider");
  }
  return context;
}
