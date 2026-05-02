import Page from '../components/Page.jsx';
import { appName } from '../data/nav.js';

export default function Settings() {
  return (
    <Page eyebrow="About" title={`${appName} Deployment`} description="Repository, deployment, and operating notes for the migrated React/Vite product.">
      <section className="panel prose">
        <h2>Repository identity</h2>
        <p><strong>Recommended repo name:</strong> MortexVision</p>
        <p><strong>GitHub Pages URL:</strong> https://YOUR_GITHUB_USERNAME.github.io/MortexVision/</p>
        <p>The Vite base path is configured as <code>/MortexVision/</code> and the build copies <code>index.html</code> to <code>404.html</code> for SPA fallback routing.</p>
      </section>
      <section className="panel prose">
        <h2>Streamlit to React mapping</h2>
        <p>Overview maps the original home page. Data Explorer preserves filters, table export, distributions, correlations, and scatter plots. Global Maps preserves choropleths and ranking tables. Analytics preserves model comparison, coefficient plots, coefficient tables, and model statistics. Country Profiles and Policy Simulator preserve their original workflows with reusable React utilities.</p>
      </section>
    </Page>
  );
}
