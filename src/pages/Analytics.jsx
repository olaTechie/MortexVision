import { useState } from 'react';
import ChartCard from '../components/ChartCard.jsx';
import { SelectControl } from '../components/Controls.jsx';
import DataTable from '../components/DataTable.jsx';
import MetricCard from '../components/MetricCard.jsx';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { formatNumber, percent, titleCase } from '../utils/format.js';

export default function Analytics() {
  const { loading, error, comparison, coefficients, variableDictionaries, modelStatistics } = useDashboardData();
  const [model, setModel] = useState('');
  const [tracked, setTracked] = useState('');

  if (loading) return <Page title="Analytics"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const activeModel = model || comparison.at(-1).Model;
  const modelOptions = comparison.map((row) => row.Model);
  const variables = [...new Set(coefficients.filter((row) => row.Variable !== 'const').map((row) => row.Variable))];
  const trackedVar = tracked || variables[0];
  const coefs = coefficients
    .filter((row) => row.Model === activeModel && row.Variable !== 'const')
    .map((row) => ({ ...row, Abs_Coef: Math.abs(Number(row.Coefficient)), Category: categoryFor(row.Variable, variableDictionaries) }))
    .sort((a, b) => Number(a.Coefficient) - Number(b.Coefficient));
  const trackedRows = coefficients.filter((row) => row.Variable === trackedVar);

  const coefTable = coefs.map((row) => ({
    Variable: titleCase(row.Variable),
    Category: row.Category,
    Coefficient: row.Coefficient,
    Std_Error: row.Std_Error,
    T_Statistic: row.T_Statistic,
    P_Value: row.P_Value,
    CI_Lower: row.CI_Lower,
    CI_Upper: row.CI_Upper,
    Significant: Number(row.P_Value) < 0.001 ? '***' : Number(row.P_Value) < 0.01 ? '**' : Number(row.P_Value) < 0.05 ? '*' : '',
  }));

  const first = trackedRows[0]?.Coefficient;
  const last = trackedRows.at(-1)?.Coefficient;
  const change = Number(first) ? ((Number(last) - Number(first)) / Math.abs(Number(first))) * 100 : null;

  return (
    <Page eyebrow="Model Interpretation" title="Regression Analysis" description="Inspect model progression, coefficients, uncertainty intervals, and mediation signals.">
      <section className="metric-grid">
        {comparison.map((row) => (
          <MetricCard key={row.Model} label={row.Model} value={percent(row['R²'])} detail={`Adjusted ${percent(row['Adj. R²'])} | ${row['Num. Features']} features`} tone="blue" />
        ))}
      </section>

      <ChartCard
        title="Progressive model fit"
        data={[
          { type: 'bar', name: 'R2', x: comparison.map((row) => row.Model), y: comparison.map((row) => Number(row['R²']) * 100), marker: { color: '#2f7c8c' } },
          { type: 'bar', name: 'Adjusted R2', x: comparison.map((row) => row.Model), y: comparison.map((row) => Number(row['Adj. R²']) * 100), marker: { color: '#9f6b50' } },
        ]}
        layout={{ height: 420, barmode: 'group', yaxis: { title: 'Variance explained (%)' }, xaxis: { title: '' } }}
      />

      <section className="control-panel compact">
        <SelectControl label="Model" value={activeModel} onChange={setModel} options={modelOptions} />
      </section>

      <ChartCard
        title="Coefficient forest plot"
        data={[{
          type: 'scatter',
          mode: 'markers',
          x: coefs.map((row) => row.Coefficient),
          y: coefs.map((row) => titleCase(row.Variable)),
          error_x: {
            type: 'data',
            symmetric: false,
            array: coefs.map((row) => Number(row.CI_Upper) - Number(row.Coefficient)),
            arrayminus: coefs.map((row) => Number(row.Coefficient) - Number(row.CI_Lower)),
            color: '#7f8d9a',
          },
          marker: { size: 12, color: coefs.map((row) => (Number(row.Coefficient) < 0 ? '#2f8a5f' : '#b95745')) },
          hovertemplate: '<b>%{y}</b><br>Coefficient: %{x:.4f}<extra></extra>',
        }]}
        layout={{ height: Math.max(480, coefs.length * 34), shapes: [{ type: 'line', x0: 0, x1: 0, y0: -1, y1: coefs.length, line: { dash: 'dash', color: '#25313d' } }], margin: { l: 190, r: 24, t: 24, b: 48 } }}
      />

      <DataTable rows={coefTable} columns={['Variable', 'Category', 'Coefficient', 'Std_Error', 'T_Statistic', 'P_Value', 'CI_Lower', 'CI_Upper', 'Significant']} maxRows={40} />

      <section className="control-panel compact">
        <SelectControl label="Track variable across models" value={trackedVar} onChange={setTracked} options={variables} format={titleCase} />
      </section>
      <ChartCard
        title={`Coefficient movement: ${titleCase(trackedVar)}`}
        data={[{ type: 'scatter', mode: 'lines+markers', x: trackedRows.map((row) => row.Model), y: trackedRows.map((row) => row.Coefficient), line: { color: '#2f7c8c', width: 3 }, marker: { size: 12 } }]}
        layout={{ height: 410, yaxis: { title: 'Coefficient' }, xaxis: { title: '' }, shapes: [{ type: 'line', x0: -0.5, x1: trackedRows.length - 0.5, y0: 0, y1: 0, line: { dash: 'dash', color: '#7f8d9a' } }] }}
      />
      {change !== null && <div className="notice">Coefficient change from first to final model: {formatNumber(first, 4)} to {formatNumber(last, 4)} ({change.toFixed(1)}%).</div>}

      <section className="metric-grid">
        <MetricCard label="R2" value={formatNumber(modelStatistics.r_squared, 4)} />
        <MetricCard label="Adjusted R2" value={formatNumber(modelStatistics.r_squared_adj, 4)} />
        <MetricCard label="F statistic" value={formatNumber(modelStatistics.f_statistic)} />
        <MetricCard label="Observations" value={modelStatistics.n_obs} />
      </section>
    </Page>
  );
}

function categoryFor(variable, dicts) {
  if (Object.values(dicts.distal_vars).includes(variable)) return 'Distal';
  if (Object.values(dicts.intermediate_vars).includes(variable)) return 'Intermediate';
  if (Object.values(dicts.proximate_vars).includes(variable)) return 'Proximate';
  return 'Other';
}
