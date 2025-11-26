"""
Global Health Ecological Analysis Dashboard
============================================

A comprehensive interactive dashboard for exploring ecological 
determinants of global mortality.

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Global Health Analytics",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/yourusername/ecological-workshop',
        'Report a bug': 'https://github.com/yourusername/ecological-workshop/issues',
        'About': """
        ## Global Health Ecological Analysis
        
        This dashboard explores the hierarchical determinants of global mortality
        using World Bank data and ecological regression analysis.
        
        **Author:** Professor of Global Health  
        **Data Source:** World Bank Open Data
        """
    }
)

# ============================================================================
# MINIMAL, CLEAN CSS - HIGH CONTRAST
# ============================================================================

st.markdown("""
<style>
    /* Clean white background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Main container */
    .main .block-container {
        background: white;
        border-radius: 10px;
        padding: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar - LIGHT background to match other pages */
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #1a1a2e;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #1a1a2e !important;
    }
    
    /* Headers - solid dark colours for contrast */
    h1 {
        color: #1a1a2e !important;
        font-weight: 700;
    }
    
    h2 {
        color: #1a1a2e !important;
        border-bottom: 2px solid #4dabf7;
        padding-bottom: 8px;
    }
    
    h3 {
        color: #333333 !important;
    }
    
    /* All paragraph text should be dark */
    p, li, span {
        color: #333333;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #e7f5ff;
        border: 1px solid #4dabf7;
        color: #1a1a2e;
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        color: #333333;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data
def load_main_data():
    """Load the main dataset"""
    try:
        df = pd.read_csv('data/global_health_data.csv')
        return df
    except FileNotFoundError:
        return None

@st.cache_data
def load_metadata():
    """Load metadata"""
    try:
        with open('data/metadata.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

@st.cache_data
def load_model_stats():
    """Load model statistics"""
    try:
        with open('data/model_statistics.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


# ============================================================================
# MAIN PAGE CONTENT
# ============================================================================

def main():
    # Title
    st.title("🌍 Global Health Analytics")
    st.markdown("**Exploring the hierarchical determinants of global mortality through ecological analysis of World Bank indicators**")
    
    st.markdown("---")
    
    # Load data
    df = load_main_data()
    metadata = load_metadata()
    model_stats = load_model_stats()
    
    if df is None:
        st.warning("""
        ### Data Not Found
        
        Please run the data export script in your Jupyter notebook first:
        
        ```python
        exec(open('save_data_for_streamlit.py').read())
        ```
        
        Then restart this Streamlit app.
        """)
        return
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Countries Analysed", len(df))
    
    with col2:
        n_regions = df['region'].nunique() if 'region' in df.columns else 0
        st.metric("World Regions", n_regions)
    
    with col3:
        n_vars = len([c for c in df.columns if c not in ['country', 'iso3_code', 'region', 'income_level']])
        st.metric("Health Indicators", n_vars)
    
    with col4:
        if model_stats:
            r2 = model_stats.get('r_squared_adj', 0) * 100
            st.metric("Variance Explained", f"{r2:.1f}%")
        else:
            st.metric("Variance Explained", "N/A")
    
    st.markdown("---")
    
    # Two column layout for content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📖 About This Dashboard")
        
        st.markdown("""
        This interactive dashboard presents an **ecological analysis** of global mortality 
        determinants using data from the World Bank. The analysis follows a hierarchical 
        framework based on the **Social Determinants of Health** model:
        """)
        
        st.subheader("🎯 Distal Determinants (Root Causes)")
        st.markdown("Socioeconomic factors: GNI per capita, education levels, inequality")
        
        st.subheader("⚙️ Intermediate Determinants (Systems)")
        st.markdown("Healthcare capacity, infrastructure: physicians, sanitation, water access")
        
        st.subheader("🔬 Proximate Determinants (Direct Causes)")
        st.markdown("Disease burden, risk factors: communicable diseases, NCDs, immunisation")
    
    with col2:
        st.header("🧭 Navigation")
        
        st.markdown("""
        Use the sidebar to explore different sections:
        
        - **Data Explorer** - Browse and filter the dataset
        - **Global Maps** - Geographic visualisations
        - **Regression Analysis** - Model results and diagnostics
        - **Country Profiles** - Individual country deep-dives
        - **Policy Simulator** - "What-if" scenario analysis
        """)
        
        st.info("💡 **Tip:** Click on the page names in the sidebar to navigate between sections.")
    
    # Ecological Fallacy Warning
    st.markdown("---")
    
    st.warning("""
    ### ⚠️ Important: The Ecological Fallacy
    
    This analysis uses **country-level (aggregate) data**. Relationships observed at the 
    country level may not apply to individuals within those countries. This is known as 
    the **ecological fallacy**.
    
    For example, if countries with higher average income have higher mortality rates, 
    we **cannot** conclude that richer individuals have higher mortality. The pattern 
    might be reversed at the individual level due to confounding factors like age structure.
    
    **Always interpret ecological analyses with caution.**
    """)
    
    # Data overview
    st.markdown("---")
    st.header("📋 Data Overview")
    
    with st.expander("View Sample Data", expanded=False):
        st.dataframe(
            df.head(20).style.format({
                col: "{:.2f}" for col in df.select_dtypes(include=[np.number]).columns
            }),
            width='stretch'
        )
    
    # Regional breakdown
    if 'region' in df.columns:
        st.subheader("🌐 Countries by Region")
        
        region_counts = df['region'].value_counts()
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.dataframe(
                pd.DataFrame({
                    'Region': region_counts.index,
                    'Countries': region_counts.values
                }),
                width='stretch',
                hide_index=True
            )
        
        with col2:
            import plotly.express as px
            fig = px.pie(
                values=region_counts.values,
                names=region_counts.index,
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, width='stretch')
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Global Health Ecological Analysis Dashboard** | Data Source: World Bank Open Data | Built with Streamlit
    """)


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🌍 Global Health")
    st.markdown("*Ecological Analysis Dashboard*")
    
    st.markdown("---")
    
    # Navigation section
    st.markdown("### 📍 Navigation")
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_Data_Explorer.py", label="📊 Data Explorer", icon="📊")
    st.page_link("pages/2_Global_Maps.py", label="🗺️ Global Maps", icon="🗺️")
    st.page_link("pages/3_Regression_Analysis.py", label="📈 Regression Analysis", icon="📈")
    st.page_link("pages/4_Country_Profiles.py", label="🎯 Country Profiles", icon="🎯")
    st.page_link("pages/5_Policy_Simulator.py", label="🔮 Policy Simulator", icon="🔮")
    
    st.markdown("---")
    
    # Load metadata for sidebar
    metadata = load_metadata()
    if metadata:
        st.markdown("### 📊 Dataset Info")
        st.markdown(f"**Countries:** {metadata.get('n_countries', 'N/A')}")
        st.markdown(f"**Variables:** {metadata.get('n_features', 'N/A')}")
        st.markdown(f"**Source:** {metadata.get('data_source', 'World Bank')}")
    
    st.markdown("---")
    
    st.markdown("### 🔗 Resources")
    st.markdown("[World Bank Data](https://data.worldbank.org)")
    st.markdown("[WHO GHO](https://www.who.int/data/gho)")
    
    st.markdown("---")
    st.caption("Version 1.0")


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
