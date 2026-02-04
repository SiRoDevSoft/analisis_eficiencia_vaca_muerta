from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from src.petro_logic import calcular_q_limite

st.set_page_config(layout="wide", page_title="Master Dashboard - Cuenca Neuquina")

# --- LECTURA DE VOLUMEN CRÍTICO (Tus 100 pozos) ---
@st.cache_data
def cargar_datos_masivos():
    try:
        # Cargamos el archivo que generamos antes
        df = pd.read_csv('datos/datos_campo_masivos.csv')
        if df['water_cut'].max() > 1:
         df['water_cut'] = df['water_cut'] / 100
        return df
       
    except Exception as e:
        st.error(f"No encontré el archivo: {e}")
        return None

df_campo = cargar_datos_masivos()

# --- 2. CONTROLES DE ESCENARIO MACRO ---
st.title("🛢️ Consola de Control de Activos - 100 Pozos")

with st.sidebar:
    st.header("Variables de Mercado")
    brent = st.slider("Precio Brent (USD)", 40, 120, 75)
    opex_fijo_estimado = st.number_input("OPEX Fijo Promedio (USD/mes)", value=45000)
    costo_trat = st.slider("Costo Tratamiento (USD/bbl fluido)", 0.5, 5.0, 2.0)
    regalias = 0.12

# --- 3. CÁLCULO DE RENTABILIDAD EN LOTE ---
# Calculamos el Q_limite para este escenario de costos
q_lim_escenario = calcular_q_limite(opex_fijo_estimado / 30, brent, regalias)

# Lógica de clasificación
df_campo['Q_Limite'] = q_lim_escenario
df_campo['Margen_BPD'] = df_campo['prod_real_bpd'] - q_lim_escenario
df_campo['Estado'] = df_campo['Margen_BPD'].apply(lambda x: "✅ RENTABLE" if x > 0 else "🚨 ZONA ROJA")

# --- 4. DASHBOARD DE ALTO IMPACTO ---
m1, m2, m3 = st.columns(3)
with m1:
    st.metric("Total Pozos Analizados", len(df_campo))
with m2:
    pozos_criticos = len(df_campo[df_campo['Estado'] == "🚨 ZONA ROJA"])
    st.metric("Pozos en Riesgo", pozos_criticos, delta=-pozos_criticos, delta_color="inverse")
with m3:
    # EBITDA simplificado del área
    ingreso_total = (df_campo['prod_real_bpd'] * brent * (1 - regalias)).sum()
    ebitda_total = ingreso_total - (opex_fijo_estimado * len(df_campo))
    st.metric("EBITDA Mensual Proyectado", f"USD {ebitda_total:,.0f}")

# --- 5. RANKING Y FILTROS ---
st.divider()
st.subheader("📋 Ranking de Performance por Pozo")

# Filtro rápido
estado_filtro = st.radio("Filtrar por condición:", ["Todos", "Solo Rentables", "Solo en Riesgo"], horizontal=True)

if estado_filtro == "Solo Rentables":
    df_ver = df_campo[df_campo['Estado'] == "✅ RENTABLE"]
elif estado_filtro == "Solo en Riesgo":
    df_ver = df_campo[df_campo['Estado'] == "🚨 ZONA ROJA"]
else:
    df_ver = df_campo

st.dataframe(df_ver.sort_values(by='Margen_BPD', ascending=True), use_container_width=True)


