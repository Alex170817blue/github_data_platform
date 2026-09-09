import { useEffect, useState } from 'react';

import ActivityChart from './components/ActivityChart';
import PRStatusChart from './components/PieChart';
import { WeeklyTrendChart } from './components/AreaChart';
import ContributorChart from './components/BarChart';
import StatsCards from './components/StatsCards';
import RepositoryTable from './components/RepositoryTable';

import {
  getSummaryMetrics,
  getContributorActivity,
  getContributorStats,
  getPRStats,
  getRepositoryMetrics,
} from './api';

import './App.css';

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [activity, setActivity] = useState([]);
  const [contributors, setContributors] = useState([]);
  const [prs, setPrs] = useState([]);
  const [repositories, setRepositories] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [
          summary,
          activityData,
          contributorData,
          prData,
          repositoryData,
        ] = await Promise.all([
          getSummaryMetrics(),
          getContributorActivity('weekly'),
          getContributorStats(),
          getPRStats(),
          getRepositoryMetrics(),
        ]);

        setMetrics(summary);
        setActivity(activityData);
        setContributors(contributorData);
        setPrs(prData);
        setRepositories(repositoryData.repositories);
      } catch (err) {
        console.error('Dashboard data loading failed:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="loading">
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        Error loading dashboard: {error}
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="no-data">
        No data available
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <h1>GitHub Engineering Dashboard</h1>

      <StatsCards data={metrics} />

      <div className="chart-card full-width">
        <h3>Repository</h3>
        <RepositoryTable data={repositories} />
      </div>

      <div className="charts-grid">
        <div className="chart-card full-width">
          <h3>Attività nel tempo</h3>
          <ActivityChart data={activity} />
        </div>

        <div className="chart-card half-width">
          <h3>Contributori</h3>
          <ContributorChart data={contributors} />
        </div>

        <div className="chart-card half-width">
          <h3>Stato PR</h3>
          <PRStatusChart data={prs} />
        </div>

        <div className="chart-card full-width">
          <h3>Trend settimanale</h3>
          <WeeklyTrendChart data={activity} />
        </div>
      </div>
    </div>
  );
}
