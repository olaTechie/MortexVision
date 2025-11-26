"""
Country Profiles Page
=====================

Deep-dive into individual country data and comparisons.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle

st.set_page_config(page_title="Country Profiles", page_icon="🎯", layout="wide")

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

st.title("🎯 Country Profiles")
st.markdown("Explore detailed health indicators for individual countries")

df = load_data()
var_dicts = load_var_dicts()

if df is None:
    st.error("Data not found. Please run the data export script first.")
    st.stop()

# ============================================================================
# COUNTRY SELECTOR
# ============================================================================

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    # Country search
    if 'country' in df.columns:
        countries = sorted(df['country'].dropna().unique().tolist())
        selected_country = st.selectbox(
            "🔍 Search for a country",
            countries,
            index=countries.index('United Kingdom') if 'United Kingdom' in countries else 0
        )
    else:
        st.error("Country names not found in data.")
        st.stop()

with col2:
    # Comparison option
    compare_to = st.selectbox(
        "📊 Compare to",
        ['Global Average', 'Regional Average'] + (['Income Group Average'] if 'income_level' in df.columns else [])
    )

# Get country data
country_data = df[df['country'] == selected_country].iloc[0]

# ============================================================================
# COUNTRY HEADER
# ============================================================================

region = country_data.get('region', 'Unknown')
income = country_data.get('income_level', 'Unknown')

st.markdown(f"""
<div class="country-header">
    <h1>🏳️ {selected_country}</h1>
    <p style="font-size: 1.2rem; margin: 0.5rem 0 0 0;">
        {region} | {income}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# KEY METRICS
# ============================================================================

# Calculate comparison values
if compare_to == 'Global Average':
    comparison_data = df.mean(numeric_only=True)
    comparison_label = "Global Avg"
elif compare_to == 'Regional Average' and 'region' in df.columns:
    comparison_data = df[df['region'] == region].mean(numeric_only=True)
    comparison_label = f"{region} Avg"
elif compare_to == 'Income Group Average' and 'income_level' in df.columns:
    comparison_data = df[df['income_level'] == income].mean(numeric_only=True)
    comparison_label = f"{income} Avg"
else:
    comparison_data = df.mean(numeric_only=True)
    comparison_label = "Global Avg"

# Key indicators
key_indicators = [
    ('crude_death_rate', '☠️ Death Rate', 'per 1,000', True),  # True = lower is better
    ('gni_per_capita', '💰 GNI per Capita', 'USD', False),
    ('adult_literacy', '📚 Adult Literacy', '%', False),
    ('physicians_density', '👨‍⚕️ Physicians', 'per 1,000', False),
    ('safe_water', '💧 Safe Water', '%', False),
    ('basic_sanitation', '🚿 Sanitation', '%', False)
]

st.markdown("### 📊 Key Indicators")

cols = st.columns(3)
for i, (var, label, unit, lower_better) in enumerate(key_indicators):
    if var in country_data.index:
        value = country_data[var]
        comp_value = comparison_data.get(var, np.nan)
        
        if pd.notna(value):
            # Calculate comparison
            if pd.notna(comp_value) and comp_value != 0:
                diff = value - comp_value
                pct_diff = (diff / comp_value) * 100
                
                if lower_better:
                    is_better = diff < 0
                else:
                    is_better = diff > 0
                
                comparison_class = "comparison-better" if is_better else "comparison-worse"
                comparison_text = f"{'↓' if diff < 0 else '↑'} {abs(pct_diff):.1f}% vs {comparison_label}"
            else:
                comparison_text = ""
                comparison_class = ""
            
            with cols[i % 3]:
                st.markdown(f"""
                <div class="indicator-card">
                    <div class="indicator-label">{label}</div>
                    <div class="indicator-value">{value:.1f}</div>
                    <div style="font-size: 0.8rem; color: #999;">{unit}</div>
                    <div class="{comparison_class}" style="font-size: 0.85rem; margin-top: 0.5rem;">
                        {comparison_text}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# RADAR CHART
# ============================================================================

st.markdown("---")
st.markdown("### 🕸️ Health Profile Comparison")

# Select variables for radar chart
radar_vars = ['crude_death_rate', 'gni_per_capita', 'adult_literacy', 
              'physicians_density', 'safe_water', 'communicable_disease_deaths']
radar_vars = [v for v in radar_vars if v in df.columns]

if len(radar_vars) >= 3:
    # Normalise values to 0-100 scale
    radar_data = []
    
    for var in radar_vars:
        country_val = country_data.get(var, np.nan)
        
        if pd.notna(country_val):
            # Normalise using percentile
            percentile = (df[var] <= country_val).mean() * 100
            
            # For death rate, invert (lower is better)
            if 'death' in var.lower():
                percentile = 100 - percentile
            
            radar_data.append({
                'variable': var.replace('_', ' ').title(),
                'value': percentile,
                'type': selected_country
            })
            
            # Add comparison
            comp_val = comparison_data.get(var, np.nan)
            if pd.notna(comp_val):
                comp_percentile = (df[var] <= comp_val).mean() * 100
                if 'death' in var.lower():
                    comp_percentile = 100 - comp_percentile
                
                radar_data.append({
                    'variable': var.replace('_', ' ').title(),
                    'value': comp_percentile,
                    'type': comparison_label
                })
    
    radar_df = pd.DataFrame(radar_data)
    
    fig_radar = px.line_polar(
        radar_df,
        r='value',
        theta='variable',
        color='type',
        line_close=True,
        color_discrete_sequence=['#667eea', '#aaa'],
        title='Country Profile (Percentile Ranking)'
    )
    
    fig_radar.update_traces(fill='toself', opacity=0.5)
    fig_radar.update_layout(
        height=500,
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )
    
    st.plotly_chart(fig_radar, width='stretch')
    
    st.info("💡 Values show percentile rankings (0-100). Higher = better health outcomes.")

# ============================================================================
# ALL INDICATORS
# ============================================================================

st.markdown("---")
st.markdown("### 📋 All Available Indicators")

# Group variables
if var_dicts:
    distal = list(var_dicts.get('distal_vars', {}).values())
    intermediate = list(var_dicts.get('intermediate_vars', {}).values())
    proximate = list(var_dicts.get('proximate_vars', {}).values())
else:
    distal = intermediate = proximate = []

tab1, tab2, tab3, tab4 = st.tabs(["🎯 Distal", "⚙️ Intermediate", "🔬 Proximate", "📊 All"])

def create_indicator_table(variables, country_data, comparison_data, df):
    """Create a formatted indicator table"""
    rows = []
    for var in variables:
        if var in country_data.index:
            value = country_data[var]
            comp = comparison_data.get(var, np.nan)
            
            if pd.notna(value):
                # Calculate global rank
                rank = (df[var] <= value).sum() if 'death' not in var.lower() else (df[var] >= value).sum()
                total = df[var].notna().sum()
                
                rows.append({
                    'Indicator': var.replace('_', ' ').title(),
                    'Value': f"{value:.2f}",
                    'Comparison': f"{comp:.2f}" if pd.notna(comp) else "N/A",
                    'Global Rank': f"{rank}/{total}"
                })
    
    return pd.DataFrame(rows)

with tab1:
    if distal:
        distal_table = create_indicator_table(distal, country_data, comparison_data, df)
        if len(distal_table) > 0:
            st.dataframe(distal_table, width='stretch', hide_index=True)
        else:
            st.info("No distal indicators available for this country.")
    else:
        st.info("Variable categories not defined.")

with tab2:
    if intermediate:
        intermediate_table = create_indicator_table(intermediate, country_data, comparison_data, df)
        if len(intermediate_table) > 0:
            st.dataframe(intermediate_table, width='stretch', hide_index=True)
        else:
            st.info("No intermediate indicators available for this country.")

with tab3:
    if proximate:
        proximate_table = create_indicator_table(proximate, country_data, comparison_data, df)
        if len(proximate_table) > 0:
            st.dataframe(proximate_table, width='stretch', hide_index=True)
        else:
            st.info("No proximate indicators available for this country.")

with tab4:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['latitude', 'longitude']]
    all_table = create_indicator_table(numeric_cols, country_data, comparison_data, df)
    st.dataframe(all_table, width='stretch', hide_index=True)

# ============================================================================
# COUNTRY COMPARISON
# ============================================================================

st.markdown("---")
st.markdown("### 🔄 Compare Countries")

col1, col2 = st.columns(2)

with col1:
    compare_countries = st.multiselect(
        "Select countries to compare",
        [c for c in countries if c != selected_country],
        default=[countries[min(5, len(countries)-1)]] if len(countries) > 1 else []
    )

with col2:
    compare_var = st.selectbox(
        "Select indicator",
        [c for c in df.select_dtypes(include=[np.number]).columns if c not in ['latitude', 'longitude']],
        index=0
    )

if compare_countries:
    all_compare = [selected_country] + compare_countries
    compare_df = df[df['country'].isin(all_compare)][['country', compare_var]].dropna()
    
    if len(compare_df) > 0:
        fig_compare = px.bar(
            compare_df.sort_values(compare_var, ascending=True),
            x=compare_var,
            y='country',
            orientation='h',
            color='country',
            color_discrete_sequence=px.colors.qualitative.Set2,
            title=f'{compare_var.replace("_", " ").title()} Comparison'
        )
        
        fig_compare.update_layout(
            height=max(300, len(all_compare) * 50),
            showlegend=False,
            yaxis_title='',
            xaxis_title=compare_var.replace('_', ' ').title()
        )
        
        st.plotly_chart(fig_compare, width='stretch')

# ============================================================================
# REGIONAL CONTEXT
# ============================================================================

st.markdown("---")
st.markdown(f"### 🌍 Regional Context: {region}")

if 'region' in df.columns:
    regional_df = df[df['region'] == region].copy()
    
    if len(regional_df) > 1 and 'crude_death_rate' in regional_df.columns:
        # Rank within region
        regional_df_sorted = regional_df.sort_values('crude_death_rate')
        country_rank = (regional_df_sorted['country'] == selected_country).argmax() + 1
        
        st.markdown(f"""
        **{selected_country}** ranks **{country_rank}** out of **{len(regional_df)}** countries 
        in {region} for mortality rate (lower = better).
        """)
        
        # Regional bar chart
        fig_regional = px.bar(
            regional_df_sorted.head(20),
            x='country',
            y='crude_death_rate',
            color='crude_death_rate',
            color_continuous_scale='RdYlGn_r',
            title=f'Mortality Rates in {region}'
        )
        
        # Highlight selected country
        colors = ['#667eea' if c == selected_country else '#ddd' for c in regional_df_sorted.head(20)['country']]
        fig_regional.update_traces(marker_color=colors)
        
        fig_regional.update_layout(
            height=400,
            xaxis_tickangle=45,
            showlegend=False,
            xaxis_title='',
            yaxis_title='Crude Death Rate (per 1,000)'
        )
        
        st.plotly_chart(fig_regional, width='stretch')
