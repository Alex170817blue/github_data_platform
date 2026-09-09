export default function StatsCards({ data }) {
  const stats = [
    {
      label: 'Total Commits',
      value: data?.total_commits ?? 0,
    },
    {
      label: 'Active Contributors',
      value: data?.active_contributors ?? 0,
    },
    {
      label: 'Open PRs',
      value: data?.open_prs ?? 0,
    },
    {
      label: 'Avg. Commits/Week',
      value: data?.avg_commits_per_week ?? 0,
    },
  ];

  return (
    <div className="stats-grid">
      {stats.map((stat) => (
        <div key={stat.label} className="stat-card">
          {stat.icon && (
            <div className="stat-icon">
              {stat.icon}
            </div>
          )}

          <div className="stat-value">
            {stat.value}
          </div>

          <div className="stat-label">
            {stat.label}
          </div>
        </div>
      ))}
    </div>
  );
}

