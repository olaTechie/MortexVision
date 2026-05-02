import { AlertTriangle, CheckCircle2 } from 'lucide-react';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { titleCase } from '../utils/format.js';

export default function Insights() {
  const { loading, error, coefficients } = useDashboardData();
  if (loading) return <Page title="Insights"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const full = coefficients.filter((row) => row.Model?.includes('Full') && row.Variable !== 'const');
  const protective = full.filter((row) => Number(row.Coefficient) < 0).sort((a, b) => Number(a.P_Value) - Number(b.P_Value)).slice(0, 5);
  const risk = full.filter((row) => Number(row.Coefficient) > 0).sort((a, b) => Number(a.P_Value) - Number(b.P_Value)).slice(0, 5);

  return (
    <Page eyebrow="Executive View" title="Insights" description="A concise reading layer for model interpretation, limitations, and decision context.">
      <section className="two-col">
        <InsightList title="Protective associations" rows={protective} icon={CheckCircle2} />
        <InsightList title="Higher-mortality associations" rows={risk} icon={AlertTriangle} />
      </section>
      <section className="feature-band">
        <div>
          <p className="eyebrow">Interpretation</p>
          <h2>Use the app to compare patterns, not claim causality.</h2>
          <p>
            The strongest product value is exploratory clarity: users can move from country patterns to regional context, then into
            coefficient uncertainty and what-if scenarios. Every page preserves the original statistical caveats.
          </p>
        </div>
      </section>
    </Page>
  );
}

function InsightList({ title, rows, icon: Icon }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      <div className="insight-list">
        {rows.map((row) => (
          <article key={row.Variable}>
            <Icon size={18} />
            <div>
              <strong>{titleCase(row.Variable)}</strong>
              <span>Coefficient {Number(row.Coefficient).toFixed(4)} | p={Number(row.P_Value).toFixed(4)}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
