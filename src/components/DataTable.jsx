import { useMemo, useState } from 'react';
import { ArrowDownUp } from 'lucide-react';
import { formatNumber } from '../utils/format.js';

export default function DataTable({ rows = [], columns = [], maxRows = 20 }) {
  const [sort, setSort] = useState({ key: columns[0], direction: 'asc' });
  const visibleRows = useMemo(() => {
    const sorted = [...rows].sort((a, b) => {
      const av = a[sort.key];
      const bv = b[sort.key];
      if (Number.isFinite(Number(av)) && Number.isFinite(Number(bv))) return (Number(av) - Number(bv)) * (sort.direction === 'asc' ? 1 : -1);
      return String(av ?? '').localeCompare(String(bv ?? '')) * (sort.direction === 'asc' ? 1 : -1);
    });
    return sorted.slice(0, maxRows);
  }, [maxRows, rows, sort]);

  const handleSort = (key) => {
    setSort((current) => ({ key, direction: current.key === key && current.direction === 'asc' ? 'desc' : 'asc' }));
  };

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column}>
                <button onClick={() => handleSort(column)}>
                  {column.replaceAll('_', ' ')}
                  <ArrowDownUp size={13} />
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {visibleRows.map((row, index) => (
            <tr key={`${row.country || 'row'}-${index}`}>
              {columns.map((column) => (
                <td key={column}>{Number.isFinite(Number(row[column])) ? formatNumber(row[column]) : row[column] || 'N/A'}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
