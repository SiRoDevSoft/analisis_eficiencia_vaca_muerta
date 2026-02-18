import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Proyecto Añelo 2026", layout="wide")

st.title("🛢️ Centro de Control Operativo - Vaca Muerta")
st.sidebar.header("Parámetros de Análisis")

# Un slider para que el jefe juegue con el precio del petróleo
precio_brent = st.sidebar.slider("Precio Brent (USD/bbl)", 40, 120, 75)

st.write(f"### Análisis de Rentabilidad con Brent a USD {precio_brent}")
st.info("Conexiones de funciones de Arps aquí abajo.")

import sys
import os
import plotly.graph_objects as go

# Esto es para que Python encuentre tus funciones en la carpeta 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.funciones_petroleras import predecir_declinacion_arps 

# 1. Carga de datos (Simulada por ahora o lee tu CSV)
st.subheader("Visualización de Producción y Pronóstico")
dias = list(range(0, 200))
# Aquí conectaríamos tu función de Arps real
produccion = [874 * (0.9985**d) for d in dias] 

# 2. Gráfico Interactivo
fig = go.Figure()
fig.add_trace(go.Scatter(x=dias, y=produccion, name='Producción Proyectada', line=dict(color='red')))
fig.add_hline(y=773, line_dash="dash", annotation_text="Límite Económico", line_color="green")

fig.update_layout(title='Curva de Declinación Exponencial', xaxis_title='Días', yaxis_title='bbl/d')
st.plotly_chart(fig, use_container_width=True)

# 3. Alerta de Negocio
st.error("⚠️ Alerta: Según el Brent seleccionado, el pozo deja de ser rentable en el día 179")

# Para ejecutarlo, poné esto en la terminal: streamlit run main.py