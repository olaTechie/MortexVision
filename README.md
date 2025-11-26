# 🌍 Global Health Analytics Dashboard

A beautiful, interactive Streamlit dashboard for exploring ecological determinants of global mortality.

## 🚀 Quick Start

### Step 1: Export Data from Jupyter Notebook

First, run your analysis in the Jupyter notebook, then export the data:

```python
# After running build_progressive_models and other analyses
exec(open('save_data_for_streamlit.py').read())
```

This creates a `data/` folder with all necessary files.

### Step 2: Install Dependencies

```bash
cd streamlit_app
pip install -r requirements.txt
```

### Step 3: Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📱 Pages

### 🏠 Home
- Overview of the analysis
- Key metrics and statistics
- Regional breakdown

### 📊 Data Explorer
- Interactive data table with filtering
- Distribution plots
- Correlation analysis
- Scatter plots with trendlines

### 🗺️ Global Maps
- Choropleth maps for any indicator
- Multiple projections and color scales
- Regional comparisons
- Bubble maps

### 📈 Regression Analysis
- Model comparison (R², AIC, BIC)
- Coefficient forest plots
- Mediation analysis (coefficient changes)
- Full model summary

### 🎯 Country Profiles
- Individual country deep-dives
- Comparison with global/regional averages
- Radar charts
- Regional context

### 🔮 Policy Simulator
- What-if scenario analysis
- Single intervention simulator
- Compare multiple interventions
- Impact distribution

---

## 📁 Data Files Required

The app expects these files in the `data/` folder:

| File | Description |
|------|-------------|
| `global_health_data.csv` | Main dataset |
| `variable_dictionaries.pkl` | Variable groupings |
| `model_comparison.csv` | Model fit statistics |
| `regression_coefficients.csv` | All coefficients |
| `model_statistics.pkl` | Key model stats |
| `full_model_summary.txt` | Detailed summary |
| `metadata.pkl` | Dataset metadata |

---

## 🎨 Features

- **Beautiful Design**: Custom CSS with gradient backgrounds
- **Fully Interactive**: Plotly charts with hover, zoom, pan
- **Responsive**: Works on desktop and tablet
- **Educational**: Tooltips and explanations throughout
- **Fast**: Cached data loading for performance

---

## ⚠️ Important Notes

1. **Ecological Fallacy**: Results describe country-level relationships, not individual effects
2. **Policy Simulator**: For educational exploration only, not actual policy decisions
3. **Data Quality**: Reflects World Bank data completeness

---

## 📧 Contact

For questions about this dashboard, contact your instructor.
