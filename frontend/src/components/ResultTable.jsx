export default function ResultTable({ data }) {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col.replace(/_/g, " ")}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {columns.map((col) => (
                <td key={col}>
                  {typeof row[col] === "number"
                    ? row[col].toLocaleString("en-US", {
                        maximumFractionDigits: 2,
                      })
                    : row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}