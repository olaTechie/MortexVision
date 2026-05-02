export const titleCase = (value = '') =>
  String(value)
    .replaceAll('_', ' ')
    .replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());

export const formatNumber = (value, digits = 2) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'N/A';
  const num = Number(value);
  if (Math.abs(num) >= 1000000) return Intl.NumberFormat('en', { notation: 'compact', maximumFractionDigits: 1 }).format(num);
  return Intl.NumberFormat('en', { maximumFractionDigits: digits }).format(num);
};

export const percent = (value, digits = 1) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return 'N/A';
  return `${(Number(value) * 100).toFixed(digits)}%`;
};

export const csvDownload = (rows, columns) => {
  const header = columns.join(',');
  const body = rows
    .map((row) =>
      columns
        .map((col) => {
          const value = row[col] ?? '';
          return `"${String(value).replaceAll('"', '""')}"`;
        })
        .join(','),
    )
    .join('\n');
  return `data:text/csv;charset=utf-8,${encodeURIComponent(`${header}\n${body}`)}`;
};
