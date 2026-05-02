export function SelectControl({ label, value, onChange, options, format = (x) => x }) {
  return (
    <label className="control">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {format(option)}
          </option>
        ))}
      </select>
    </label>
  );
}

export function RangeControl({ label, value, min, max, onChange }) {
  return (
    <label className="control">
      <span>
        {label} <b>{value}</b>
      </span>
      <input type="range" min={min} max={max} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}

export function SearchControl({ value, onChange, placeholder = 'Search' }) {
  return <input className="search-input" value={value} onChange={(event) => onChange(event.target.value)} placeholder={placeholder} />;
}

export function ToggleControl({ checked, onChange, label }) {
  return (
    <label className="toggle-control">
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
      <span>{label}</span>
    </label>
  );
}
