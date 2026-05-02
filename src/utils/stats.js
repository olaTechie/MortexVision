export const numericColumns = (rows, excluded = []) => {
  if (!rows?.length) return [];
  return Object.keys(rows[0]).filter((key) => !excluded.includes(key) && rows.some((row) => Number.isFinite(Number(row[key]))));
};

export const describe = (rows, column) => {
  const values = rows.map((row) => Number(row[column])).filter(Number.isFinite).sort((a, b) => a - b);
  if (!values.length) return null;
  const sum = values.reduce((acc, value) => acc + value, 0);
  const mean = sum / values.length;
  const variance = values.reduce((acc, value) => acc + (value - mean) ** 2, 0) / Math.max(values.length - 1, 1);
  const percentile = (p) => values[Math.min(values.length - 1, Math.max(0, Math.floor((values.length - 1) * p)))];
  return {
    count: values.length,
    min: values[0],
    q1: percentile(0.25),
    median: percentile(0.5),
    mean,
    q3: percentile(0.75),
    max: values[values.length - 1],
    std: Math.sqrt(variance),
  };
};

export const pearson = (rows, x, y) => {
  const pairs = rows
    .map((row) => [Number(row[x]), Number(row[y])])
    .filter(([a, b]) => Number.isFinite(a) && Number.isFinite(b));
  if (pairs.length < 3) return null;
  const meanX = pairs.reduce((sum, [a]) => sum + a, 0) / pairs.length;
  const meanY = pairs.reduce((sum, [, b]) => sum + b, 0) / pairs.length;
  let numerator = 0;
  let denomX = 0;
  let denomY = 0;
  pairs.forEach(([a, b]) => {
    numerator += (a - meanX) * (b - meanY);
    denomX += (a - meanX) ** 2;
    denomY += (b - meanY) ** 2;
  });
  return { r: numerator / Math.sqrt(denomX * denomY), n: pairs.length };
};

export const correlationMatrix = (rows, columns) =>
  columns.map((y) => columns.map((x) => pearson(rows, x, y)?.r ?? null));

export const groupBy = (rows, key) =>
  rows.reduce((acc, row) => {
    const group = row[key] || 'Unknown';
    acc[group] = acc[group] || [];
    acc[group].push(row);
    return acc;
  }, {});

export const aggregateBy = (rows, groupKey, valueKey) =>
  Object.entries(groupBy(rows, groupKey))
    .map(([group, groupRows]) => ({ group, ...describe(groupRows, valueKey) }))
    .filter((row) => row.count)
    .sort((a, b) => b.mean - a.mean);

export const percentileRank = (rows, column, value, invert = false) => {
  const values = rows.map((row) => Number(row[column])).filter(Number.isFinite);
  if (!Number.isFinite(Number(value)) || !values.length) return null;
  const pct = (values.filter((candidate) => candidate <= Number(value)).length / values.length) * 100;
  return invert ? 100 - pct : pct;
};
