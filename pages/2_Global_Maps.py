"""
Global Maps Page
================

Interactive choropleth maps and geographic visualisations.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Global Maps", page_icon="🗺️", layout="wide")

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

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("🗺️ Global Maps")
st.markdown("Explore the geographic distribution of health indicators across the world")

df = load_data()

if df is None:
    st.error("Data not found. Please run the data export script first.")
    st.stop()

# Check for ISO codes
if 'iso3_code' not in df.columns:
    st.error("ISO codes not found in data. Maps require ISO3 country codes.")
    st.stop()

# ============================================================================
# MAP CONTROLS
# ============================================================================

st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    # Variable selector
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['latitude', 'longitude', 'total_population']]
    
    # Group variables
    outcome_vars = [c for c in numeric_cols if 'death' in c.lower() or 'mortality' in c.lower()]
    other_vars = [c for c in numeric_cols if c not in outcome_vars]
    
    selected_var = st.selectbox(
        "🎯 Select Indicator to Map",
        ['crude_death_rate'] + outcome_vars + other_vars,
        format_func=lambda x: x.replace('_', ' ').title()
    )

with col2:
    # Color scale
    color_scales = {
        'Viridis': 'Viridis',
        'Plasma': 'Plasma',
        'Inferno': 'Inferno',
        'Red-Yellow-Green': 'RdYlGn',
        'Red-Blue': 'RdBu',
        'Blues': 'Blues',
        'Reds': 'Reds',
        'Greens': 'Greens'
    }
    
    # Reverse for mortality (high = bad = red)
    default_scale = 'Red-Yellow-Green' if 'death' in selected_var or 'mortality' in selected_var else 'Viridis'
    color_scale = st.selectbox("🎨 Color Scale", list(color_scales.keys()), 
                               index=list(color_scales.keys()).index(default_scale))

with col3:
    # Projection
    projections = {
        'Natural Earth': 'natural earth',
        'Equirectangular': 'equirectangular',
        'Mercator': 'mercator',
        'Orthographic': 'orthographic',
        'Robinson': 'robinson'
    }
    projection = st.selectbox("🌐 Projection", list(projections.keys()))

# Reverse scale option
reverse_scale = st.checkbox(
    "Reverse color scale", 
    value=('death' in selected_var.lower() or 'mortality' in selected_var.lower())
)

# ============================================================================
# MAIN CHOROPLETH MAP
# ============================================================================

st.markdown("---")
st.markdown(f"### 🌍 Global Distribution: {selected_var.replace('_', ' ').title()}")

# Prepare data
df_map = df.dropna(subset=[selected_var, 'iso3_code']).copy()

# Create choropleth
fig = px.choropleth(
    df_map,
    locations='iso3_code',
    color=selected_var,
    hover_name='country' if 'country' in df_map.columns else None,
    hover_data={
        'iso3_code': False,
        selected_var: ':.2f',
        'region': True if 'region' in df_map.columns else False
    },
    color_continuous_scale=color_scales[color_scale] + ('_r' if reverse_scale else ''),
    projection=projections[projection],
    title=None
)

fig.update_layout(
    height=600,
    margin=dict(l=0, r=0, t=0, b=0),
    geo=dict(
        showframe=False,
        showcoastlines=True,
        coastlinecolor='lightgray',
        showland=True,
        landcolor='#f8f9fa',
        showocean=True,
        oceancolor='#e3f2fd',
        showcountries=True,
        countrycolor='white',
        countrywidth=0.5
    ),
    coloraxis_colorbar=dict(
        title=dict(text=selected_var.replace('_', ' ').title(), font=dict(size=12)),
        thickness=15,
        len=0.7
    )
)

st.plotly_chart(fig, width='stretch')

# Statistics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("🔻 Minimum", f"{df_map[selected_var].min():.2f}")
with col2:
    st.metric("📊 Median", f"{df_map[selected_var].median():.2f}")
with col3:
    st.metric("📈 Mean", f"{df_map[selected_var].mean():.2f}")
with col4:
    st.metric("🔺 Maximum", f"{df_map[selected_var].max():.2f}")
with col5:
    st.metric("📉 Std Dev", f"{df_map[selected_var].std():.2f}")

# ============================================================================
# REGIONAL COMPARISON
# ============================================================================

st.markdown("---")
st.markdown("### 🌐 Regional Comparison")

if 'region' in df.columns:
    # Box plot by region
    fig_box = px.box(
        df.dropna(subset=[selected_var]),
        x='region',
        y=selected_var,
        color='region',
        color_discrete_sequence=px.colors.qualitative.Set2,
        title=f'{selected_var.replace("_", " ").title()} by Region'
    )
    
    fig_box.update_layout(
        height=450,
        showlegend=False,
        xaxis_title="",
        yaxis_title=selected_var.replace('_', ' ').title()
    )
    fig_box.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig_box, width='stretch')
    
    # Regional statistics table
    with st.expander("📊 Regional Statistics"):
        regional_stats = df.groupby('region')[selected_var].agg([
            'count', 'mean', 'median', 'std', 'min', 'max'
        ]).round(2)
        regional_stats.columns = ['N', 'Mean', 'Median', 'Std Dev', 'Min', 'Max']
        regional_stats = regional_stats.sort_values('Mean', ascending=False)
        
        st.dataframe(regional_stats, width='stretch')

# ============================================================================
# BUBBLE MAP
# ============================================================================

st.markdown("---")
st.markdown("### 🔵 Bubble Map")

if 'latitude' in df.columns and 'longitude' in df.columns:
    col1, col2 = st.columns(2)
    
    with col1:
        bubble_color = st.selectbox(
            "Color by",
            numeric_cols,
            index=numeric_cols.index(selected_var) if selected_var in numeric_cols else 0,
            key='bubble_color'
        )
    
    with col2:
        bubble_size = st.selectbox(
            "Size by",
            ['total_population'] + numeric_cols if 'total_population' in df.columns else numeric_cols,
            key='bubble_size'
        )
    
    df_bubble = df.dropna(subset=['latitude', 'longitude', bubble_color]).copy()
    
    # Handle size variable
    if bubble_size in df_bubble.columns:
        df_bubble['size_scaled'] = df_bubble[bubble_size].fillna(df_bubble[bubble_size].median())
        # Ensure positive values for size
        df_bubble['size_scaled'] = df_bubble['size_scaled'].clip(lower=1)
    else:
        df_bubble['size_scaled'] = 10
    
    fig_bubble = px.scatter_geo(
        df_bubble,
        lat='latitude',
        lon='longitude',
        color=bubble_color,
        size='size_scaled',
        hover_name='country' if 'country' in df_bubble.columns else None,
        hover_data={
            'latitude': False,
            'longitude': False,
            'size_scaled': False,
            bubble_color: ':.2f',
            bubble_size: ':.0f' if bubble_size != bubble_color else False
        },
        color_continuous_scale=color_scales[color_scale] + ('_r' if reverse_scale else ''),
        projection=projections[projection],
        size_max=40
    )
    
    fig_bubble.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor='lightgray',
            showland=True,
            landcolor='#f8f9fa',
            showocean=True,
            oceancolor='#e3f2fd'
        )
    )
    
    st.plotly_chart(fig_bubble, width='stretch')

else:
    st.info("Latitude and longitude data not available for bubble map.")

# ============================================================================
# TOP/BOTTOM COUNTRIES
# ============================================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### 🔺 Highest {selected_var.replace('_', ' ').title()}")
    top_10 = df.nlargest(10, selected_var)[['country', 'region', selected_var]].copy()
    top_10[selected_var] = top_10[selected_var].round(2)
    st.dataframe(top_10, width='stretch', hide_index=True)

with col2:
    st.markdown(f"### 🔻 Lowest {selected_var.replace('_', ' ').title()}")
    bottom_10 = df.nsmallest(10, selected_var)[['country', 'region', selected_var]].copy()
    bottom_10[selected_var] = bottom_10[selected_var].round(2)
    st.dataframe(bottom_10, width='stretch', hide_index=True)
