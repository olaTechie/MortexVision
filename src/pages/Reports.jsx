import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';

export default function Reports() {
  const { loading, error, modelSummary } = useDashboardData();
  if (loading) return <Page title="Reports"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  return (
    <Page eyebrow="Documentation" title="Reports" description="Model summary output and reproducibility context migrated from the Streamlit regression page.">
      <section className="panel report-panel">
        <h2>Full model summary</h2>
        <pre>{modelSummary}</pre>
      </section>
    </Page>
  );
}
