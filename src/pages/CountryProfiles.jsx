import { useState } from 'react';
import ChartCard from '../components/ChartCard.jsx';
import { SelectControl } from '../components/Controls.jsx';
import DataTable from '../components/DataTable.jsx';
import MetricCard from '../components/MetricCard.jsx';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { formatNumber, titleCase } from '../utils/format.js';
import { numericColumns, percentileRank } from '../utils/stats.js';

export default function CountryProfiles() {
  const { loading, error, health, variableDictionaries } = useDashboardData();
  const [country, setCountry] = useState('United Kingdom');
  const [compareTo, setCompareTo] = useState('Global Average');
  const [compareVar, setCompareVar] = useState('crude_death_rate');

  if (loading) return <Page title="Country Profiles"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const countries = health.map((row) => row.country).filter(Boolean).sort();
  const selectedCountry = countries.includes(country) ? country : countries[0];
  const row = health.find((item) => item.country === selectedCountry);
  const numeric = numericColumns(health, ['latitude', 'longitude']);
  const comparisonRows = compareTo === 'Regional Average' ? health.filter((item) => item.region === row.region) : compareTo === 'Income Group Average' ? health.filter((item) => item.income_level === row.income_level) : health;
  const comparison = averageRow(comparisonRows, numeric);
  const radarVars = ['crude_death_rate', 'gni_per_capita', 'adult_literacy', 'physicians_density', 'safe_water', 'communicable_disease_deaths'].filter((key) => numeric.includes(key));
  const radar = radarVars.map((key) => ({
    variable: titleCase(key),
    country: percentileRank(health, key, row[key], key.includes('death')),
    comparison: percentileRank(health, key, comparison[key], key.includes('death')),
  }));
  const regional = health.filter((item) => item.region === row.region && Number.isFinite(Number(item.crude_death_rate))).sort((a, b) => Number(a.crude_death_rate) - Number(b.crude_death_rate));
  const countryRank = regional.findIndex((item) => item.country === selectedCountry) + 1;

  const vars = [
    ...Object.values(variableDictionaries.distal_vars),
    ...Object.values(variableDictionaries.intermediate_vars),
    ...Object.values(variableDictionaries.proximate_vars),
  ].filter((key) => row[key] !== undefined);
  const indicatorRows = vars.map((key) => ({
    Indicator: titleCase(key),
    Value: row[key],
    Comparison: comparison[key],
    Rank: `${rankFor(health, key, row[key], key.includes('death'))}/${health.filter((item) => Number.isFinite(Number(item[key]))).length}`,
  }));

  return (
    <Page eyebrow="Profiles" title="Country Profiles" description="Inspect individual country context, rank, and determinants against global, regional, or income peers.">
      <section className="control-panel">
        <SelectControl label="Country" value={selectedCountry} onChange={setCountry} options={countries} />
        <SelectControl label="Compare to" value={compareTo} onChange={setCompareTo} options={['Global Average', 'Regional Average', 'Income Group Average']} />
      </section>

      <section className="country-hero">
        <div>
          <p className="eyebrow">{row.region} | {row.income_level}</p>
          <h2>{selectedCountry}</h2>
        </div>
        <span>Rank {countryRank} of {regional.length} in region for mortality, lower is better.</span>
      </section>

      <section className="metric-grid three">
        <Indicator row={row} comparison={comparison} variable="crude_death_rate" label="Death Rate" lowerBetter />
        <Indicator row={row} comparison={comparison} variable="gni_per_capita" label="GNI per Capita" />
        <Indicator row={row} comparison={comparison} variable="adult_literacy" label="Adult Literacy" />
        <Indicator row={row} comparison={comparison} variable="physicians_density" label="Physicians" />
        <Indicator row={row} comparison={comparison} variable="safe_water" label="Safe Water" />
        <Indicator row={row} comparison={comparison} variable="basic_sanitation" label="Sanitation" />
      </section>

      <ChartCard
        title="Health profile percentile"
        data={[
          { type: 'scatterpolar', r: radar.map((item) => item.country), theta: radar.map((item) => item.variable), fill: 'toself', name: selectedCountry, line: { color: '#2f7c8c' } },
          { type: 'scatterpolar', r: radar.map((item) => item.comparison), theta: radar.map((item) => item.variable), fill: 'toself', name: compareTo, line: { color: '#a9b5bf' } },
        ]}
        layout={{ height: 520, polar: { radialaxis: { visible: true, range: [0, 100] } } }}
      />

      <DataTable rows={indicatorRows} columns={['Indicator', 'Value', 'Comparison', 'Rank']} maxRows={50} />

      <section className="control-panel compact">
        <SelectControl label="Regional chart indicator" value={compareVar} onChange={setCompareVar} options={numeric} format={titleCase} />
      </section>
      <ChartCard
        title={`Regional context: ${row.region}`}
        data={[{
          type: 'bar',
          x: regional.slice(0, 24).map((item) => item.country),
          y: regional.slice(0, 24).map((item) => item[compareVar]),
          marker: { color: regional.slice(0, 24).map((item) => (item.country === selectedCountry ? '#2f7c8c' : '#d4dde5')) },
        }]}
        layout={{ height: 420, xaxis: { title: '', tickangle: -35 }, yaxis: { title: titleCase(compareVar) } }}
      />
    </Page>
  );
}

function Indicator({ row, comparison, variable, label, lowerBetter = false }) {
  const value = Number(row[variable]);
  const comp = Number(comparison[variable]);
  const pct = Number.isFinite(value) && Number.isFinite(comp) && comp !== 0 ? ((value - comp) / comp) * 100 : null;
  const better = pct === null ? null : lowerBetter ? pct < 0 : pct > 0;
  return <MetricCard label={label} value={formatNumber(value)} detail={pct === null ? 'No comparison' : `${better ? 'Better' : 'Below peer'} by ${Math.abs(pct).toFixed(1)}%`} tone={better ? 'green' : 'amber'} />;
}

function averageRow(rows, keys) {
  return keys.reduce((acc, key) => {
    const values = rows.map((row) => Number(row[key])).filter(Number.isFinite);
    acc[key] = values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
    return acc;
  }, {});
}

function rankFor(rows, key, value, lowerBetter) {
  const values = rows.map((row) => Number(row[key])).filter(Number.isFinite).sort((a, b) => (lowerBetter ? a - b : b - a));
  return values.findIndex((candidate) => candidate === Number(value)) + 1;
}
