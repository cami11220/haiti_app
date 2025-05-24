import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Haiti Data Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and prepare data
@st.cache_data
def load_data():
    """Load and prepare the data"""
    try:
        # Load the main dataset
        data_op_pres = pd.read_stata("data_op_pres.dta")
        
        # Convert date column to datetime if it exists
        if 'date' in data_op_pres.columns:
            data_op_pres['date'] = pd.to_datetime(data_op_pres['date'], errors='coerce')
        
        return data_op_pres
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Helper functions for filtering
def filter_data(data, sector=None, department=None, org_type=None, date_range=None):
    """Filter data based on selected criteria"""
    filtered_data = data.copy()
    
    if sector and sector != "All":
        filtered_data = filtered_data[filtered_data['Secteur'] == sector]
    
    if department and department != "All":
        filtered_data = filtered_data[filtered_data['adm1code'] == department]
    
    if org_type and org_type != "All":
        filtered_data = filtered_data[filtered_data['Typedorganisation'] == org_type]
    
    if date_range and len(date_range) == 2:
        filtered_data = filtered_data[
            (filtered_data['date'] >= pd.to_datetime(date_range[0])) &
            (filtered_data['date'] <= pd.to_datetime(date_range[1]))
        ]
    
    return filtered_data

def create_bar_chart(data, group_by, title, x_label, y_label):
    """Create a bar chart with grouped data"""
    if data.empty:
        st.warning("No data available for the selected filters.")
        return
    
    grouped_data = data.groupby(group_by).size().reset_index(name='count')
    
    fig = px.bar(
        grouped_data,
        x=group_by,
        y='count',
        title=title,
        labels={group_by: x_label, 'count': y_label},
        color='count',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_pie_chart(data, group_by, title):
    """Create a pie chart with grouped data"""
    if data.empty:
        st.warning("No data available for the selected filters.")
        return
    
    grouped_data = data.groupby(group_by).size().reset_index(name='count')
    
    fig = px.pie(
        grouped_data,
        values='count',
        names=group_by,
        title=title
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_time_series(data, date_col, title):
    """Create a time series chart"""
    if data.empty or data[date_col].isna().all():
        st.warning("No date data available for the selected filters.")
        return
    
    # Group by date and count
    time_data = data.groupby(data[date_col].dt.date).size().reset_index(name='count')
    
    fig = px.line(
        time_data,
        x=date_col,
        y='count',
        title=title,
        markers=True
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Main app
def main():
    # Load data
    data = load_data()
    
    if data is None:
        st.error("Unable to load data. Please check if the data file exists.")
        return
    
    # Title
    st.title("🇭🇹 Haiti Data Dashboard")
    st.markdown("Dashboard para análisis de datos de operaciones y presencia en Haití")
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.title("📊 Filtros")
    
    # Get unique values for filters
    sectors = ["All"] + sorted(data['Secteur'].dropna().unique().tolist()) if 'Secteur' in data.columns else ["All"]
    departments = ["All"] + sorted(data['adm1code'].dropna().unique().tolist()) if 'adm1code' in data.columns else ["All"]
    org_types = ["All"] + sorted(data['Typedorganisation'].dropna().unique().tolist()) if 'Typedorganisation' in data.columns else ["All"]
    
    # Filter controls
    sector_filter = st.sidebar.selectbox("Sector", sectors)
    department_filter = st.sidebar.selectbox("Departamento", departments)
    org_type_filter = st.sidebar.selectbox("Tipo de Organización", org_types)
    
    # Date range filter
    if 'date' in data.columns and not data['date'].isna().all():
        min_date = data['date'].min().date()
        max_date = data['date'].max().date()
        
        date_range = st.sidebar.date_input(
            "Rango de Fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    else:
        date_range = None
    
    # Apply filters
    filtered_data = filter_data(
        data, 
        sector=sector_filter,
        department=department_filter,
        org_type=org_type_filter,
        date_range=date_range
    )
    
    # Display summary statistics
    st.header("📈 Resumen General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Registros", len(filtered_data))
    
    with col2:
        unique_sectors = filtered_data['Secteur'].nunique() if 'Secteur' in filtered_data.columns else 0
        st.metric("Sectores Únicos", unique_sectors)
    
    with col3:
        unique_departments = filtered_data['adm1code'].nunique() if 'adm1code' in filtered_data.columns else 0
        st.metric("Departamentos", unique_departments)
    
    with col4:
        unique_orgs = filtered_data['Typedorganisation'].nunique() if 'Typedorganisation' in filtered_data.columns else 0
        st.metric("Tipos de Org.", unique_orgs)
    
    st.markdown("---")
    
    # Charts section
    st.header("📊 Visualizaciones")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Secteur' in filtered_data.columns:
            create_bar_chart(
                filtered_data, 
                'Secteur', 
                "Distribución por Sector",
                "Sector",
                "Cantidad"
            )
        
        if 'Typedorganisation' in filtered_data.columns:
            create_pie_chart(
                filtered_data,
                'Typedorganisation',
                "Distribución por Tipo de Organización"
            )
    
    with col2:
        if 'adm1code' in filtered_data.columns:
            create_bar_chart(
                filtered_data,
                'adm1code',
                "Distribución por Departamento",
                "Departamento",
                "Cantidad"
            )
        
        if 'date' in filtered_data.columns:
            create_time_series(
                filtered_data,
                'date',
                "Tendencia Temporal"
            )
    
    # Data table section
    st.markdown("---")
    st.header("📋 Vista de Datos")
    
    # Show data preview
    if st.checkbox("Mostrar datos filtrados"):
        st.dataframe(filtered_data, use_container_width=True)
    
    # Download filtered data
    if st.button("💾 Descargar datos filtrados (CSV)"):
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Descargar CSV",
            data=csv,
            file_name=f"haiti_data_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
