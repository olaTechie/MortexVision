import Papa from 'papaparse';
import { useEffect, useState } from 'react';

const base = import.meta.env.BASE_URL.replace(/\/$/, '');

const parseCsv = async (path) => {
  const response = await fetch(`${base}/data/${path}`);
  if (!response.ok) throw new Error(`Unable to load ${path}`);
  const text = await response.text();
  return Papa.parse(text, {
    header: true,
    dynamicTyping: true,
    skipEmptyLines: true,
  }).data;
};

const parseJson = async (path) => {
  const response = await fetch(`${base}/data/${path}`);
  if (!response.ok) throw new Error(`Unable to load ${path}`);
  return response.json();
};

const parseText = async (path) => {
  const response = await fetch(`${base}/data/${path}`);
  if (!response.ok) throw new Error(`Unable to load ${path}`);
  return response.text();
};

export function useDashboardData() {
  const [state, setState] = useState({ loading: true, error: null });

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        const [health, comparison, coefficients, metadata, variableDictionaries, modelStatistics, modelSummary] = await Promise.all([
          parseCsv('global_health_data.csv'),
          parseCsv('model_comparison.csv'),
          parseCsv('regression_coefficients.csv'),
          parseJson('metadata.json'),
          parseJson('variable_dictionaries.json'),
          parseJson('model_statistics.json'),
          parseText('full_model_summary.txt'),
        ]);
        if (mounted) {
          setState({
            loading: false,
            error: null,
            health,
            comparison,
            coefficients,
            metadata,
            variableDictionaries,
            modelStatistics,
            modelSummary,
          });
        }
      } catch (error) {
        if (mounted) setState({ loading: false, error });
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  return state;
}
