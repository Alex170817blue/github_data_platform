import { BarChart as RechartsBarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ContributorChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 300,
        color: '#999',
        fontSize: '14px'
      }}>
        No contributor data available
      </div>
    );
  }

  const chartData = data.map(contributor => ({
    contributor: contributor.name || contributor.login || 'Unknown',
    commits: contributor.commits || 0,
    prs: contributor.prs || 0,
  }));

  // Se tutti i commit sono 0, mostra un messaggio
  if (chartData.every(d => d.commits === 0 && d.prs === 0)) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: 300,
        color: '#999',
        fontSize: '14px'
      }}>
        No activity data for contributors
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsBarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="contributor" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="commits" fill="#FF5F1F" name="Commits" />
        <Bar dataKey="prs" fill="#FFCE1F" name="Pull Requests" />
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}