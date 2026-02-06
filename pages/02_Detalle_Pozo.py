from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from src.funciones_petroleras import predecir_declinacion_arps 
from src.generador_reportes import crear_informe_ejecutivo
from src.petro_logic import calcular_q_limite, proyectar_produccion, calcular_flujo_caja


st.set_page_config(layout="wide", page_title="Monitor Vaca Muerta")

if 'pozo_seleccionado' in st.session_state:
    pozo_actual = st.session_state['pozo_seleccionado']
else:
    st.switch_page("main.py") 


   
# --- 1. LECTURA DE DATOS DINÁMICA ---
@st.cache_data
def cargar_datos_pozo(id_buscado):
    try:
        # Leemos el archivo masivo que tiene los 100 pozos
        df_masivo = pd.read_csv('datos/datos_campo_masivos.csv')
        df_limpio = df_masivo[df_masivo['prod_real_bpd'] > 0].copy()
        df_limpio = df_limpio[df_limpio['prod_real_bpd'] < 5000]
        # Aseguramos que la declinación no sea cero para evitar errores matemáticos
        #Manejo de la Declinación (di)
        if 'di' not in df_limpio.columns:
            df_limpio['di'] = (df_limpio['prod_teorica_bpd'] - df_limpio['prod_real_bpd']) / df_limpio['prod_teorica_bpd']
            
            # Limpiamos el cálculo: si da negativo o cero, ponemos un mínimo técnico
            df_limpio['di'] = df_limpio['di'].apply(lambda x: x if x > 0 else 0.001)
            # Capamos la declinación máxima al 5% diario para evitar distorsiones
            df_limpio['di'] = df_limpio['di'].clip(upper=0.05)

        # Reporte de limpieza en consola (para tu seguimiento como Analista)
        filas_eliminadas = len(df_masivo) - len(df_limpio)
        if filas_eliminadas > 0:
             print(f"Resiliencia: Se omitieron {filas_eliminadas} registros inconsistentes.")

        df_limpio['pozo_id'] = df_limpio['pozo_id'].astype(str).str.strip()
        id_buscado = str(id_buscado).strip()
        
        # Filtramos por el pozo que viene de la memoria (pozo_actual)
        datos_pozo = df_limpio[df_limpio['pozo_id'] == id_buscado]
        
        if not datos_pozo.empty:
            q_inicio = float(datos_pozo['prod_real_bpd'].values[0])
            bsw_raw = float(datos_pozo['water_cut'].values[0])
            di_calculado = float(datos_pozo['di'].values[0])
            bsw_real = bsw_raw / 100 if bsw_raw > 1 else bsw_raw
            return q_inicio, bsw_real, di_calculado
        else:
           # Si entra acá, es que el ID buscado no existe en el CSV
            st.error(f"ID '{id_buscado}' no encontrado en el archivo masivo.")
            return 500.0, 0.15, 0.005
    except Exception as e:
        st.error(f"Error de lectura: {e}")
        return 874.1, 0.30

# EJECUCIÓN: Ahora le pasamos el 'pozo_actual' que recuperamos arriba
qi_real, bsw, di_real = cargar_datos_pozo(pozo_actual)

# Línea de depuración (Borrar después)
# st.write(f'⚠️ DEBUG: Produccion Real bdp:{qi_real}    | Water Cut: {bsw} ')

# --- INTERFAZ ---
st.title(f"🛢️ Centro de Control Operativo | Analizando Pozo: **{pozo_actual}**")
# Parámetros en el Sidebar
st.sidebar.header("Variables de Mercado")
precio_brent = st.sidebar.slider("Precio Brent (USD/bbl)", 40, 120, 75)
opex_diario = 58000  # Valor fijo según analisis del reporte anterior
regalias = 0.12

st.sidebar.subheader("Costos Operativos")
opex_base = st.sidebar.number_input("OPEX Fijo Mensual (USD)", value=60000)
costo_tratamiento_bbl = st.sidebar.slider("Costo Tratamiento (USD/bbl fluido)", 0.5, 5.0, 1.5)

st.sidebar.subheader("Proyección Operativo")
horizonte_proyeccion = st.sidebar.slider("Horizonte de Análisis (Días)", 30, 1095, 730)

# --- LÓGICA DE INGENIERÍA ---
m_std=30  # mes estándar de 30 días

# A. Cálculo de Punto de Equilibrio
q_limite = calcular_q_limite(
    opex_base/m_std, 
    precio_brent, 
    regalias
    )

# B. Proyección de Producción (200 días)
dias, prod_proyectada = proyectar_produccion(
    qi=qi_real, 
    di=di_real, 
    dias_proyeccion=horizonte_proyeccion
    )

# C. Cálculo de OPEX Variable (Emulsión)

produccion_fluido = prod_proyectada / (1 - bsw)
costo_emulsion_diario = produccion_fluido * costo_tratamiento_bbl
opex_total_diario = (opex_base / m_std) + costo_emulsion_diario


# D. Flujo de Caja
cash_flow_diario, cash_flow_acumulado = calcular_flujo_caja(
    prod_proyectada, 
    precio_brent, 
    opex_total_diario, 
    regalias
    )

# --- VISUALIZACIÓN ---
fig = go.Figure()

# Curva de producción
fig.add_trace(go.Scatter(x=dias, 
                         y=prod_proyectada, 
                         name='Producción Proyectada', 
                         line=dict(color='#FF4B4B', width=3),
                         hovertemplate='Día: %{x}<br>Prod: %{y:.1f} bbl/d<extra></extra>'))

# Línea dinámica de Límite Económico
fig.add_hline(
    y=q_limite, 
    line_dash="dash", 
    line_color="#00FF00", 
    annotation_text=f"Límite Económico: {q_limite:.1f} bbl/d", 
    annotation_position="bottom right"
    )
fig.add_annotation(
    x=horizonte_proyeccion * 0.8, # La posicionamos al final del gráfico
    y=prod_proyectada[0] * 0.9,
    text=f"Tasa de Declinación (di): <b>{di_real*100:.2f}%</b>",
    showarrow=False,
    font=dict(size=14, color="white"),
    bgcolor="rgba(255, 75, 75, 0.6)",
    bordercolor="#FF4B4B",
    borderwidth=1
    )

fig.update_layout(
    title='Análisis de Viabilidad Económica', 
    xaxis_title='Días de Proyección', 
    yaxis_title='Barriles por Día (bpd)', 
    template="plotly_dark",
    hovermode="x unified"
    )
st.plotly_chart(fig, use_container_width=True)

# --- MÉTRICAS CRÍTICAS ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Punto de Quiebre (Qel)", f"{q_limite:.2f} bbl/d")
with col2:
    # Encontrar el día donde la producción cae por debajo del límite
    dia_quiebre = np.where(prod_proyectada < q_limite)[0]
    dia_final = dia_quiebre[0] if len(dia_quiebre) > 0 else 730
    st.metric("Días de Vida Útil", f"{dia_final} días")
    st.write(f'Tiempo hasta llegar al Límite Económico con una proyección estimada a {horizonte_proyeccion} días.')
# Línea de depuración (Borrar después)
# st.write(f"⚠️ DEBUG: dia final: {dia_final} | Brent calculado: {precio_brent:.2f}")

if dia_final == 0:
    st.error(f"🚨 **INVIABLE PARA POZO {pozo_actual}:** Con Brent a USD {precio_brent}, los costos operativos (OPEX) superan los ingresos desde el inicio. El pozo genera pérdidas inmediatas.")
    st.metric("Déficit Inicial", f"{prod_proyectada[0] - q_limite:.2f} bbl/d", delta_color="inverse")
    
elif dia_final < 100:
    st.warning(f"⚠️ **ALERTA DE CIERRE PRÓXIMO:** EL POZO {pozo_actual} entrará en zona de pérdida en apenas {dia_final} días. Evaluar optimización de OPEX urgente.")

elif dia_final < 365:
    st.info(f"📅 **LÍMITE ECONÓMICO DETECTADO:** EL POZO {pozo_actual} es rentable actualmente, pero se estima su cierre técnico en el día {dia_final}.")

else:
    st.success(f"✅ **OPERACIÓN RENTABLE:** Bajo este escenario de USD {precio_brent}, el pozo se mantiene por encima del punto de equilibrio durante todo el año.")




# --- CÁLCULO DE CASH FLOW ---
st.subheader("📊 Análisis de Flujo de Caja Neto")

# --- VISUALIZACIÓN ---
col_cf1, col_cf2 = st.columns(2)

with col_cf1:
    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(
        x=dias, 
        y=cash_flow_diario, 
        name='CF Diario', 
        marker_color='royalblue')
        )
    fig_cf.update_layout(
        title="Flujo de Caja Diario (USD)", 
        template="plotly_dark"
        )
    st.plotly_chart(fig_cf, use_container_width=True)

with col_cf2:
    fig_acum = go.Figure()
    fig_acum.add_trace(go.Scatter(x=dias, y=cash_flow_acumulado, fill='tozeroy', name='CF Acumulado', line=dict(color='gold')))
    fig_acum.update_layout(
        title="Rentabilidad Acumulada Anual (USD)", 
        template="plotly_dark"
        )
    st.plotly_chart(fig_acum, use_container_width=True)


# --- 3. VISUALIZACIÓN ---
st.write("### 💰 Cash Flow con Costo de Emulsión Variable")
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.metric("OPEX Diario Promedio", f"USD {opex_total_diario.mean():,.2f}")
with col_m2:
    st.metric("EBITDA Proyectado Anual", f"USD {cash_flow_acumulado[-1]:,.2f}")

# Gráfico de barras para el flujo diario
fig_cash = go.Figure()
fig_cash.add_trace(go.Bar(x=dias, y=cash_flow_diario, name='Flujo Neto Diario', marker_color='lightgreen'))
fig_cash.update_layout(title="Flujo de Caja Diario (Neto)", template="plotly_dark")
st.plotly_chart(fig_cash, use_container_width=True)


# Empaquetamos la información para el reporte
datos_para_reporte = {
    "qi": round(qi_real, 2),
    "brent": precio_brent,
    "q_limite": q_limite,
    "opex": opex_total_diario.mean(), # Usamos el promedio diario
    "estado": "OPERACION RENTABLE" if dia_final == 730 else f"ALERTA DE CIERRE (Día {dia_final})",
    "dia_quiebre": dia_final
}

st.sidebar.divider()
st.sidebar.subheader("Reportes")

# Generamos el PDF en memoria
try:
    pdf_bytes = crear_informe_ejecutivo(datos_para_reporte)

    st.sidebar.download_button(
        label="📥 Descargar Reporte PDF",
        data=pdf_bytes,
        file_name=f"Reporte_Produccion_2026_{datetime.now().strftime('%d%m%y')}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.sidebar.error("Error al generar PDF. Verifique fpdf2.")


# Una línea divisoria para separar el análisis de la firma

st.divider() 
st.space(30)
# Ajustamos el ancho de las columnas (1 parte para imagen, 4 para el texto)
with st.container(border=True):
    col_info, col_cita = st.columns([3,4])
    with col_cita:
        st.markdown(
            """
            <div style="
                padding-top: 10px;
                border-left: 3px solid #FF4B4B;
                padding-left: 20px;
                font-style: italic;
                color: #BDBDBD;
                line-height: 1.6;
            ">
                "Diseñé esta herramienta de monitoreo en tiempo real que integra la declinación de Arps 
                con la volatilidad del Brent para predecir el punto de cierre económico"
            </div>
            """, 
            unsafe_allow_html=True
        )
    with col_info:
        st.info("""
        ### Stack Tecnológico del Proyecto
        - **Lenguaje:** Python 3.12 (Pandas, NumPy, Plotly).
        - **Frontend:** Streamlit Framework para Dashboards de alta disponibilidad.
        - **Modelado:** Declinación de Arps para pronóstico de reservas y límites económicos.
        - **Navegación:** Arquitectura multinivel con persistencia de estado (Session State).
        """)
        st.success("**Objetivo:** Optimizar la toma de decisiones operativas en la Cuenca Neuquina mediante análisis de datos en tiempo real.")