import { Activity, BarChart3, Database, Globe2 } from 'lucide-react';
import ChartCard from '../components/ChartCard.jsx';
import MetricCard from '../components/MetricCard.jsx';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { determinantGroups } from '../data/nav.js';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { aggregateBy } from '../utils/stats.js';
import { percent } from '../utils/format.js';

export default function Overview() {
  const { loading, error, health, modelStatistics } = useDashboardData();

  if (loading) return <Page title="MortexVision" description="Loading global health intelligence."><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const regionStats = aggregateBy(health, 'region', 'crude_death_rate');
  const indicators = Object.keys(health[0]).filter((key) => !['country', 'iso3_code', 'region', 'income_level'].includes(key));

  return (
    <Page
      eyebrow="MortexVision"
      title="Global mortality intelligence, redesigned."
      description="A polished multi-page analytics product for exploring ecological determinants of mortality across countries, regions, and income groups."
    >
      <section className="metric-grid">
        <MetricCard label="Countries analysed" value={health.length} icon={Globe2} tone="blue" />
        <MetricCard label="World regions" value={new Set(health.map((row) => row.region)).size} icon={Database} tone="green" />
        <MetricCard label="Health indicators" value={indicators.length} icon={Activity} tone="amber" />
        <MetricCard label="Variance explained" value={percent(modelStatistics.r_squared_adj)} icon={BarChart3} tone="rose" />
      </section>

      <section className="feature-band">
        <div>
          <p className="eyebrow">Migration Strategy</p>
          <h2>From Streamlit dashboard to launch-ready React product</h2>
          <p>
            The original pages were mapped into typed, reusable data flows: filters and tables live in Data Explorer, geographic
            views in Global Maps, model outputs in Analytics, country deep-dives in Profiles, and intervention math in the Policy
            Simulator. Static CSV and JSON assets keep the app deployable on GitHub Pages without a server.
          </p>
        </div>
        <div className="warning-panel">
          <strong>Ecological fallacy notice</strong>
          <span>
            This app uses country-level aggregate data. Relationships observed between countries must not be interpreted as
            individual-level causal effects.
          </span>
        </div>
      </section>

      <section className="group-grid">
        {determinantGroups.map(({ title, description, icon: Icon, tone }) => (
          <article className={`group-card tone-${tone}`} key={title}>
            <Icon size={22} />
            <h3>{title}</h3>
            <p>{description}</p>
          </article>
        ))}
      </section>

      <ChartCard
        title="Regional mortality profile"
        eyebrow="Overview"
        data={[
          {
            type: 'bar',
            x: regionStats.map((row) => row.group),
            y: regionStats.map((row) => row.mean),
            marker: { color: '#2f7c8c', line: { color: '#ffffff', width: 1 } },
            hovertemplate: '<b>%{x}</b><br>Mean death rate: %{y:.2f}<extra></extra>',
          },
        ]}
        layout={{ height: 390, yaxis: { title: 'Crude death rate per 1,000' }, xaxis: { title: '' } }}
      />
    </Page>
  );
}
