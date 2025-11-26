"""
Policy Simulator Page
=====================

Interactive what-if analysis for policy interventions.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pickle

st.set_page_config(page_title="Policy Simulator", page_icon="🔮", layout="wide")

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
def load_coefficients():
    try:
        return pd.read_csv('data/regression_coefficients.csv')
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
# PREDICTION FUNCTION
# ============================================================================

def predict_mortality_change(df, coefficients, variable, percent_change, countries=None):
    """
    Estimate mortality change based on regression coefficients.
    This is a simplified linear approximation.
    """
    # Get coefficient for the variable from the full model
    full_model_coefs = coefficients[coefficients['Model'].str.contains('Full')].copy()
    
    if variable not in full_model_coefs['Variable'].values:
        return None
    
    coef = full_model_coefs[full_model_coefs['Variable'] == variable]['Coefficient'].values[0]
    
    # Calculate expected change
    if countries is None:
        countries_df = df
    else:
        countries_df = df[df['country'].isin(countries)]
    
    results = []
    for _, row in countries_df.iterrows():
        current_value = row.get(variable, np.nan)
        
        if pd.notna(current_value):
            # Calculate the change in the predictor
            new_value = current_value * (1 + percent_change / 100)
            
            # Cap at 100 for percentage variables
            if any(x in variable.lower() for x in ['literacy', 'water', 'sanitation', 'immunisation', 'access']):
                new_value = min(new_value, 100)
            
            value_change = new_value - current_value
            
            # Estimate mortality change (linear approximation)
            mortality_change = coef * value_change
            
            results.append({
                'country': row.get('country', 'Unknown'),
                'region': row.get('region', 'Unknown'),
                'current_value': current_value,
                'new_value': new_value,
                'current_mortality': row.get('crude_death_rate', np.nan),
                'mortality_change': mortality_change,
                'predicted_mortality': row.get('crude_death_rate', np.nan) + mortality_change
            })
    
    return pd.DataFrame(results)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("🔮 Policy Simulator")
st.markdown("Explore hypothetical policy interventions and their predicted impact on mortality")

# Warning box
st.warning("""
⚠️ **Important Limitations:**

1. These are **model predictions**, not guaranteed outcomes
2. Based on **ecological (country-level)** relationships
3. Assumes **linear relationships** and **no interaction effects**
4. Real-world implementation may produce different results
5. **Correlation does not imply causation**

Use these simulations for educational exploration, not policy decisions.
""")

df = load_data()
coefficients = load_coefficients()
var_dicts = load_var_dicts()

if df is None or coefficients is None:
    st.error("Data or model results not found. Please run the analysis first.")
    st.stop()

# ============================================================================
# SINGLE INTERVENTION SIMULATOR
# ============================================================================

st.markdown("---")
st.markdown("## 🎚️ Single Intervention Simulator")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Configure Intervention")
    
    # Get modifiable variables (those with coefficients)
    full_model_coefs = coefficients[coefficients['Model'].str.contains('Full')]
    modifiable_vars = full_model_coefs[full_model_coefs['Variable'] != 'const']['Variable'].tolist()
    modifiable_vars = [v for v in modifiable_vars if v in df.columns]
    
    # Group by type
    if var_dicts:
        distal = list(var_dicts.get('distal_vars', {}).values())
        intermediate = list(var_dicts.get('intermediate_vars', {}).values())
        proximate = list(var_dicts.get('proximate_vars', {}).values())
    else:
        distal = intermediate = proximate = []
    
    # Variable selector with grouping
    selected_var = st.selectbox(
        "Select intervention variable",
        modifiable_vars,
        format_func=lambda x: f"{'🎯 ' if x in distal else '⚙️ ' if x in intermediate else '🔬 '}{x.replace('_', ' ').title()}"
    )
    
    # Get coefficient info
    var_coef = full_model_coefs[full_model_coefs['Variable'] == selected_var]['Coefficient'].values[0]
    var_pval = full_model_coefs[full_model_coefs['Variable'] == selected_var]['P_Value'].values[0]
    
    st.markdown(f"""
    <div class="scenario-box">
        <strong>Coefficient:</strong> {var_coef:.4f}<br>
        <strong>P-value:</strong> {var_pval:.4f} {'✅' if var_pval < 0.05 else '⚠️'}<br>
        <strong>Effect:</strong> {'Increases' if var_coef > 0 else 'Decreases'} mortality
    </div>
    """, unsafe_allow_html=True)
    
    # Intervention size
    intervention_pct = st.slider(
        "Intervention Size (%)",
        min_value=-50,
        max_value=100,
        value=20,
        step=5,
        help="Percentage change in the selected variable"
    )
    
    # Country filter
    apply_to = st.radio(
        "Apply to",
        ['All Countries', 'Selected Region', 'Selected Countries']
    )
    
    if apply_to == 'Selected Region' and 'region' in df.columns:
        selected_region = st.selectbox("Select region", df['region'].dropna().unique())
        target_countries = df[df['region'] == selected_region]['country'].tolist()
    elif apply_to == 'Selected Countries':
        target_countries = st.multiselect("Select countries", df['country'].dropna().unique())
    else:
        target_countries = None

with col2:
    st.markdown("### Predicted Impact")
    
    # Run simulation
    if st.button("🚀 Run Simulation", type="primary"):
        results = predict_mortality_change(
            df, coefficients, selected_var, intervention_pct, target_countries
        )
        
        if results is not None and len(results) > 0:
            # Store in session state
            st.session_state['simulation_results'] = results
            st.session_state['simulation_var'] = selected_var
            st.session_state['simulation_pct'] = intervention_pct
    
    # Display results
    if 'simulation_results' in st.session_state:
        results = st.session_state['simulation_results']
        var_name = st.session_state['simulation_var']
        pct_change = st.session_state['simulation_pct']
        
        # Summary metrics
        avg_change = results['mortality_change'].mean()
        total_countries = len(results)
        improved = (results['mortality_change'] < 0).sum()
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            direction = "reduction" if avg_change < 0 else "increase"
            st.markdown(f"""
            <div class="policy-card">
                <h2>{abs(avg_change):.3f}</h2>
                <p>Avg mortality {direction} per 1,000</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown(f"""
            <div class="policy-card" style="background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);">
                <h2>{improved}</h2>
                <p>Countries with lower mortality</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown(f"""
            <div class="policy-card" style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
                <h2>{total_countries}</h2>
                <p>Countries analysed</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Impact distribution
        st.markdown("#### 📊 Impact Distribution")
        
        fig_hist = px.histogram(
            results,
            x='mortality_change',
            nbins=30,
            color_discrete_sequence=['#667eea'],
            title=f'Distribution of Predicted Mortality Changes'
        )
        fig_hist.add_vline(x=0, line_dash='dash', line_color='red')
        fig_hist.update_layout(
            xaxis_title='Predicted Mortality Change (per 1,000)',
            yaxis_title='Number of Countries',
            height=350
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Top impacted countries
        st.markdown("#### 🏆 Most Impacted Countries")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Largest Improvements**")
            best = results.nsmallest(5, 'mortality_change')[['country', 'current_mortality', 'mortality_change', 'predicted_mortality']]
            best.columns = ['Country', 'Current', 'Change', 'Predicted']
            st.dataframe(best.style.format({'Current': '{:.2f}', 'Change': '{:.3f}', 'Predicted': '{:.2f}'}), 
                        use_container_width=True, hide_index=True)
        
        with col_b:
            st.markdown("**Smallest Improvements**")
            worst = results.nlargest(5, 'mortality_change')[['country', 'current_mortality', 'mortality_change', 'predicted_mortality']]
            worst.columns = ['Country', 'Current', 'Change', 'Predicted']
            st.dataframe(worst.style.format({'Current': '{:.2f}', 'Change': '{:.3f}', 'Predicted': '{:.2f}'}),
                        use_container_width=True, hide_index=True)

# ============================================================================
# POLICY COMPARISON
# ============================================================================

st.markdown("---")
st.markdown("## ⚖️ Compare Multiple Interventions")

st.markdown("""
Compare the predicted impact of different policy interventions side by side.
All interventions assume a **20% improvement** in each indicator.
""")

# Define standard scenarios
scenarios = {
    '📚 Education (+20% Literacy)': ('adult_literacy', 20),
    '💰 Economic (+20% GNI)': ('gni_per_capita', 20),
    '👨‍⚕️ Healthcare (+20% Physicians)': ('physicians_density', 20),
    '💧 Water (+20% Safe Water)': ('safe_water', 20),
    '🚿 Sanitation (+20% Sanitation)': ('basic_sanitation', 20),
    '💉 Immunisation (+20%)': ('measles_immunisation', 20)
}

# Filter to available variables
available_scenarios = {k: v for k, v in scenarios.items() if v[0] in modifiable_vars}

if st.button("📊 Compare All Interventions", type="primary"):
    comparison_results = []
    
    for scenario_name, (var, pct) in available_scenarios.items():
        results = predict_mortality_change(df, coefficients, var, pct, None)
        
        if results is not None and len(results) > 0:
            comparison_results.append({
                'Intervention': scenario_name,
                'Variable': var,
                'Avg Mortality Change': results['mortality_change'].mean(),
                'Countries Improved': (results['mortality_change'] < 0).sum(),
                'Max Improvement': results['mortality_change'].min(),
                'Countries Analysed': len(results)
            })
    
    if comparison_results:
        comparison_df = pd.DataFrame(comparison_results)
        comparison_df = comparison_df.sort_values('Avg Mortality Change')
        
        # Store for display
        st.session_state['comparison_df'] = comparison_df

if 'comparison_df' in st.session_state:
    comparison_df = st.session_state['comparison_df']
    
    # Bar chart
    fig_compare = px.bar(
        comparison_df,
        x='Intervention',
        y='Avg Mortality Change',
        color='Avg Mortality Change',
        color_continuous_scale='RdYlGn_r',
        title='Average Predicted Mortality Change by Intervention'
    )
    
    fig_compare.add_hline(y=0, line_dash='dash', line_color='black')
    fig_compare.update_layout(
        height=450,
        xaxis_tickangle=45,
        xaxis_title='',
        yaxis_title='Avg Mortality Change (per 1,000)',
        showlegend=False
    )
    
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # Detailed table
    st.markdown("### 📋 Detailed Comparison")
    st.dataframe(
        comparison_df.style.format({
            'Avg Mortality Change': '{:.4f}',
            'Max Improvement': '{:.4f}'
        }).background_gradient(subset=['Avg Mortality Change'], cmap='RdYlGn_r'),
        use_container_width=True,
        hide_index=True
    )
    
    # Best intervention
    best = comparison_df.iloc[0]
    st.success(f"""
    🏆 **Most Effective Intervention:** {best['Intervention']}
    
    Predicted to reduce mortality by an average of **{abs(best['Avg Mortality Change']):.4f}** deaths per 1,000 population.
    """)

# ============================================================================
# METHODOLOGY NOTE
# ============================================================================

st.markdown("---")

with st.expander("📖 Methodology & Limitations"):
    st.markdown("""
    ### How This Simulator Works
    
    1. **Regression Coefficients**: We use coefficients from the OLS regression model
    2. **Linear Approximation**: Impact = Coefficient × Change in Predictor
    3. **Ceteris Paribus**: Assumes other factors remain constant
    
    ### Key Limitations
    
    1. **Ecological Fallacy**: Country-level relationships may not apply to individuals
    2. **Linearity**: Real relationships are often non-linear
    3. **No Interaction Effects**: Interventions may have synergistic or competing effects
    4. **Temporal Dynamics**: Changes don't happen instantaneously
    5. **Implementation**: Real policies face barriers not captured in the model
    6. **Endogeneity**: Causation may run in both directions
    
    ### Appropriate Use
    
    ✅ Educational exploration of relationships  
    ✅ Generating hypotheses for further research  
    ✅ Understanding relative importance of factors  
    
    ❌ Making actual policy decisions  
    ❌ Predicting precise outcomes  
    ❌ Budget allocation without further analysis
    """)
