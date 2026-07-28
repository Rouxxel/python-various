interface Column<T> {
  id: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
}

interface DataTableProps<T extends Record<string, unknown>> {
  columns: Column<T>[];
  data: T[];
  exportable?: boolean;
  emptyMessage?: string;
}

export function DataTable<T extends Record<string, unknown>>({
  columns,
  data,
  exportable = false,
  emptyMessage = "No data available",
}: DataTableProps<T>) {
  const exportCsv = () => {
    const headers = columns.map((column) => column.header).join(",");
    const rows = data
      .map((row) =>
        columns
          .map((column) => {
            const value = row[column.id as keyof T];
            return `"${String(value ?? "")}"`;
          })
          .join(",")
      )
      .join("\n");
    const blob = new Blob([`${headers}\n${rows}`], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "export.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  if (data.length === 0) {
    return <p className="text-sm text-gray-500">{emptyMessage}</p>;
  }

  return (
    <div>
      {exportable && (
        <div className="mb-3 flex justify-end">
          <button
            type="button"
            onClick={exportCsv}
            className="rounded border px-3 py-1 text-sm hover:bg-gray-50"
          >
            Export CSV
          </button>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={String(column.id)}
                  className="px-4 py-2 text-left font-medium text-gray-600"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.map((row, index) => (
              <tr key={index}>
                {columns.map((column) => (
                  <td key={String(column.id)} className="px-4 py-2">
                    {column.render
                      ? column.render(row)
                      : String(row[column.id as keyof T] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
