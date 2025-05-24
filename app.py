import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/cami11220/haiti_app/main/data_op_pres.csv", parse_dates=["date"])
    gdf = gpd.read_file("https://raw.githubusercontent.com/cami11220/haiti_app/main/communes_haiti.shp")
    gdf = gdf.merge(df, how='left', left_on='ADM2_PCODE', right_on='adm2code')
    return df, gdf

df, gdf = load_data()

# Page setup
st.set_page_config(page_title="Haiti Data Dashboard", layout="wide")
st.title("Haiti Operations Dashboard")

# Sidebar
page = st.sidebar.selectbox("Choose a page", ["Basic Statistics", "Map View (coming soon)"])

if page == "Basic Statistics":
    st.header("Basic Statistics Viewer")

    # First chart - Sector and Time filter
    st.subheader("1. Operations by Department (Filtered by Sector and Date)")

    sector = st.selectbox("Select a sector", options=sorted(df['Secteur'].dropna().unique()))
    date_range_1 = st.date_input("Select date range (optional)", [], key="date1")

    df_filtered = df[df['Secteur'] == sector]
    if date_range_1 and len(date_range_1) == 2:
        df_filtered = df_filtered[(df_filtered['date'] >= pd.to_datetime(date_range_1[0])) &
                                  (df_filtered['date'] <= pd.to_datetime(date_range_1[1]))]

    chart1 = df_filtered.groupby('adm1code').size().reset_index(name='count')
    fig1 = px.bar(chart1, x='adm1code', y='count', labels={'adm1code': 'Department', 'count': 'Number of Records'})
    st.plotly_chart(fig1, use_container_width=True)

    # Second chart - Type of Organization and Time filter
    st.subheader("2. Operations by Department (Filtered by Type of Organization and Date)")

    org_type = st.selectbox("Select a type of organization", options=sorted(df['Typedorganisation'].dropna().unique()))
    date_range_2 = st.date_input("Select date range (optional)", [], key="date2")

    df_filtered_org = df[df['Typedorganisation'] == org_type]
    if date_range_2 and len(date_range_2) == 2:
        df_filtered_org = df_filtered_org[(df_filtered_org['date'] >= pd.to_datetime(date_range_2[0])) &
                                          (df_filtered_org['date'] <= pd.to_datetime(date_range_2[1]))]

    chart2 = df_filtered_org.groupby('adm1code').size().reset_index(name='count')
    fig2 = px.bar(chart2, x='adm1code', y='count', labels={'adm1code': 'Department', 'count': 'Number of Records'})
    st.plotly_chart(fig2, use_container_width=True)

    # Third chart - Department and Time filter
    st.subheader("3. Sector Breakdown in Selected Department")

    dept = st.selectbox("Select a department", options=sorted(df['adm1code'].dropna().unique()))
    date_range_3 = st.date_input("Select date range", [], key="date3")

    df_filtered_dept = df[df['adm1code'] == dept]
    if date_range_3 and len(date_range_3) == 2:
        df_filtered_dept = df_filtered_dept[(df_filtered_dept['date'] >= pd.to_datetime(date_range_3[0])) &
                                            (df_filtered_dept['date'] <= pd.to_datetime(date_range_3[1]))]

    chart3 = df_filtered_dept.groupby('Secteur').size().reset_index(name='count')
    fig3 = px.bar(chart3, x='Secteur', y='count', labels={'Secteur': 'Sector', 'count': 'Number of Records'})
    st.plotly_chart(fig3, use_container_width=True)
