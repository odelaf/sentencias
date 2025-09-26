import streamlit as st
import pandas as pd
import numpy as np
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
    # Aquí debes cargar tu CSV
    # Reemplaza con la ruta correcta
    df = pd.read_csv("sentencias_ambientales_data.csv")
    
    # Limpiar datos - manejar valores NaN
    df = df.fillna('')
    
    return df

try:
    df = load_data()
    st.success(f"✅ Datos cargados correctamente. {len(df)} registros encontrados.")
except Exception as e:
    st.error(f"❌ Error al cargar los datos: {e}")
    st.stop()

# Función para limpiar y extraer términos
@st.cache_data
def extract_terms(descriptores_series):
    all_terms = []
    for desc in descriptores_series:
        if isinstance(desc, str) and desc.strip():
            terms = [t.strip() for t in desc.split(",") if t.strip()]
            all_terms.extend(terms)
    
    term_freq = Counter(all_terms)
    return term_freq

# Sidebar para filtros
st.sidebar.header("🔍 Filtros de Búsqueda")

# Función para obtener opciones únicas manejando NaN
def get_unique_options(column):
    unique_vals = df[column].unique()
    # Filtrar valores vacíos y NaN
    clean_vals = [str(x) for x in unique_vals if pd.notna(x) and str(x).strip()]
    return ["Todos"] + sorted([x for x in clean_vals if x])

# Filtro por término en descriptores
st.sidebar.subheader("Buscar por término específico")
search_term = st.sidebar.text_input("Ingresa un término para buscar en Descriptores:")

# Filtros con manejo de valores NaN
st.sidebar.subheader("Filtrar por Materia")
materias = get_unique_options("Materia")
selected_materia = st.sidebar.selectbox("Selecciona una materia:", materias)

st.sidebar.subheader("Filtrar por Tipo de Recurso")
tipos_recurso = get_unique_options("Tipo recurso")
selected_tipo = st.sidebar.selectbox("Selecciona tipo de recurso:", tipos_recurso)

st.sidebar.subheader("Filtrar por Resultado")
resultados = get_unique_options("Resultado Recurso")
selected_resultado = st.sidebar.selectbox("Selecciona resultado:", resultados)

# Aplicar filtros
filtered_df = df.copy()

if selected_materia != "Todos":
    filtered_df = filtered_df[filtered_df["Materia"] == selected_materia]

if selected_tipo != "Todos":
    filtered_df = filtered_df[filtered_df["Tipo recurso"] == selected_tipo]

if selected_resultado != "Todos":
    filtered_df = filtered_df[filtered_df["Resultado Recurso"] == selected_resultado]

if search_term:
    filtered_df = filtered_df[
        filtered_df["Descriptores"].astype(str).str.contains(
            search_term, case=False, na=False
        )
    ]

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

# Pestañas principales
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Resumen General", 
    "🔍 Términos Más Frecuentes", 
    "📋 Sentencias Filtradas", 
    "🔎 Búsqueda Avanzada"
])

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
    
    # Vista previa de datos
    st.subheader("Vista Previa de los Datos")
    st.dataframe(
        filtered_df.head(10)[["Rol", "Caratulado", "Materia", "Resultado Recurso", "Tipo recurso"]],
        use_container_width=True
    )

with tab2:
    st.subheader("Términos Más Frecuentes en Descriptores")
    
    # Extraer términos
    term_freq = extract_terms(df["Descriptores"])
    
    num_terms = st.slider("Número de términos a mostrar:", 10, 50, 20)
    
    top_terms = dict(term_freq.most_common(num_terms))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top términos por frecuencia:**")
        for i, (term, freq) in enumerate(list(top_terms.items())[:num_terms//2]):
            st.write(f"{i+1}. **{term}**: {freq} ocurrencias")
    
    with col2:
        st.write("**Continuación:**")
        for i, (term, freq) in enumerate(list(top_terms.items())[num_terms//2:], start=num_terms//2 + 1):
            st.write(f"{i}. **{term}**: {freq} ocurrencias")
    
    # Gráfico de términos
    if top_terms:
        st.subheader("Distribución de Términos Más Frecuentes")
        terms_df = pd.DataFrame(list(top_terms.items())[:15], columns=['Término', 'Frecuencia'])
        st.bar_chart(terms_df.set_index('Término'))

with tab3:
    st.subheader("Sentencias Filtradas")
    
    if len(filtered_df) == 0:
        st.warning("No hay sentencias que coincidan con los filtros seleccionados.")
    else:
        st.success(f"Se encontraron {len(filtered_df)} sentencias que coinciden con los filtros.")
        
        # Selector de columnas
        available_columns = filtered_df.columns.tolist()
        default_cols = ["Rol", "Caratulado", "Materia", "Resultado Recurso", "Tipo recurso"]
        
        selected_columns = st.multiselect(
            "Selecciona las columnas a mostrar:",
            options=available_columns,
            default=default_cols
        )
        
        if selected_columns:
            # Mostrar datos filtrados
            st.dataframe(
                filtered_df[selected_columns], 
                use_container_width=True,
                height=400
            )
            
            # Botón de descarga
            csv_data = filtered_df[selected_columns].to_csv(index=False)
            st.download_button(
                label="📥 Descargar resultados filtrados (CSV)",
                data=csv_data,
                file_name="sentencias_filtradas.csv",
                mime="text/csv"
            )
        else:
            st.warning("Por favor selecciona al menos una columna para mostrar.")

with tab4:
    st.subheader("Búsqueda Avanzada por Términos")
    
    st.info("Busca sentencias que contengan términos específicos en los descriptores")
    
    # Búsqueda múltiple
    search_terms = st.text_area(
        "Ingresa términos a buscar (uno por línea):",
        placeholder="Ejemplo:\nDaño ambiental\nParticipación ciudadana\nSistema de Evaluación de Impacto Ambiental"
    )
    
    if search_terms:
        terms_list = [term.strip() for term in search_terms.split('\n') if term.strip()]
        
        if terms_list:
            st.write(f"**Buscando términos:** {', '.join(terms_list)}")
            
            # Filtrar por múltiples términos
            advanced_filtered = df.copy()
            for term in terms_list:
                advanced_filtered = advanced_filtered[
                    advanced_filtered["Descriptores"].astype(str).str.contains(
                        term, case=False, na=False
                    )
                ]
            
            st.write(f"**Resultados encontrados:** {len(advanced_filtered)} sentencias")
            
            if len(advanced_filtered) > 0:
                st.dataframe(
                    advanced_filtered[["Rol", "Caratulado", "Materia", "Descriptores"]],
                    use_container_width=True
                )

# Información adicional
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Instrucciones")
st.sidebar.info("""
1. Usa los filtros para refinar tu búsqueda
2. Explora las diferentes pestañas para distintos tipos de análisis
3. Descarga los resultados filtrados en CSV
""")

# Pie de página
st.markdown("---")
st.caption("📊 Aplicación de análisis de sentencias ambientales | Desarrollado con Streamlit")
