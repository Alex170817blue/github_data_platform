import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28'];

export default function PRStatusChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="no-data-message">
        <p>No PR data available</p>
      </div>
    );
  }

  const pieData = data.map((item) => ({
    name: item.status,
    value: item.count ?? 0,
  }));

  const total = pieData.reduce(
    (sum, item) => sum + item.value,
    0
  );

  if (total === 0) {
    return (
      <div className="no-data-message">
        <p>No pull requests found</p>
        <span className="no-data-sub">
          No pull requests are available in the current dataset.
        </span>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsPieChart>
        <Pie
          data={pieData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) =>
            `${name} ${(percent * 100).toFixed(0)}%`
          }
          outerRadius={80}
          dataKey="value"
        >
          {pieData.map((entry, index) => (
            <Cell
              key={entry.name}
              fill={COLORS[index % COLORS.length]}
            />
          ))}
        </Pie>

        <Tooltip />

        <Legend />
      </RechartsPieChart>
    </ResponsiveContainer>
  );
}