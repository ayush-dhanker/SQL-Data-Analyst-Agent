import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Chart({ chart }) {
  if (!chart || !chart.chartable) return null;

  const { chart_type, x_axis, y_axis, data } = chart;

  const formatYAxis = (value) =>
    value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value;

  const formatTooltip = (value) =>
    value.toLocaleString("en-US", { maximumFractionDigits: 2 });

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        {chart_type === "bar" ? (
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey={x_axis}
              tick={{ fontSize: 11 }}
              interval={0}
              angle={-30}
              textAnchor="end"
              height={60}
            />
            <YAxis tickFormatter={formatYAxis} />
            <Tooltip formatter={formatTooltip} />
            <Bar dataKey={y_axis} fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        ) : (
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey={x_axis}
              tick={{ fontSize: 11 }}
              interval={0}
              angle={-30}
              textAnchor="end"
              height={60}
            />
            <YAxis tickFormatter={formatYAxis} />
            <Tooltip formatter={formatTooltip} />
            <Line
              type="monotone"
              dataKey={y_axis}
              stroke="#6366f1"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}