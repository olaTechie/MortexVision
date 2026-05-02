# MortexVision

MortexVision is a production-ready React/Vite migration of the original Streamlit Global Health Ecological Analysis dashboard. It preserves the original data exploration, maps, regression interpretation, country profiles, and policy simulation workflows while adding a polished multi-page interface, subtle motion, responsive navigation, and GitHub Pages deployment.

## Migration Summary

- Streamlit home page -> `Overview`
- `1_Data_Explorer.py` -> `Data Explorer`
- `2_Global_Maps.py` -> `Global Maps`
- `3_Regression_Analysis.py` -> `Analytics` and `Reports`
- `4_Country_Profiles.py` -> `Country Profiles`
- `5_Policy_Simulator.py` -> `Policy Simulator`
- Pickle metadata/model files were converted to JSON so the app can run as a static GitHub Pages site.

## Tech Stack

- React 18
- Vite
- React Router
- Plotly
- Framer Motion
- Papa Parse
- Lucide React
- GitHub Actions and GitHub Pages

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
npm run preview
```

The production build uses the Vite base path `/MortexVision/`. The `postbuild` script copies `dist/index.html` to `dist/404.html` for GitHub Pages SPA fallback routing.

## Deployment

1. Create a GitHub repository named `MortexVision`.
2. Push this project to the `main` branch.
3. In GitHub, open `Settings -> Pages`.
4. Set `Source` to `GitHub Actions`.
5. Push to `main` or run the `Deploy to GitHub Pages` workflow manually.

Expected URL:

```text
https://YOUR_GITHUB_USERNAME.github.io/MortexVision/
```

## Repository Setup Commands

```bash
git init
git add .
git commit -m "feat: migrate Streamlit dashboard to MortexVision React app"
git branch -M main
git remote add origin git@github.com:YOUR_GITHUB_USERNAME/MortexVision.git
git push -u origin main
```

## Notes

This dashboard uses country-level aggregate data. Results are ecological associations, not individual-level causal claims. The policy simulator uses a simplified linear approximation based on regression coefficients and is intended for educational scenario exploration.
