import { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import { getContributorActivity } from '../api';

export default function ActivityChart() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    getContributorActivity('weekly')
      .then((rows) => {
        const grouped = groupByPeriod(rows);
        setData(grouped);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error}</p>;
  if (data.length === 0) return <p>No activity data yet.</p>;

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="period_start" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="commits_count" stroke="#8884d8" name="Commits" />
      </LineChart>
    </ResponsiveContainer>
  );
}

function groupByPeriod(rows) {
  const totals = {};

  for (const row of rows) {
    const key = row.period_start;
    totals[key] = (totals[key] || 0) + row.commits_count;
  }

  return Object.entries(totals)
    .map(([period_start, commits_count]) => ({ period_start, commits_count }))
    .sort((a, b) => a.period_start.localeCompare(b.period_start));
}