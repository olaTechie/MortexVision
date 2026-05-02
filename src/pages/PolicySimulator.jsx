import { useState } from 'react';
import ChartCard from '../components/ChartCard.jsx';
import { RangeControl, SelectControl } from '../components/Controls.jsx';
import DataTable from '../components/DataTable.jsx';
import MetricCard from '../components/MetricCard.jsx';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { predictMortalityChange } from '../utils/policy.js';
import { formatNumber, titleCase } from '../utils/format.js';

const scenarios = {
  'Education: +20% literacy': ['adult_literacy', 20],
  'Economic: +20% GNI': ['gni_per_capita', 20],
  'Healthcare: +20% physicians': ['physicians_density', 20],
  'Water: +20% safe water': ['safe_water', 20],
  'Sanitation: +20% sanitation': ['basic_sanitation', 20],
  'Immunisation: +20% measles': ['measles_immunisation', 20],
};

export default function PolicySimulator() {
  const { loading, error, health, coefficients } = useDashboardData();
  const [variable, setVariable] = useState('adult_literacy');
  const [percentChange, setPercentChange] = useState(20);
  const [scope, setScope] = useState('All Countries');
  const [region, setRegion] = useState('All');

  if (loading) return <Page title="Policy Simulator"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const fullCoefs = coefficients.filter((row) => row.Model?.includes('Full') && row.Variable !== 'const' && health[0][row.Variable] !== undefined);
  const variables = fullCoefs.map((row) => row.Variable);
  const activeVariable = variables.includes(variable) ? variable : variables[0];
  const regions = ['All', ...new Set(health.map((row) => row.region).filter(Boolean))].sort();
  const countries = scope === 'Selected Region' && region !== 'All' ? health.filter((row) => row.region === region).map((row) => row.country) : null;
  const results = predictMortalityChange(health, coefficients, activeVariable, percentChange, countries);
  const avg = results.reduce((sum, row) => sum + row.mortality_change, 0) / Math.max(results.length, 1);
  const improved = results.filter((row) => row.mortality_change < 0).length;
  const coefficient = fullCoefs.find((row) => row.Variable === activeVariable);
  const comparison = Object.entries(scenarios)
    .filter(([, [scenarioVar]]) => variables.includes(scenarioVar))
    .map(([label, [scenarioVar, pct]]) => {
      const scenarioRows = predictMortalityChange(health, coefficients, scenarioVar, pct);
      return {
        Intervention: label,
        Variable: titleCase(scenarioVar),
        Avg_Mortality_Change: scenarioRows.reduce((sum, row) => sum + row.mortality_change, 0) / Math.max(scenarioRows.length, 1),
        Countries_Improved: scenarioRows.filter((row) => row.mortality_change < 0).length,
        Countries_Analysed: scenarioRows.length,
      };
    })
    .sort((a, b) => a.Avg_Mortality_Change - b.Avg_Mortality_Change);

  return (
    <Page eyebrow="Scenario Analysis" title="Policy Simulator" description="Run model-based what-if scenarios using full-model regression coefficients and clear limitations.">
      <div className="warning-panel wide">
        <strong>Use as educational exploration only.</strong>
        <span>Predictions are ecological, linear approximations. They are not causal estimates and should not drive policy decisions without further study.</span>
      </div>

      <section className="split-grid">
        <div className="panel">
          <h2>Configure intervention</h2>
          <SelectControl label="Variable" value={activeVariable} onChange={setVariable} options={variables} format={titleCase} />
          <RangeControl label="Intervention size (%)" value={percentChange} min={-50} max={100} onChange={setPercentChange} />
          <SelectControl label="Scope" value={scope} onChange={setScope} options={['All Countries', 'Selected Region']} />
          {scope === 'Selected Region' && <SelectControl label="Region" value={region} onChange={setRegion} options={regions} />}
          {coefficient && (
            <div className="insight-card">
              <strong>Coefficient {formatNumber(coefficient.Coefficient, 4)}</strong>
              <span>P-value {formatNumber(coefficient.P_Value, 4)}</span>
              <span>{Number(coefficient.Coefficient) > 0 ? 'Increases' : 'Decreases'} predicted mortality.</span>
            </div>
          )}
        </div>

        <div className="stack">
          <section className="metric-grid three">
            <MetricCard label="Average change" value={formatNumber(avg, 3)} detail="Deaths per 1,000" tone={avg < 0 ? 'green' : 'rose'} />
            <MetricCard label="Countries improved" value={improved} tone="green" />
            <MetricCard label="Countries analysed" value={results.length} tone="blue" />
          </section>
          <ChartCard
            title="Impact distribution"
            data={[{ type: 'histogram', x: results.map((row) => row.mortality_change), marker: { color: '#2f7c8c' }, nbinsx: 30 }]}
            layout={{ height: 350, xaxis: { title: 'Predicted mortality change' }, yaxis: { title: 'Countries' }, shapes: [{ type: 'line', x0: 0, x1: 0, y0: 0, y1: 1, yref: 'paper', line: { dash: 'dash', color: '#b95745' } }] }}
          />
        </div>
      </section>

      <section className="two-col">
        <div className="panel"><h2>Largest improvements</h2><DataTable rows={[...results].sort((a, b) => a.mortality_change - b.mortality_change).slice(0, 8)} columns={['country', 'current_mortality', 'mortality_change', 'predicted_mortality']} /></div>
        <div className="panel"><h2>Smallest improvements</h2><DataTable rows={[...results].sort((a, b) => b.mortality_change - a.mortality_change).slice(0, 8)} columns={['country', 'current_mortality', 'mortality_change', 'predicted_mortality']} /></div>
      </section>

      <ChartCard
        title="Compare standard interventions"
        data={[{ type: 'bar', x: comparison.map((row) => row.Intervention), y: comparison.map((row) => row.Avg_Mortality_Change), marker: { color: comparison.map((row) => (row.Avg_Mortality_Change < 0 ? '#2f8a5f' : '#b95745')) } }]}
        layout={{ height: 460, xaxis: { title: '', tickangle: -30 }, yaxis: { title: 'Average mortality change' } }}
      />
      <DataTable rows={comparison} columns={['Intervention', 'Variable', 'Avg_Mortality_Change', 'Countries_Improved', 'Countries_Analysed']} maxRows={10} />
    </Page>
  );
}
