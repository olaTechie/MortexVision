import { useState } from 'react';
import ChartCard from '../components/ChartCard.jsx';
import { SelectControl, ToggleControl } from '../components/Controls.jsx';
import DataTable from '../components/DataTable.jsx';
import Page from '../components/Page.jsx';
import Skeleton from '../components/Skeleton.jsx';
import { useDashboardData } from '../hooks/useDashboardData.js';
import { formatNumber, titleCase } from '../utils/format.js';
import { aggregateBy, describe, numericColumns } from '../utils/stats.js';

const scales = ['Viridis', 'Plasma', 'Inferno', 'RdYlGn', 'RdBu', 'Blues', 'Reds', 'Greens'];
const projections = ['natural earth', 'equirectangular', 'mercator', 'orthographic', 'robinson'];

export default function Maps() {
  const { loading, error, health } = useDashboardData();
  const [selectedVar, setSelectedVar] = useState('crude_death_rate');
  const [scale, setScale] = useState('RdYlGn');
  const [projection, setProjection] = useState('natural earth');
  const [reverse, setReverse] = useState(true);

  if (loading) return <Page title="Global Maps"><Skeleton rows={8} /></Page>;
  if (error) return <Page title="Data unavailable" description={error.message} />;

  const numeric = numericColumns(health, ['latitude', 'longitude', 'total_population']);
  const mapped = health.filter((row) => row.iso3_code && Number.isFinite(Number(row[selectedVar])));
  const stats = describe(mapped, selectedVar);
  const regional = aggregateBy(mapped, 'region', selectedVar);
  const top = [...mapped].sort((a, b) => Number(b[selectedVar]) - Number(a[selectedVar])).slice(0, 10);
  const bottom = [...mapped].sort((a, b) => Number(a[selectedVar]) - Number(b[selectedVar])).slice(0, 10);

  return (
    <Page eyebrow="Geography" title="Global Maps" description="Explore the geographic distribution of mortality determinants and regional variation.">
      <section className="control-panel">
        <SelectControl label="Indicator" value={selectedVar} onChange={setSelectedVar} options={numeric} format={titleCase} />
        <SelectControl label="Color scale" value={scale} onChange={setScale} options={scales} />
        <SelectControl label="Projection" value={projection} onChange={setProjection} options={projections} format={titleCase} />
        <ToggleControl checked={reverse} onChange={setReverse} label="Reverse scale" />
      </section>

      <ChartCard
        title={`Global distribution: ${titleCase(selectedVar)}`}
        data={[{
          type: 'choropleth',
          locations: mapped.map((row) => row.iso3_code),
          z: mapped.map((row) => row[selectedVar]),
          text: mapped.map((row) => `${row.country}<br>${row.region}`),
          colorscale: reverse ? `${scale}_r` : scale,
          marker: { line: { color: '#ffffff', width: 0.45 } },
          colorbar: { title: titleCase(selectedVar), thickness: 14 },
          hovertemplate: '<b>%{text}</b><br>Value: %{z:.2f}<extra></extra>',
        }]}
        layout={{ height: 620, geo: { projection: { type: projection }, showframe: false, showcoastlines: true, coastlinecolor: '#a8b6c4', bgcolor: 'rgba(0,0,0,0)' }, margin: { l: 0, r: 0, t: 12, b: 0 } }}
      />

      <section className="metric-grid five">
        {stats && Object.entries({ Minimum: stats.min, Median: stats.median, Mean: stats.mean, Maximum: stats.max, 'Std Dev': stats.std }).map(([label, value]) => (
          <div className="mini-metric" key={label}><span>{label}</span><strong>{formatNumber(value)}</strong></div>
        ))}
      </section>

      <ChartCard
        title="Regional comparison"
        data={[{ type: 'bar', x: regional.map((row) => row.group), y: regional.map((row) => row.mean), marker: { color: '#7c5c38' } }]}
        layout={{ height: 430, yaxis: { title: titleCase(selectedVar) }, xaxis: { title: '' } }}
      />

      <section className="two-col">
        <div className="panel"><h2>Highest {titleCase(selectedVar)}</h2><DataTable rows={top} columns={['country', 'region', selectedVar]} maxRows={10} /></div>
        <div className="panel"><h2>Lowest {titleCase(selectedVar)}</h2><DataTable rows={bottom} columns={['country', 'region', selectedVar]} maxRows={10} /></div>
      </section>
    </Page>
  );
}
