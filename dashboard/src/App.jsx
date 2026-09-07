import ActivityChart from './components/ActivityChart';
import './App.css';

function App() {
  return (
    <div className="dashboard">
      <h1>GitHub Engineering Metrics</h1>

      <section>
        <h2>Contributor Activity (weekly)</h2>
        <ActivityChart />
      </section>
    </div>
  );
}

export default App;