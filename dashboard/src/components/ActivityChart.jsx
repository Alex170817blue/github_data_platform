import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function ActivityChart({ data }) {
  if (!data || data.length === 0) {
    return <p>No activity data yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="period_start" />

        <YAxis />

        <Tooltip />

        <Legend />

        <Line
          type="monotone"
          dataKey="commits_count"
          name="Commits"
          stroke="#FF5F1F"
          fill="#FFCE1F"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}