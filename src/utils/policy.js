export const predictMortalityChange = (rows, coefficients, variable, percentChange, countries = null) => {
  const fullCoefs = coefficients.filter((row) => row.Model?.includes('Full'));
  const match = fullCoefs.find((row) => row.Variable === variable);
  if (!match) return [];
  const coef = Number(match.Coefficient);
  const targetRows = countries?.length ? rows.filter((row) => countries.includes(row.country)) : rows;

  return targetRows
    .map((row) => {
      const currentValue = Number(row[variable]);
      const currentMortality = Number(row.crude_death_rate);
      if (!Number.isFinite(currentValue) || !Number.isFinite(currentMortality)) return null;
      let newValue = currentValue * (1 + percentChange / 100);
      if (['literacy', 'water', 'sanitation', 'immunisation', 'access'].some((term) => variable.toLowerCase().includes(term))) {
        newValue = Math.min(newValue, 100);
      }
      const mortalityChange = coef * (newValue - currentValue);
      return {
        country: row.country,
        region: row.region,
        current_value: currentValue,
        new_value: newValue,
        current_mortality: currentMortality,
        mortality_change: mortalityChange,
        predicted_mortality: currentMortality + mortalityChange,
      };
    })
    .filter(Boolean);
};
