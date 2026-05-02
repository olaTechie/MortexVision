import { Download } from 'lucide-react';
import { useState } from 'react';
import ChartCard from '../components/ChartCard.jsx';
import { RangeControl, SearchControl, SelectControl, ToggleControl } from '../components/Controls.jsx';
import DataTable from '../components/DataTable.jsx';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { useFilteredData } from '../hooks/useFilteredData.js';
import { csvDownload, formatNumber, titleCase } from '../utils/format.js';
import { correlationMatrix, describe, numericColumns, pearson } from '../utils/stats.js';

export default function DataExplorer() {
  const { loading, error, health = [], variableDictionaries } = useDashboardData();
  const [tab, setTab] = useState('table');
  const [selectedVar, setSelectedVar] = useState('crude_death_rate');
  const [xVar, setXVar] = useState('gni_per_capita');
  const [yVar, setYVar] = useState('crude_death_rate');
  const [splitRegion, setSplitRegion] = useState(true);
  const { filtered, filters, actions } = useFilteredData(health);

  if (loading) return <Page title="Data Explorer"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const regions = ['All', ...new Set(health.map((row) => row.region).filter(Boolean))].sort();
  const incomeLevels = ['All', ...new Set(health.map((row) => row.income_level).filter(Boolean))].sort();
  const numeric = numericColumns(health, ['latitude', 'longitude']);
  const columns = ['country', 'region', 'income_level', 'crude_death_rate', 'gni_per_capita', 'adult_literacy', 'physicians_density', 'safe_water'].filter((col) => health[0][col] !== undefined);
  const corrVars = numeric.slice(0, 10);
  const stats = describe(filtered, selectedVar);
  const corr = pearson(filtered, xVar, yVar);

  const histogramTraces = splitRegion
    ? Object.entries(
        filtered.reduce((acc, row) => {
          const group = row.region || 'Unknown';
          acc[group] = acc[group] || [];
          if (Number.isFinite(Number(row[selectedVar]))) acc[group].push(Number(row[selectedVar]));
          return acc;
        }, {}),
      ).map(([region, values]) => ({ type: 'histogram', x: values, name: region, opacity: 0.72 }))
    : [{ type: 'histogram', x: filtered.map((row) => row[selectedVar]).filter(Number.isFinite), marker: { color: '#2f7c8c' } }];

  const matrix = correlationMatrix(filtered, corrVars);

  return (
    <Page eyebrow="Explorer" title="Data Explorer" description="Filter countries, inspect indicators, compare distributions, and export clean subsets.">
      <section className="control-panel">
        <SearchControl value={filters.search} onChange={actions.setSearch} placeholder="Search country" />
        <SelectControl label="Region" value={filters.region} onChange={actions.setRegion} options={regions} />
        <SelectControl label="Income level" value={filters.income} onChange={actions.setIncome} options={incomeLevels} />
        <RangeControl label="Max death rate" value={filters.mortalityMax} min={filters.minMortality} max={filters.maxMortality} onChange={actions.setMortalityMax} />
      </section>

      <div className="tab-row">
        {['table', 'distributions', 'correlations', 'scatter'].map((item) => (
          <button className={tab === item ? 'active' : ''} key={item} onClick={() => setTab(item)}>{titleCase(item)}</button>
        ))}
      </div>

      {tab === 'table' && (
        <section className="stack">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Filtered set</p>
              <h2>{filtered.length} of {health.length} countries</h2>
            </div>
            <a className="button" href={csvDownload(filtered, columns)} download="mortexvision-filtered-data.csv">
              <Download size={16} /> Download CSV
            </a>
          </div>
          <DataTable rows={filtered} columns={columns} maxRows={40} />
        </section>
      )}

      {tab === 'distributions' && (
        <section className="split-grid">
          <div className="panel">
            <SelectControl label="Variable" value={selectedVar} onChange={setSelectedVar} options={numeric} format={titleCase} />
            <ToggleControl checked={splitRegion} onChange={setSplitRegion} label="Split by region" />
            {stats && (
              <dl className="stat-list">
                {Object.entries(stats).map(([key, value]) => <div key={key}><dt>{titleCase(key)}</dt><dd>{formatNumber(value)}</dd></div>)}
              </dl>
            )}
          </div>
          <ChartCard
            title={`Distribution of ${titleCase(selectedVar)}`}
            data={histogramTraces}
            layout={{ height: 520, barmode: 'overlay', xaxis: { title: titleCase(selectedVar) }, yaxis: { title: 'Countries' } }}
          />
        </section>
      )}

      {tab === 'correlations' && (
        <section className="stack">
          <div className="insight-card">
            <strong>Variable groups</strong>
            <span>Distal: {Object.values(variableDictionaries.distal_vars).slice(0, 4).map(titleCase).join(', ')}</span>
            <span>Intermediate: {Object.values(variableDictionaries.intermediate_vars).slice(0, 4).map(titleCase).join(', ')}</span>
            <span>Proximate: {Object.values(variableDictionaries.proximate_vars).slice(0, 4).map(titleCase).join(', ')}</span>
          </div>
          <ChartCard
            title="Correlation matrix"
            data={[{ type: 'heatmap', z: matrix, x: corrVars.map(titleCase), y: corrVars.map(titleCase), colorscale: 'RdBu', zmin: -1, zmax: 1 }]}
            layout={{ height: 620, margin: { l: 150, r: 24, t: 24, b: 150 } }}
          />
        </section>
      )}

      {tab === 'scatter' && (
        <section className="stack">
          <section className="control-panel compact">
            <SelectControl label="X axis" value={xVar} onChange={setXVar} options={numeric} format={titleCase} />
            <SelectControl label="Y axis" value={yVar} onChange={setYVar} options={numeric} format={titleCase} />
          </section>
          <ChartCard
            title={`${titleCase(yVar)} vs ${titleCase(xVar)}`}
            data={[{
              type: 'scatter',
              mode: 'markers',
              x: filtered.map((row) => row[xVar]),
              y: filtered.map((row) => row[yVar]),
              text: filtered.map((row) => row.country),
              marker: { size: 11, color: filtered.map((row) => row.crude_death_rate), colorscale: 'Tealrose', opacity: 0.78, line: { color: '#ffffff', width: 1 } },
              hovertemplate: '<b>%{text}</b><br>X: %{x:.2f}<br>Y: %{y:.2f}<extra></extra>',
            }]}
            layout={{ height: 590, xaxis: { title: titleCase(xVar) }, yaxis: { title: titleCase(yVar) } }}
          />
          {corr && <div className="notice">Pearson correlation: r = {corr.r.toFixed(3)} across {corr.n} countries.</div>}
        </section>
      )}
    </Page>
  );
}
