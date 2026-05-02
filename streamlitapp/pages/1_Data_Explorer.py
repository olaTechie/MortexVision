"""
Data Explorer Page
==================

Interactive data exploration with filtering and visualisation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")

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
def load_data():
    try:
        df = pd.read_csv('data/global_health_data.csv')
        return df
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

st.title("📊 Data Explorer")

df = load_data()
var_dicts = load_var_dicts()

if df is None:
    st.error("Data not found. Please run the data export script first.")
    st.stop()

# ============================================================================
# FILTERS SIDEBAR
# ============================================================================

st.sidebar.markdown("## 🔍 Filters")

# Region filter
if 'region' in df.columns:
    regions = ['All'] + sorted(df['region'].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("🌍 Region", regions)
else:
    selected_region = 'All'

# Income level filter
if 'income_level' in df.columns:
    income_levels = ['All'] + sorted(df['income_level'].dropna().unique().tolist())
    selected_income = st.sidebar.selectbox("💰 Income Level", income_levels)
else:
    selected_income = 'All'

# Mortality range filter
if 'crude_death_rate' in df.columns:
    min_mort = float(df['crude_death_rate'].min())
    max_mort = float(df['crude_death_rate'].max())
    mortality_range = st.sidebar.slider(
        "☠️ Mortality Rate Range",
        min_mort, max_mort, (min_mort, max_mort)
    )
else:
    mortality_range = None

# Apply filters
df_filtered = df.copy()

if selected_region != 'All':
    df_filtered = df_filtered[df_filtered['region'] == selected_region]

if selected_income != 'All':
    df_filtered = df_filtered[df_filtered['income_level'] == selected_income]

if mortality_range and 'crude_death_rate' in df.columns:
    df_filtered = df_filtered[
        (df_filtered['crude_death_rate'] >= mortality_range[0]) &
        (df_filtered['crude_death_rate'] <= mortality_range[1])
    ]

# Show filter status
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** {len(df_filtered)} / {len(df)} countries")

# ============================================================================
# MAIN CONTENT TABS
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Data Table", 
    "📊 Distributions", 
    "🔗 Correlations",
    "📈 Scatter Plots"
])

# ----------------------------------------------------------------------------
# TAB 1: DATA TABLE
# ----------------------------------------------------------------------------

with tab1:
    st.markdown("### 📋 Country Data")
    
    # Column selector
    all_cols = df_filtered.columns.tolist()
    default_cols = ['country', 'region', 'crude_death_rate', 'gni_per_capita', 
                    'adult_literacy', 'physicians_density']
    default_cols = [c for c in default_cols if c in all_cols]
    
    selected_cols = st.multiselect(
        "Select columns to display",
        all_cols,
        default=default_cols
    )
    
    if selected_cols:
        # Format numeric columns
        display_df = df_filtered[selected_cols].copy()
        
        st.dataframe(
            display_df.style.format({
                col: "{:.2f}" for col in display_df.select_dtypes(include=[np.number]).columns
            }).background_gradient(subset=['crude_death_rate'] if 'crude_death_rate' in selected_cols else [], cmap='RdYlGn_r'),
            width='stretch',
            height=500
        )
        
        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            "📥 Download Filtered Data",
            csv,
            "filtered_data.csv",
            "text/csv",
            key='download-csv'
        )

# ----------------------------------------------------------------------------
# TAB 2: DISTRIBUTIONS
# ----------------------------------------------------------------------------

with tab2:
    st.markdown("### 📊 Variable Distributions")
    
    # Get numeric columns
    numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['latitude', 'longitude']]
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        selected_var = st.selectbox("Select Variable", numeric_cols, 
                                    index=numeric_cols.index('crude_death_rate') if 'crude_death_rate' in numeric_cols else 0)
        
        show_by_region = st.checkbox("Split by Region", value=True)
        
        # Statistics
        st.markdown("#### 📈 Statistics")
        stats = df_filtered[selected_var].describe()
        st.dataframe(stats.round(2))
    
    with col2:
        if show_by_region and 'region' in df_filtered.columns:
            fig = px.histogram(
                df_filtered.dropna(subset=[selected_var]),
                x=selected_var,
                color='region',
                marginal='box',
                nbins=30,
                color_discrete_sequence=px.colors.qualitative.Set2,
                title=f'Distribution of {selected_var.replace("_", " ").title()}'
            )
        else:
            fig = px.histogram(
                df_filtered.dropna(subset=[selected_var]),
                x=selected_var,
                marginal='box',
                nbins=30,
                color_discrete_sequence=['#667eea'],
                title=f'Distribution of {selected_var.replace("_", " ").title()}'
            )
        
        fig.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        st.plotly_chart(fig, width='stretch')

# ----------------------------------------------------------------------------
# TAB 3: CORRELATIONS
# ----------------------------------------------------------------------------

with tab3:
    st.markdown("### 🔗 Correlation Analysis")
    
    # Select variables for correlation
    numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['latitude', 'longitude']]
    
    # Group variables by type
    if var_dicts:
        distal = list(var_dicts.get('distal_vars', {}).values())
        intermediate = list(var_dicts.get('intermediate_vars', {}).values())
        proximate = list(var_dicts.get('proximate_vars', {}).values())
        
        st.markdown("""
        <div style="background: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <b>Variable Groups:</b><br>
            🎯 <b>Distal:</b> {} <br>
            ⚙️ <b>Intermediate:</b> {} <br>
            🔬 <b>Proximate:</b> {}
        </div>
        """.format(
            ', '.join(distal[:3]) + '...' if len(distal) > 3 else ', '.join(distal),
            ', '.join(intermediate[:3]) + '...' if len(intermediate) > 3 else ', '.join(intermediate),
            ', '.join(proximate[:3]) + '...' if len(proximate) > 3 else ', '.join(proximate)
        ), unsafe_allow_html=True)
    
    selected_corr_vars = st.multiselect(
        "Select variables for correlation matrix",
        numeric_cols,
        default=numeric_cols[:8]
    )
    
    if len(selected_corr_vars) >= 2:
        corr_matrix = df_filtered[selected_corr_vars].corr()
        
        fig = px.imshow(
            corr_matrix,
            text_auto='.2f',
            aspect='auto',
            color_continuous_scale='RdBu_r',
            zmin=-1, zmax=1,
            title='Correlation Matrix'
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, width='stretch')
        
        # Top correlations with outcome
        if 'crude_death_rate' in selected_corr_vars:
            st.markdown("#### 🎯 Top Correlations with Mortality")
            
            mort_corr = corr_matrix['crude_death_rate'].drop('crude_death_rate').sort_values(key=abs, ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Positive Correlations** (↑ mortality)")
                pos_corr = mort_corr[mort_corr > 0].head(5)
                for var, val in pos_corr.items():
                    st.markdown(f"- {var.replace('_', ' ').title()}: **{val:.3f}**")
            
            with col2:
                st.markdown("**Negative Correlations** (↓ mortality)")
                neg_corr = mort_corr[mort_corr < 0].head(5)
                for var, val in neg_corr.items():
                    st.markdown(f"- {var.replace('_', ' ').title()}: **{val:.3f}**")

# ----------------------------------------------------------------------------
# TAB 4: SCATTER PLOTS
# ----------------------------------------------------------------------------

with tab4:
    st.markdown("### 📈 Scatter Plots")
    
    numeric_cols = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['latitude', 'longitude']]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x_var = st.selectbox("X-axis", numeric_cols, 
                            index=numeric_cols.index('gni_per_capita') if 'gni_per_capita' in numeric_cols else 0)
    
    with col2:
        y_var = st.selectbox("Y-axis", numeric_cols,
                            index=numeric_cols.index('crude_death_rate') if 'crude_death_rate' in numeric_cols else 1)
    
    with col3:
        size_var = st.selectbox("Size (optional)", ['None'] + numeric_cols,
                               index=0)
    
    col1, col2 = st.columns(2)
    with col1:
        log_x = st.checkbox("Log scale X-axis", value=(x_var == 'gni_per_capita'))
    with col2:
        log_y = st.checkbox("Log scale Y-axis", value=False)
    
    color_var = 'region' if 'region' in df_filtered.columns else None
    
    # Create scatter plot
    fig = px.scatter(
        df_filtered.dropna(subset=[x_var, y_var]),
        x=x_var,
        y=y_var,
        color=color_var,
        size=size_var if size_var != 'None' else None,
        hover_name='country' if 'country' in df_filtered.columns else None,
        log_x=log_x,
        log_y=log_y,
        trendline='lowess',
        trendline_color_override='black',
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=f'{y_var.replace("_", " ").title()} vs {x_var.replace("_", " ").title()}'
    )
    
    fig.update_layout(
        height=600,
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    fig.update_traces(marker=dict(opacity=0.7, line=dict(width=1, color='white')))
    
    st.plotly_chart(fig, width='stretch')
    
    # Correlation coefficient
    valid_data = df_filtered[[x_var, y_var]].dropna()
    if len(valid_data) > 2:
        corr = valid_data[x_var].corr(valid_data[y_var])
        st.info(f"**Pearson Correlation:** r = {corr:.3f} (n = {len(valid_data)})")
