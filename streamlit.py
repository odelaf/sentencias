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
    
    # Mostrar información de las columnas para debugging
    st.sidebar.info(f"Columnas cargadas: {', '.join(df.columns.tolist())}")
    
    return df

try:
    df = load_data()
    st.success(f"✅ Datos cargados correctamente. {len(df)} registros encontrados.")
    
    # Mostrar información del dataset
    with st.expander("🔍 Ver información del dataset"):
        st.write("**Columnas disponibles:**")
        st.write(df.columns.tolist())
        st.write("**Primeras filas:**")
        st.dataframe(df.head(3))
        st.write("**Tipos de datos:**")
        st.write(df.dtypes)
        
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

# Función para obtener opciones únicas manejando NaN y columnas que puedan no existir
def get_unique_options(column_name, df):
    if column_name not in df.columns:
        st.warning(f"⚠️ Columna '{column_name}' no encontrada. Columnas disponibles: {list(df.columns)}")
        return ["Todos"]
    
    unique_vals = df[column_name].unique()
    # Filtrar valores vacíos y NaN
    clean_vals = [str(x) for x in unique_vals if pd.notna(x) and str(x).strip()]
    return ["Todos"] + sorted([x for x in clean_vals if x])

# Sidebar para filtros
st.sidebar.header("🔍 Filtros de Búsqueda")

# Mostrar columnas disponibles para debugging
st.sidebar.info(f"**Columnas cargadas:** {len(df.columns)}")

# Filtro por término en descriptores
st.sidebar.subheader("Buscar por término específico")
search_term = st.sidebar.text_input("Ingresa un término para buscar en Descriptores:")

# Filtros con manejo de columnas que puedan no existir
st.sidebar.subheader("Filtrar por Materia")
materias = get_unique_options("Materia", df)
selected_materia = st.sidebar.selectbox("Selecciona una materia:", materias)

# Intentar diferentes nombres posibles para la columna de tipo de recurso
tipo_recurso_column = None
possible_names = ["Tipo recurso", "Tipo Recurso", "Tipo_recurso", "TipoRecurso", "Tipo"]

for name in possible_names:
    if name in df.columns:
        tipo_recurso_column = name
        break

if tipo_recurso_column:
    st.sidebar.subheader("Filtrar por Tipo de Recurso")
    tipos_recurso = get_unique_options(tipo_recurso_column, df)
    selected_tipo = st.sidebar.selectbox("Selecciona tipo de recurso:", tipos_recurso)
else:
    st.sidebar.warning("Columna de tipo de recurso no encontrada")
    selected_tipo = "Todos"

# Intentar diferentes nombres para resultado
resultado_column = None
possible_result_names = ["Resultado Recurso", "Resultado_recurso", "ResultadoRecurso", "Resultado"]

for name in possible_result_names:
    if name in df.columns:
        resultado_column = name
        break

if resultado_column:
    st.sidebar.subheader("Filtrar por Resultado")
    resultados = get_unique_options(resultado_column, df)
    selected_resultado = st.sidebar.selectbox("Selecciona resultado:", resultados)
else:
    st.sidebar.warning("Columna de resultado no encontrada")
    selected_resultado = "Todos"

# Aplicar filtros
filtered_df = df.copy()

if selected_materia != "Todos":
    filtered_df = filtered_df[filtered_df["Materia"] == selected_materia]

if selected_tipo != "Todos" and tipo_recurso_column:
    filtered_df = filtered_df[filtered_df[tipo_recurso_column] == selected_tipo]

if selected_resultado != "Todos" and resultado_column:
    filtered_df = filtered_df[filtered_df[resultado_column] == selected_resultado]

if search_term and "Descriptores" in df.columns:
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
    unique_materias = df["Materia"].nunique() if "Materia" in df.columns else 0
    st.metric("Materias Únicas", unique_materias)

with col4:
    unique_tipos = df[tipo_recurso_column].nunique() if tipo_recurso_column else 0
    st.metric("Tipos de Recurso", unique_tipos)

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
        if "Materia" in df.columns:
            st.write("**Materias más comunes:**")
            materia_counts = df["Materia"].value_counts().head(10)
            st.bar_chart(materia_counts)
        else:
            st.warning("Columna 'Materia' no disponible")
    
    with col2:
        if resultado_column and resultado_column in df.columns:
            st.write("**Resultados más frecuentes:**")
            resultado_counts = df[resultado_column].value_counts().head(10)
            st.bar_chart(resultado_counts)
        else:
            st.warning("Columna de resultados no disponible")
    
    # Vista previa de datos
    st.subheader("Vista Previa de los Datos")
    
    # Seleccionar columnas disponibles para mostrar
    available_columns = []
    for col in ["Rol", "Caratulado", "Materia", resultado_column, tipo_recurso_column]:
        if col and col in df.columns:
            available_columns.append(col)
    
    if available_columns:
        st.dataframe(
            filtered_df[available_columns].head(10),
            use_container_width=True
        )
    else:
        st.warning("No hay columnas disponibles para mostrar")

with tab2:
    st.subheader("Términos Más Frecuentes en Descriptores")
    
    if "Descriptores" in df.columns:
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
    else:
        st.warning("Columna 'Descriptores' no encontrada en el dataset")

with tab3:
    st.subheader("Sentencias Filtradas")
    
    if len(filtered_df) == 0:
        st.warning("No hay sentencias que coincidan con los filtros seleccionados.")
    else:
        st.success(f"Se encontraron {len(filtered_df)} sentencias que coinciden con los filtros.")
        
        # Mostrar todas las columnas disponibles
        available_columns = filtered_df.columns.tolist()
        
        # Columnas por defecto (si existen)
        default_cols = []
        for col in ["Rol", "Caratulado", "Materia", resultado_column, tipo_recurso_column]:
            if col and col in available_columns:
                default_cols.append(col)
        
        if not default_cols:
            default_cols = available_columns[:3]  # Tomar primeras 3 columnas
        
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
    
    if "Descriptores" in df.columns:
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
                    # Mostrar columnas disponibles
                    display_cols = []
                    for col in ["Rol", "Caratulado", "Materia", "Descriptores"]:
                        if col in advanced_filtered.columns:
                            display_cols.append(col)
                    
                    st.dataframe(
                        advanced_filtered[display_cols],
                        use_container_width=True
                    )
    else:
        st.warning("Columna 'Descriptores' no disponible para búsqueda avanzada")

# Información adicional
st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ Instrucciones")
st.sidebar.info("""
1. Usa los filtros para refinar tu búsqueda
2. Explora las diferentes pestañas para distintos tipos de análisis
3. Descarga los resultados filtrados en CSV
""")

# Mostrar estructura completa del dataset en el sidebar para debugging
with st.sidebar.expander("🔧 Debug Info"):
    st.write("**Estructura del dataset:**")
    st.write(f"- Filas: {len(df)}")
    st.write(f"- Columnas: {len(df.columns)}")
    st.write("**Columnas disponibles:**")
    for col in df.columns:
        st.write(f"- {col}")

# Pie de página
st.markdown("---")
st.caption("📊 Aplicación de análisis de sentencias ambientales | Desarrollado con Streamlit")
