
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================

st.set_page_config(
    page_title="SIEP-GYE | Análisis Energético",
    page_icon="⚡",
    layout="wide"
)

# ==========================================
# ESTILOS
# ==========================================

st.title("⚡ SIEP-GYE")
st.subheader(
    "Sistema Inteligente de Predicción y Análisis Energético"
)
st.markdown(
    "Plataforma de análisis de demanda eléctrica, "
    "variables climáticas y pérdidas energéticas en Guayaquil."
)

st.divider()

# ==========================================
# CARGAR DATASET
# ==========================================

RUTA_DATOS = (
    Path(__file__).parent
    / "data"
    / "dataset_siep_gye_2026.csv"
)

@st.cache_data
def cargar_datos():
    df = pd.read_csv(RUTA_DATOS)
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"No se pudo cargar el dataset: {e}")
    st.stop()

# ==========================================
# FILTROS
# ==========================================

st.sidebar.header("Filtros de consulta")

sectores = sorted(df["sector"].dropna().unique())
fases = sorted(df["fase_climatica"].dropna().unique())

sector_seleccionado = st.sidebar.multiselect(
    "Seleccionar sectores",
    sectores,
    default=sectores
)

fase_seleccionada = st.sidebar.multiselect(
    "Fase climática",
    fases,
    default=fases
)

fecha_min = df["fecha"].min().date()
fecha_max = df["fecha"].max().date()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

if len(rango_fechas) != 2:
    st.warning("Selecciona una fecha inicial y una final.")
    st.stop()

fecha_inicio, fecha_fin = rango_fechas

# ==========================================
# APLICAR FILTROS
# ==========================================

datos = df[
    (df["sector"].isin(sector_seleccionado))
    & (df["fase_climatica"].isin(fase_seleccionada))
    & (df["fecha"].dt.date >= fecha_inicio)
    & (df["fecha"].dt.date <= fecha_fin)
].copy()

if datos.empty:
    st.warning("No existen registros para los filtros seleccionados.")
    st.stop()

# ==========================================
# INDICADORES PRINCIPALES
# ==========================================

st.header("Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Demanda promedio",
    f"{datos['demanda_mw'].mean():,.2f} MW"
)

col2.metric(
    "Pérdida promedio",
    f"{datos['perdida_mw'].mean():,.2f} MW"
)

col3.metric(
    "Temperatura promedio",
    f"{datos['temperatura'].mean():.2f} °C"
)

col4.metric(
    "Humedad promedio",
    f"{datos['humedad'].mean():.2f} %"
)

st.caption(
    "Los indicadores se calculan a partir de los registros "
    "del dataset seleccionado; no representan por sí solos "
    "mediciones oficiales de CNEL."
)

st.divider()

# ==========================================
# GRÁFICO DE DEMANDA
# ==========================================

st.header("Comportamiento de la demanda energética")

demanda_tiempo = (
    datos.groupby("fecha", as_index=False)["demanda_mw"]
    .mean()
)

fig_demanda = px.line(
    demanda_tiempo,
    x="fecha",
    y="demanda_mw",
    title="Demanda promedio a lo largo del tiempo",
    labels={
        "fecha": "Fecha",
        "demanda_mw": "Demanda (MW)"
    }
)

fig_demanda.update_layout(
    hovermode="x unified"
)

st.plotly_chart(fig_demanda, use_container_width=True)

# ==========================================
# ANÁLISIS POR SECTOR
# ==========================================

st.header("Análisis por sector")

demanda_sector = (
    datos.groupby("sector", as_index=False)
    ["demanda_mw"].mean()
    .sort_values("demanda_mw", ascending=False)
)

fig_sector = px.bar(
    demanda_sector,
    x="sector",
    y="demanda_mw",
    color="sector",
    title="Demanda promedio por sector",
    labels={
        "sector": "Sector",
        "demanda_mw": "Demanda promedio (MW)"
    }
)

st.plotly_chart(fig_sector, use_container_width=True)

# ==========================================
# COMPORTAMIENTO HORARIO
# ==========================================

st.header("Comportamiento por hora del día")

demanda_hora = (
    datos.groupby("hora", as_index=False)["demanda_mw"]
    .mean()
)

fig_hora = px.line(
    demanda_hora,
    x="hora",
    y="demanda_mw",
    markers=True,
    title="Demanda promedio según la hora",
    labels={
        "hora": "Hora del día",
        "demanda_mw": "Demanda promedio (MW)"
    }
)

st.plotly_chart(fig_hora, use_container_width=True)

# ==========================================
# VARIABLES CLIMÁTICAS
# ==========================================

st.header("Análisis de variables climáticas")

col1, col2 = st.columns(2)

with col1:
    fig_temp = px.line(
        datos.groupby("fecha", as_index=False)["temperatura"].mean(),
        x="fecha",
        y="temperatura",
        title="Temperatura promedio",
        labels={
            "fecha": "Fecha",
            "temperatura": "Temperatura (°C)"
        }
    )
    st.plotly_chart(fig_temp, use_container_width=True)

with col2:
    fig_humedad = px.line(
        datos.groupby("fecha", as_index=False)["humedad"].mean(),
        x="fecha",
        y="humedad",
        title="Humedad promedio",
        labels={
            "fecha": "Fecha",
            "humedad": "Humedad (%)"
        }
    )
    st.plotly_chart(fig_humedad, use_container_width=True)

# ==========================================
# PÉRDIDAS ENERGÉTICAS
# ==========================================

st.header("Análisis de pérdidas energéticas")

perdidas = (
    datos.groupby("sector", as_index=False)
    ["perdida_mw"].mean()
)

fig_perdidas = px.bar(
    perdidas,
    x="sector",
    y="perdida_mw",
    color="sector",
    title="Pérdida promedio por sector",
    labels={
        "sector": "Sector",
        "perdida_mw": "Pérdida promedio (MW)"
    }
)

st.plotly_chart(fig_perdidas, use_container_width=True)

# ==========================================
# RELACIÓN CLIMA Y DEMANDA
# ==========================================

st.header("Relación entre temperatura y demanda")

fig_relacion = px.scatter(
    datos,
    x="temperatura",
    y="demanda_mw",
    color="sector",
    opacity=0.5,
    title="Temperatura frente a demanda energética",
    labels={
        "temperatura": "Temperatura (°C)",
        "demanda_mw": "Demanda (MW)"
    }
)

st.plotly_chart(fig_relacion, use_container_width=True)

# ==========================================
# TABLA DE DATOS
# ==========================================

st.header("Registros del dataset")

st.dataframe(
    datos,
    use_container_width=True,
    hide_index=True
)

# ==========================================
# DESCARGAR DATOS FILTRADOS
# ==========================================

csv = datos.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Descargar datos filtrados",
    data=csv,
    file_name="datos_siep_gye_filtrados.csv",
    mime="text/csv"
)

# ==========================================
# PIE DE PÁGINA
# ==========================================

st.divider()

st.caption(
    "SIEP-GYE | Proyecto académico de análisis energético "
    "y variables climáticas de Guayaquil | 2026"
)
