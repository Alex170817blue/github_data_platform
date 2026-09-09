export default function RepositoryTable({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="no-data-message">
        <p>No repositories found</p>
        <span className="no-data-sub">
          No repository data is available.
        </span>
      </div>
    );
  }

  return (
    <div className="repository-table-wrapper">
      <table className="repository-table">
        <thead>
          <tr>
            <th>Repository</th>
            <th>Language</th>
            <th>Commits</th>
            <th>Stars</th>
            <th>Forks</th>
            <th>Open issues</th>
            <th>Visibility</th>
          </tr>
        </thead>

        <tbody>
          {data.map((repository) => (
            <tr key={repository.name}>
              <td className="repository-name">
                {repository.name}
              </td>

              <td>
                {repository.primary_language || 'Unknown'}
              </td>

              <td>{repository.commits ?? 0}</td>

              <td>{repository.stars ?? 0}</td>

              <td>{repository.forks ?? 0}</td>

              <td>{repository.open_issues ?? 0}</td>

              <td>
                {repository.is_private ? 'Private' : 'Public'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}