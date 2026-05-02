import { useMemo, useState } from 'react';

export function useFilteredData(rows = []) {
  const mortalityValues = rows.map((row) => Number(row.crude_death_rate)).filter(Number.isFinite);
  const minMortality = mortalityValues.length ? Math.floor(Math.min(...mortalityValues)) : 0;
  const maxMortality = mortalityValues.length ? Math.ceil(Math.max(...mortalityValues)) : 30;
  const [region, setRegion] = useState('All');
  const [income, setIncome] = useState('All');
  const [mortalityMax, setMortalityMax] = useState(maxMortality || 30);
  const [search, setSearch] = useState('');

  const filtered = useMemo(
    () =>
      rows.filter((row) => {
        const mortality = Number(row.crude_death_rate);
        return (
          (region === 'All' || row.region === region) &&
          (income === 'All' || row.income_level === income) &&
          (!Number.isFinite(mortality) || mortality <= mortalityMax) &&
          (!search || row.country?.toLowerCase().includes(search.toLowerCase()))
        );
      }),
    [income, mortalityMax, region, rows, search],
  );

  return {
    filtered,
    filters: { region, income, mortalityMax, search, minMortality, maxMortality },
    actions: { setRegion, setIncome, setMortalityMax, setSearch },
  };
}
