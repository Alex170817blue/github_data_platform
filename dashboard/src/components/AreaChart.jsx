import {
  AreaChart as RechartsAreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export function WeeklyTrendChart({ data }) {
  if (!data || data.length === 0) {
    return <p>No weekly activity data yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsAreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="period_start" />

        <YAxis />

        <Tooltip />

        <Legend />

        <Area
          type="monotone"
          dataKey="commits_count"
          name="Activity"
        />
      </RechartsAreaChart>
    </ResponsiveContainer>
  );
}
