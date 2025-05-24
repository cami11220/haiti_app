import streamlit as st
import pandas as pd
import geopandas as gpd

# Page setup
st.set_page_config(page_title="Haiti Data Dashboard", layout="wide")
st.title("Haiti Operations Dashboard - Test Version")

# Load data
@st.cache_data
def load_data():
    try:
        st.write("Cargando datos...")
        df = pd.read_csv("https://raw.githubusercontent.com/cami11220/haiti_app/main/data_op_pres.csv", parse_dates=["date"])
        st.write(f"✅ DataFrame cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        gdf = gpd.read_file("https://raw.githubusercontent.com/cami11220/haiti_app/main/communes_haiti.shp")
        st.write(f"✅ GeoDataFrame cargado: {gdf.shape[0]} filas, {gdf.shape[1]} columnas")
        
        gdf = gdf.merge(df, how='left', left_on='ADM2_PCODE', right_on='adm2code')
        st.write(f"✅ Merge completado: {gdf.shape[0]} filas, {gdf.shape[1]} columnas")
        
        return df, gdf
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None, None

# Load data
df, gdf = load_data()

if df is not None and gdf is not None:
    st.header("📊 Datos Cargados Exitosamente")
    
    # Mostrar info básica
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 DataFrame (CSV):")
        st.write(f"**Shape:** {df.shape}")
        st.write("**Primeras 5 filas:**")
        st.dataframe(df.head())
        
        st.write("**Columnas:**")
        st.write(df.columns.tolist())
    
    with col2:
        st.subheader("🗺️ GeoDataFrame (Shapefile + merge):")
        st.write(f"**Shape:** {gdf.shape}")
        st.write("**Primeras 5 filas:**")
        st.dataframe(gdf.head())
        
        st.write("**Columnas:**")
        st.write(gdf.columns.tolist())
    
    # Información adicional
    st.header("📈 Información Adicional")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("Sectores únicos:")
        if 'Secteur' in df.columns:
            sectores = df['Secteur'].dropna().unique()
            st.write(f"Total: {len(sectores)}")
            st.write(sectores.tolist())
        else:
            st.write("Columna 'Secteur' no encontrada")
    
    with col4:
        st.subheader("Departamentos únicos:")
        if 'adm1code' in df.columns:
            deptos = df['adm1code'].dropna().unique()
            st.write(f"Total: {len(deptos)}")
            st.write(deptos.tolist())
        else:
            st.write("Columna 'adm1code' no encontrada")
    
    # Test de geometrías
    st.header("🔍 Test de Geometrías")
    if 'geometry' in gdf.columns:
        st.write(f"**Geometrías válidas:** {gdf.geometry.notna().sum()}")
        st.write(f"**Geometrías nulas:** {gdf.geometry.isna().sum()}")
        st.write(f"**Tipo de geometría:** {gdf.geometry.geom_type.iloc[0] if not gdf.empty else 'N/A'}")
    else:
        st.write("Columna 'geometry' no encontrada")

else:
    st.error("❌ No se pudieron cargar los datos. Revisa las URLs o la conexión.")
    st.write("Verifica que estos enlaces funcionen:")
    st.write("- https://raw.githubusercontent.com/cami11220/haiti_app/main/data_op_pres.csv")
    st.write("- https://raw.githubusercontent.com/cami11220/haiti_app/main/communes_haiti.shp")
