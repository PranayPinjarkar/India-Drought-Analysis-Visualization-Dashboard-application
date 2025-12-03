import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Set Page Config
st.set_page_config(page_title="India Drought Analysis", page_icon="🌍", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stSidebar {
        background-color: #2c3e50;
        color: white;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Loading Functions ---
@st.cache_data
def load_data():
    base_dir = "e:/DS-Naresh IT/Projects/dhrought"
    
    # Climate Data
    chirps_df = pd.read_excel(os.path.join(base_dir, "climate_data/chirps_rainfall_timeseries.xlsx"))
    chirps_df['date'] = pd.to_datetime(chirps_df['date'])
    chirps_df['year'] = chirps_df['date'].dt.year
    
    bundelkhand_spei = pd.read_excel(os.path.join(base_dir, "climate_data/bundelkhand_spei.xlsx"))
    bundelkhand_spei['date'] = pd.to_datetime(bundelkhand_spei['date'])
    
    marathwada_spei = pd.read_excel(os.path.join(base_dir, "climate_data/marathwada_spei.xlsx"))
    marathwada_spei['date'] = pd.to_datetime(marathwada_spei['dates'])
    
    ndvi_df = pd.read_excel(os.path.join(base_dir, "climate_data/ndvi_1998_2013.xlsx"))
    ndvi_df['date'] = pd.to_datetime(ndvi_df['date'])
    
    # Groundwater Data
    gldas_recent = pd.read_csv(os.path.join(base_dir, "groundwater_data/gldas_2018_2023.csv"))
    gldas_old = pd.read_excel(os.path.join(base_dir, "groundwater_data/gldas_2000_2002.xlsx"))
    gldas_recent['date'] = pd.to_datetime(gldas_recent['date'])
    gldas_old['date'] = pd.to_datetime(gldas_old['date'])
    gldas_combined = pd.concat([gldas_old, gldas_recent], ignore_index=True)
    gldas_combined['year'] = gldas_combined['date'].dt.year
    
    # Agricultural Data
    agri_df = pd.read_csv(os.path.join(base_dir, "agricultural_data/icrisat_district_data.csv"))
    
    return chirps_df, bundelkhand_spei, marathwada_spei, ndvi_df, gldas_combined, agri_df

try:
    chirps_df, bundelkhand_spei, marathwada_spei, ndvi_df, gldas_combined, agri_df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- Sidebar ---
st.sidebar.title("🌍 Drought Analysis")
page = st.sidebar.radio("Navigate", ["Home", "Rainfall Analysis", "Drought Index (SPEI)", "Groundwater Trends", "Agricultural Impact"])

st.sidebar.markdown("---")
st.sidebar.info("Data Sources: ICRISAT, CHIRPS, GLDAS, MODIS")

# --- Home Page ---
if page == "Home":
    st.title("🌍 India Drought Analysis Dashboard")
    st.markdown("### Focus Regions: Bundelkhand & Marathwada")
    
    st.markdown("""
    This dashboard provides a comprehensive analysis of drought trends using multi-source data:
    - **Climate**: Rainfall (CHIRPS), Drought Index (SPEI), Vegetation Health (NDVI).
    - **Groundwater**: Soil Moisture and Groundwater anomalies (GLDAS).
    - **Agriculture**: Crop production and yield statistics (ICRISAT).
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>Regions Analyzed</h3><h2>2</h2><p>Bundelkhand & Marathwada</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>Data Sources</h3><h2>3+</h2><p>Climate, GW, Agri</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>Years Covered</h3><h2>~50</h2><p>1966 - 2023</p></div>', unsafe_allow_html=True)

# --- Rainfall Analysis ---
elif page == "Rainfall Analysis":
    st.title("🌧️ Rainfall Trends (CHIRPS)")
    
    region_filter = st.sidebar.selectbox("Select Region", chirps_df['region'].unique())
    filtered_chirps = chirps_df[chirps_df['region'] == region_filter]
    
    # Annual Rainfall
    annual_rain = filtered_chirps.groupby('year')['precipitation'].sum().reset_index()
    
    fig_annual = px.line(annual_rain, x='year', y='precipitation', markers=True, 
                         title=f"Annual Rainfall Trend in {region_filter}",
                         labels={'precipitation': 'Total Rainfall (mm)'})
    st.plotly_chart(fig_annual, use_container_width=True)
    
    # Monthly Distribution
    filtered_chirps['month'] = filtered_chirps['date'].dt.month_name()
    fig_monthly = px.box(filtered_chirps, x='month', y='precipitation', 
                         title=f"Monthly Rainfall Distribution in {region_filter}",
                         category_orders={"month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]})
    st.plotly_chart(fig_monthly, use_container_width=True)

# --- Drought Index (SPEI) ---
elif page == "Drought Index (SPEI)":
    st.title("🔥 Drought Index (SPEI)")
    st.markdown("Standardized Precipitation Evapotranspiration Index (SPEI). **Values < -1 indicate drought.**")
    
    region_spei = st.sidebar.selectbox("Select Region", ["Bundelkhand", "Marathwada"])
    
    if region_spei == "Bundelkhand":
        df_spei = bundelkhand_spei
    else:
        df_spei = marathwada_spei
        
    fig_spei = px.line(df_spei, x='date', y='spei', title=f"{region_spei} SPEI Trends")
    fig_spei.add_hline(y=-1, line_dash="dash", line_color="red", annotation_text="Drought Threshold (-1)")
    fig_spei.update_traces(line_color='orange' if region_spei == "Bundelkhand" else 'green')
    
    st.plotly_chart(fig_spei, use_container_width=True)
    
    # Highlight Drought Years
    drought_years = df_spei[df_spei['spei'] < -1]
    st.subheader("Severe Drought Events")
    st.dataframe(drought_years.sort_values('spei').head(10).style.format({"spei": "{:.2f}"}))

# --- Groundwater Trends ---
elif page == "Groundwater Trends":
    st.title("💧 Groundwater & Soil Moisture (GLDAS)")
    
    districts = gldas_combined['ADM2_NAME'].unique()
    selected_districts = st.multiselect("Select Districts", districts, default=['Latur', 'Jhansi'])
    
    if selected_districts:
        subset_gw = gldas_combined[gldas_combined['ADM2_NAME'].isin(selected_districts)]
        
        # Aggregate by year for smoother trend
        annual_gw = subset_gw.groupby(['ADM2_NAME', 'year'])['mean'].mean().reset_index()
        
        fig_gw = px.line(annual_gw, x='year', y='mean', color='ADM2_NAME', markers=True,
                         title="Annual Mean Groundwater/Soil Moisture Levels",
                         labels={'mean': 'Mean Level'})
        st.plotly_chart(fig_gw, use_container_width=True)
    else:
        st.warning("Please select at least one district.")

# --- Agricultural Impact ---
elif page == "Agricultural Impact":
    st.title("🌾 Agricultural Impact Analysis")
    
    districts = agri_df['Dist Name'].unique()
    selected_district = st.selectbox("Select District", districts, index=0)
    
    # Filter columns that look like yield or production
    yield_cols = [c for c in agri_df.columns if 'YIELD' in c]
    selected_crop_metric = st.selectbox("Select Crop Metric", yield_cols)
    
    district_agri = agri_df[agri_df['Dist Name'] == selected_district]
    
    fig_agri = px.line(district_agri, x='Year', y=selected_crop_metric, markers=True,
                       title=f"{selected_crop_metric} in {selected_district}")
    st.plotly_chart(fig_agri, use_container_width=True)
    
    st.markdown("### Correlation with Climate")
    st.info("To see direct correlation, compare the crop yield dips with the Drought Index (SPEI) years identified in the previous tab.")

