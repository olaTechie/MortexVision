"""
Regression Analysis Page
========================

Explore model results, coefficients, and diagnostics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle

st.set_page_config(page_title="Regression Analysis", page_icon="📈", layout="wide")

# ============================================================================
# CLEAN CSS
# ============================================================================

st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main .block-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #1a1a2e !important;
    }
    p, li, span, label {
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_model_comparison():
    try:
        return pd.read_csv('data/model_comparison.csv')
    except FileNotFoundError:
        return None

@st.cache_data
def load_coefficients():
    try:
        return pd.read_csv('data/regression_coefficients.csv')
    except FileNotFoundError:
        return None

@st.cache_data
def load_model_stats():
    try:
        with open('data/model_statistics.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

@st.cache_data
def load_model_summary():
    try:
        with open('data/full_model_summary.txt', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

@st.cache_data
def load_var_dicts():
    try:
        with open('data/variable_dictionaries.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("📈 Regression Analysis")
st.markdown("Explore the hierarchical determinants of global mortality")

# Load data
model_comparison = load_model_comparison()
coefficients = load_coefficients()
model_stats = load_model_stats()
model_summary = load_model_summary()
var_dicts = load_var_dicts()

if model_comparison is None or coefficients is None:
    st.warning("""
    ### 📊 Model Results Not Found
    
    Please run the regression analysis and data export in your Jupyter notebook:
    
    ```python
    # Run progressive models
    model_comparison, fitted_models, diagnostic_data = build_progressive_models(...)
    
    # Export data
    exec(open('save_data_for_streamlit.py').read())
    ```
    """)
    st.stop()

# ============================================================================
# MODEL COMPARISON
# ============================================================================

st.markdown("---")
st.markdown("## 🔄 Progressive Model Comparison")

st.markdown("""
<div style="background: #e3f2fd; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <strong>Hierarchical Modelling Approach:</strong><br>
    We build models progressively to understand how different determinant levels contribute to explaining mortality variation.
</div>
""", unsafe_allow_html=True)

# Model comparison cards
cols = st.columns(len(model_comparison))

for i, (idx, row) in enumerate(model_comparison.iterrows()):
    with cols[i]:
        r2_pct = row['R²'] * 100 if 'R²' in row else row.get('r_squared', 0) * 100
        adj_r2_pct = row['Adj. R²'] * 100 if 'Adj. R²' in row else row.get('r_squared_adj', 0) * 100
        
        st.markdown(f"""
        <div class="model-card">
            <h4>{row['Model']}</h4>
            <p style="font-size: 2rem; font-weight: bold;">{r2_pct:.1f}%</p>
            <p>R² (Adj: {adj_r2_pct:.1f}%)</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem;">
                Features: {int(row.get('Num. Features', row.get('n_features', 0)))}
            </p>
        </div>
        """, unsafe_allow_html=True)

# Model comparison chart
st.markdown("### 📊 Model Fit Progression")

fig = make_subplots(rows=1, cols=2, subplot_titles=('R² Comparison', 'AIC/BIC Comparison'))

# R² plot
r2_col = 'R²' if 'R²' in model_comparison.columns else 'r_squared'
adj_r2_col = 'Adj. R²' if 'Adj. R²' in model_comparison.columns else 'r_squared_adj'

fig.add_trace(
    go.Bar(
        x=model_comparison['Model'],
        y=model_comparison[r2_col] * 100,
        name='R²',
        marker_color='#667eea'
    ),
    row=1, col=1
)

fig.add_trace(
    go.Bar(
        x=model_comparison['Model'],
        y=model_comparison[adj_r2_col] * 100,
        name='Adjusted R²',
        marker_color='#764ba2'
    ),
    row=1, col=1
)

# AIC/BIC plot
if 'AIC' in model_comparison.columns:
    fig.add_trace(
        go.Bar(
            x=model_comparison['Model'],
            y=model_comparison['AIC'],
            name='AIC',
            marker_color='#f39c12'
        ),
        row=1, col=2
    )

if 'BIC' in model_comparison.columns:
    fig.add_trace(
        go.Bar(
            x=model_comparison['Model'],
            y=model_comparison['BIC'],
            name='BIC',
            marker_color='#e74c3c'
        ),
        row=1, col=2
    )

fig.update_layout(
    height=400,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
fig.update_yaxes(title_text="Variance Explained (%)", row=1, col=1)
fig.update_yaxes(title_text="Information Criterion", row=1, col=2)

st.plotly_chart(fig, width='stretch')

# ============================================================================
# COEFFICIENT ANALYSIS
# ============================================================================

st.markdown("---")
st.markdown("## 📊 Regression Coefficients")

# Model selector
selected_model = st.selectbox(
    "Select Model",
    model_comparison['Model'].tolist(),
    index=len(model_comparison) - 1  # Default to full model
)

# Filter coefficients for selected model
model_coefs = coefficients[coefficients['Model'] == selected_model].copy()
model_coefs = model_coefs[model_coefs['Variable'] != 'const']  # Remove constant

# Categorise variables
if var_dicts:
    distal = list(var_dicts.get('distal_vars', {}).values())
    intermediate = list(var_dicts.get('intermediate_vars', {}).values())
    proximate = list(var_dicts.get('proximate_vars', {}).values())
    
    def categorise_var(var):
        if var in distal:
            return '🎯 Distal'
        elif var in intermediate:
            return '⚙️ Intermediate'
        elif var in proximate:
            return '🔬 Proximate'
        return '❓ Other'
    
    model_coefs['Category'] = model_coefs['Variable'].apply(categorise_var)
else:
    model_coefs['Category'] = 'Variable'

# Sort by absolute coefficient
model_coefs['Abs_Coef'] = model_coefs['Coefficient'].abs()
model_coefs = model_coefs.sort_values('Abs_Coef', ascending=True)

# Coefficient forest plot
st.markdown("### 🌳 Coefficient Forest Plot")

fig_forest = go.Figure()

# Add coefficient points with error bars
colors = ['#27ae60' if c < 0 else '#e74c3c' for c in model_coefs['Coefficient']]

fig_forest.add_trace(go.Scatter(
    x=model_coefs['Coefficient'],
    y=model_coefs['Variable'].apply(lambda x: x.replace('_', ' ').title()),
    mode='markers',
    marker=dict(size=12, color=colors),
    error_x=dict(
        type='data',
        symmetric=False,
        array=model_coefs['CI_Upper'] - model_coefs['Coefficient'],
        arrayminus=model_coefs['Coefficient'] - model_coefs['CI_Lower'],
        color='gray',
        thickness=2
    ),
    hovertemplate='<b>%{y}</b><br>Coefficient: %{x:.4f}<br><extra></extra>'
))

# Add vertical line at 0
fig_forest.add_vline(x=0, line_dash='dash', line_color='black', line_width=1)

fig_forest.update_layout(
    height=max(400, len(model_coefs) * 30),
    xaxis_title='Coefficient (95% CI)',
    yaxis_title='',
    showlegend=False,
    margin=dict(l=200)
)

st.plotly_chart(fig_forest, width='stretch')

# Interpretation guide
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: #e8f5e9; padding: 1rem; border-radius: 10px; border-left: 5px solid #27ae60;">
        <h4 style="color: #27ae60; margin-top: 0;">🟢 Negative Coefficients</h4>
        <p>Associated with <strong>lower mortality</strong></p>
        <p><em>e.g., Higher literacy → Lower death rate</em></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: #ffebee; padding: 1rem; border-radius: 10px; border-left: 5px solid #e74c3c;">
        <h4 style="color: #e74c3c; margin-top: 0;">🔴 Positive Coefficients</h4>
        <p>Associated with <strong>higher mortality</strong></p>
        <p><em>e.g., Higher disease burden → Higher death rate</em></p>
    </div>
    """, unsafe_allow_html=True)

# Coefficient table
st.markdown("### 📋 Detailed Coefficient Table")

coef_display = model_coefs[['Variable', 'Category', 'Coefficient', 'Std_Error', 
                            'T_Statistic', 'P_Value', 'CI_Lower', 'CI_Upper']].copy()
coef_display['Significant'] = coef_display['P_Value'].apply(
    lambda p: '✅ ***' if p < 0.001 else '✅ **' if p < 0.01 else '✅ *' if p < 0.05 else '❌'
)

# Format display
coef_display['Variable'] = coef_display['Variable'].apply(lambda x: x.replace('_', ' ').title())

st.dataframe(
    coef_display.style.format({
        'Coefficient': '{:.4f}',
        'Std_Error': '{:.4f}',
        'T_Statistic': '{:.2f}',
        'P_Value': '{:.4f}',
        'CI_Lower': '{:.4f}',
        'CI_Upper': '{:.4f}'
    }).background_gradient(subset=['P_Value'], cmap='RdYlGn'),
    width='stretch',
    hide_index=True
)

# ============================================================================
# COEFFICIENT COMPARISON ACROSS MODELS
# ============================================================================

st.markdown("---")
st.markdown("## 🔄 Coefficient Changes Across Models")

st.markdown("""
<div style="background: #fff3e0; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
    <strong>💡 Mediation Analysis:</strong><br>
    If a distal variable's coefficient <strong>decreases</strong> from Model 1 to Model 3, 
    it suggests the effect is <strong>mediated</strong> through intermediate/proximate factors.
</div>
""", unsafe_allow_html=True)

# Select variable to track
all_vars = coefficients[coefficients['Variable'] != 'const']['Variable'].unique()
selected_var = st.selectbox(
    "Select variable to track across models",
    all_vars,
    format_func=lambda x: x.replace('_', ' ').title()
)

# Get coefficients for selected variable across models
var_across_models = coefficients[coefficients['Variable'] == selected_var].copy()

if len(var_across_models) > 0:
    fig_track = go.Figure()
    
    fig_track.add_trace(go.Scatter(
        x=var_across_models['Model'],
        y=var_across_models['Coefficient'],
        mode='lines+markers',
        marker=dict(size=15, color='#667eea'),
        line=dict(width=3, color='#667eea'),
        error_y=dict(
            type='data',
            symmetric=False,
            array=var_across_models['CI_Upper'] - var_across_models['Coefficient'],
            arrayminus=var_across_models['Coefficient'] - var_across_models['CI_Lower'],
            color='gray'
        )
    ))
    
    fig_track.add_hline(y=0, line_dash='dash', line_color='gray')
    
    fig_track.update_layout(
        title=f'Coefficient for {selected_var.replace("_", " ").title()} Across Models',
        xaxis_title='Model',
        yaxis_title='Coefficient (95% CI)',
        height=400
    )
    
    st.plotly_chart(fig_track, width='stretch')
    
    # Calculate change
    if len(var_across_models) >= 2:
        first_coef = var_across_models.iloc[0]['Coefficient']
        last_coef = var_across_models.iloc[-1]['Coefficient']
        
        if first_coef != 0:
            pct_change = ((last_coef - first_coef) / abs(first_coef)) * 100
            
            if abs(pct_change) > 20:
                interpretation = "🔄 **Substantial attenuation** - effect is partially mediated" if pct_change < 0 else "📈 **Effect strengthened** after controlling for other factors"
            else:
                interpretation = "➡️ **Stable effect** - direct relationship with mortality"
            
            st.info(f"""
            **Coefficient Change:** {first_coef:.4f} → {last_coef:.4f} ({pct_change:+.1f}%)
            
            {interpretation}
            """)

# ============================================================================
# FULL MODEL SUMMARY
# ============================================================================

st.markdown("---")
st.markdown("## 📄 Full Model Summary")

if model_summary:
    with st.expander("View Complete Statsmodels Output"):
        st.code(model_summary, language='text')
else:
    st.info("Full model summary not available.")

# Model statistics
if model_stats:
    st.markdown("### 📊 Key Model Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("R²", f"{model_stats.get('r_squared', 0):.4f}")
    with col2:
        st.metric("Adjusted R²", f"{model_stats.get('r_squared_adj', 0):.4f}")
    with col3:
        st.metric("F-statistic", f"{model_stats.get('f_statistic', 0):.2f}")
    with col4:
        st.metric("Observations", f"{model_stats.get('n_obs', 0)}")
