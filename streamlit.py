import streamlit as st
import pandas as pd
import re
from collections import Counter

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Sentencias Ambientales",
    page_icon="⚖️",
    layout="wide"
)

# Título principal
st.title("⚖️ Análisis de Sentencias Ambientales")
st.markdown("---")

# Cargar datos
@st.cache_data
def load_data():
    # Reemplaza con la ruta correcta de tu archivo
    return pd.read_csv("sentencias_ambientales_data.csv")

try:
    df = load_data()
except:
    st.error("No se pudo cargar el archivo CSV. Asegúrate de que esté en la misma carpeta que este script.")
    st.stop()

# Sidebar para filtros
st.sidebar.header("🔍 Filtros de Búsqueda")

# Función para extraer términos únicos
@st.cache_data
def extract_terms(descriptores_series):
    all_terms = []
    for desc in descriptores_series:
        if isinstance(desc, str):
            terms = [t.strip() for t in desc.split(",")]
            all_terms.extend(terms)
    
    # Calcular frecuencia
    term_freq = Counter(all_terms)
    return term_freq

# Extraer términos y frecuencias
term_freq = extract_terms(df["Descriptores"])

# Filtro por término en descriptores
st.sidebar.subheader("Buscar por término específico")
search_term = st.sidebar.text_input("Ingresa un término para buscar en Descriptores:")

# Filtro por materia
st.sidebar.subheader("Filtrar por Materia")
materias = ["Todas"] + sorted(df["Materia"].unique().tolist())
selected_materia = st.sidebar.selectbox("Selecciona una materia:", materias)

# Filtro por tipo de recurso
st.sidebar.subheader("Filtrar por Tipo de Recurso")
tipos_recurso = ["Todos"] + sorted(df["Tipo recurso"].unique().tolist())
selected_tipo = st.sidebar.selectbox("Selecciona tipo de recurso:", tipos_recurso)

# Filtro por resultado
st.sidebar.subheader("Filtrar por Resultado")
resultados = ["Todos"] + sorted(df["Resultado Recurso"].unique().tolist())
selected_resultado = st.sidebar.selectbox("Selecciona resultado:", resultados)

# Aplicar filtros
filtered_df = df.copy()

if selected_materia != "Todas":
    filtered_df = filtered_df[filtered_df["Materia"] == selected_materia]

if selected_tipo != "Todos":
    filtered_df = filtered_df[filtered_df["Tipo recurso"] == selected_tipo]

if selected_resultado != "Todos":
    filtered_df = filtered_df[filtered_df["Resultado Recurso"] == selected_resultado]

if search_term:
    filtered_df = filtered_df[filtered_df["Descriptores"].str.contains(search_term, case=False, na=False)]

# Mostrar estadísticas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Sentencias", len(df))
with col2:
    st.metric("Sentencias Filtradas", len(filtered_df))
with col3:
    st.metric("Materias Únicas", df["Materia"].nunique())
with col4:
    st.metric("Tipos de Recurso", df["Tipo recurso"].nunique())

st.markdown("---")

# Pestañas para diferentes vistas
tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen General", "🔍 Términos Más Frecuentes", "📋 Sentencias Filtradas", "📈 Análisis por Año"])

with tab1:
    st.subheader("Resumen General de los Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Materias más comunes:**")
        materia_counts = df["Materia"].value_counts().head(10)
        st.bar_chart(materia_counts)
    
    with col2:
        st.write("**Resultados más frecuentes:**")
        resultado_counts = df["Resultado Recurso"].value_counts().head(10)
        st.bar_chart(resultado_counts)
    
    # Vista previa de los datos
    st.subheader("Vista Previa de los Datos")
    st.dataframe(filtered_df.head(10), use_container_width=True)

with tab2:
    st.subheader("Términos Más Frecuentes en Descriptores")
    
    # Mostrar top términos
    num_terms = st.slider("Número de términos a mostrar:", 10, 50, 20)
    
    top_terms = dict(term_freq.most_common(num_terms))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top términos por frecuencia:**")
        for term, freq in list(top_terms.items())[:num_terms//2]:
            st.write(f"`{term}`: **{freq}** ocurrencias")
    
    with col2:
        st.write("**Continuación:**")
        for term, freq in list(top_terms.items())[num_terms//2:]:
            st.write(f"`{term}`: **{freq}** ocurrencias")
    
    # Gráfico de términos más frecuentes
    st.subheader("Distribución de Términos Más Frecuentes")
    terms_df = pd.DataFrame(list(top_terms.items()), columns=['Término', 'Frecuencia'])
    st.bar_chart(terms_df.set_index('Término').head(15))

with tab3:
    st.subheader("Sentencias Filtradas")
    
    if len(filtered_df) == 0:
        st.warning("No hay sentencias que coincidan con los filtros seleccionados.")
    else:
        st.write(f"**Mostrando {len(filtered_df)} sentencias:**")
        
        # Selector de columnas a mostrar
        columnas = st.multiselect(
            "Selecciona las columnas a mostrar:",
            options=filtered_df.columns.tolist(),
            default=["Rol", "Caratulado", "Materia", "Resultado Recurso", "Tipo recurso"]
        )
        
        # Mostrar datos filtrados
        st.dataframe(
            filtered_df[columnas], 
            use_container_width=True,
            height=400
        )
        
        # Botón para descargar resultados filtrados
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Descargar resultados filtrados (CSV)",
            data=csv,
            file_name="sentencias_filtradas.csv",
            mime="text/csv"
        )

with tab4:
    st.subheader("Análisis Temporal")
    
    # Extraer año de la fecha (asumiendo formato DD-MM-YYYY)
    try:
        df['Año'] = pd.to_datetime(df['Fecha Sentencia'], format='%d-%m-%Y').dt.year
        yearly_counts = df['Año'].value_counts().sort_index()
        
        st.write("**Sentencias por año:**")
        st.line_chart(yearly_counts)
        
        # Estadísticas por año
        st.write("**Distribución por año:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(yearly_counts)
        
        with col2:
            st.metric("Año con más sentencias", yearly_counts.idxmax())
            st.metric("Máximo de sentencias en un año", yearly_counts.max())
    
    except:
        st.warning("No se pudo analizar la distribución temporal. Revisa el formato de las fechas.")

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Información")
st.sidebar.info("""
Esta aplicación permite explorar y filtrar sentencias ambientales 
de la Corte Suprema de Chile. Usa los filtros para refinar tu búsqueda.
""")

# Pie de página
st.markdown("---")
st.caption("Desarrollado con Streamlit | Análisis de sentencias ambientales")
