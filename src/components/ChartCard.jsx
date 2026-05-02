import Plot from 'react-plotly.js';
import Skeleton from './Skeleton.jsx';

const plotConfig = {
  displayModeBar: false,
  responsive: true,
};

const layoutDefaults = {
  autosize: true,
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { family: 'Inter, ui-sans-serif, system-ui', color: '#203040' },
  margin: { l: 48, r: 24, t: 24, b: 48 },
  hoverlabel: { bordercolor: '#dfe7ef', bgcolor: '#ffffff', font: { color: '#17212b' } },
};

export default function ChartCard({ title, eyebrow, children, data, layout, className = '' }) {
  return (
    <section className={`chart-card ${className}`}>
      {(title || eyebrow) && (
        <div className="chart-card-header">
          <div>
            {eyebrow && <p className="eyebrow">{eyebrow}</p>}
            {title && <h2>{title}</h2>}
          </div>
          {children}
        </div>
      )}
      {data ? (
        <Plot data={data} layout={{ ...layoutDefaults, ...layout }} config={plotConfig} useResizeHandler className="plot" />
      ) : (
        <Skeleton rows={5} />
      )}
    </section>
  );
}
