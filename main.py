from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.funciones_petroleras import predecir_declinacion_arps 
from src.generador_reportes import crear_informe_ejecutivo


st.set_page_config(layout="wide", page_title="Monitor Vaca Muerta")

# --- 1. NUEVA SECCIÓN: LECTURA DE DATOS REALES ---
@st.cache_data
def cargar_datos_csv():
    try:
        df_hist = pd.read_csv('datos/produccion_historica.csv')
        # Extraemos los últimos valores reales de tus columnas
        q_inicio = df_hist['q_petroleo'].iloc[-1]
        bsw_real = df_hist['water_cut'].iloc[-1]
        return q_inicio, bsw_real
    except Exception as e:
        # Si el archivo falla, usamos tus valores originales como respaldo (Safety)
        return 874.1, 0.30

# Ejecutamos la carga
qi_dinamico, bsw_dinamico = cargar_datos_csv()

# Configuración de rutas para importar tus funciones de ingeniería
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# --- INTERFAZ ---
st.title("🛢️ Centro de Control Operativo - Vaca Muerta")

# Parámetros en el Sidebar
st.sidebar.header("Variables de Mercado")
precio_brent = st.sidebar.slider("Precio Brent (USD/bbl)", 40, 120, 75)
opex_diario = 58000  # Valor fijo según analisis del reporte anterior
regalias = 0.12

# --- LÓGICA DE INGENIERÍA ---

# Calculamos el Qel (Barriles mínimos para no perder plata)
q_limite = opex_diario / (precio_brent * (1 - regalias))

# Datos de producción (Simulando 200 días de proyección)
dias = np.arange(0, 200)
qi = 874.1  # Producción inicial según reporte
di = 0.0007 # Tasa de declinación nominal diaria
prod_proyectada = qi * np.exp(-di * dias)



# --- VISUALIZACIÓN ---
fig = go.Figure()

# Curva de producción
fig.add_trace(go.Scatter(x=dias, y=prod_proyectada, name='Producción Proyectada', line=dict(color='#FF4B4B', width=3)))

# Línea dinámica de Límite Económico
fig.add_hline(y=q_limite, line_dash="dash", line_color="#00FF00", 
              annotation_text=f"Límite Económico: {q_limite:.1f} bbl/d", 
              annotation_position="bottom right")

fig.update_layout(title='Análisis de Viabilidad Económica', xaxis_title='Días desde hoy', yaxis_title='Producción (bbl/d)', template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# --- MÉTRICAS CRÍTICAS ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Punto de Quiebre (Qel)", f"{q_limite:.2f} bbl/d")
with col2:
    # Encontrar el día donde la producción cae por debajo del límite
    dia_quiebre = np.where(prod_proyectada < q_limite)[0]
    dia_final = dia_quiebre[0] if len(dia_quiebre) > 0 else 200
    st.metric("Días de Vida Útil", f"{dia_final} días")


if dia_final == 0:
    st.error(f"🚨 **INVIABLE:** Con Brent a USD {precio_brent}, los costos operativos (OPEX) superan los ingresos desde el inicio. El pozo genera pérdidas inmediatas.")
    st.metric("Déficit Inicial", f"{prod_proyectada[0] - q_limite:.2f} bbl/d", delta_color="inverse")
    
elif dia_final < 100:
    st.warning(f"⚠️ **ALERTA DE CIERRE PRÓXIMO:** El pozo entrará en zona de pérdida en apenas {dia_final} días. Evaluar optimización de OPEX urgente.")

elif dia_final < 365:
    st.info(f"📅 **LÍMITE ECONÓMICO DETECTADO:** El pozo es rentable actualmente, pero se estima su cierre técnico en el día {dia_final}.")

else:
    st.success(f"✅ **OPERACIÓN RENTABLE:** Bajo este escenario de USD {precio_brent}, el pozo se mantiene por encima del punto de equilibrio durante todo el año.")




# --- CÁLCULO DE CASH FLOW ---
st.subheader("📊 Análisis de Flujo de Caja Neto")

# Calculamos el ingreso neto por día (Ingreso - Regalías - Costos)
ingresos_diarios = prod_proyectada * precio_brent * (1 - regalias)
cash_flow_diario = ingresos_diarios - opex_diario

# Cash Flow Acumulado (La "bolsa" de dinero que se va llenando)
cash_flow_acumulado = np.cumsum(cash_flow_diario)

# --- VISUALIZACIÓN ---
col_cf1, col_cf2 = st.columns(2)

with col_cf1:
    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(x=dias, y=cash_flow_diario, name='CF Diario', marker_color='royalblue'))
    fig_cf.update_layout(title="Flujo de Caja Diario (USD)", template="plotly_dark")
    st.plotly_chart(fig_cf, use_container_width=True)

with col_cf2:
    fig_acum = go.Figure()
    fig_acum.add_trace(go.Scatter(x=dias, y=cash_flow_acumulado, fill='tozeroy', name='CF Acumulado', line=dict(color='gold')))
    fig_acum.update_layout(title="Rentabilidad Acumulada Anual (USD)", template="plotly_dark")
    st.plotly_chart(fig_acum, use_container_width=True)

# --- 1. NUEVAS VARIABLES EN EL SIDEBAR ---
st.sidebar.subheader("Costos Operativos")
opex_base = st.sidebar.number_input("OPEX Fijo Mensual (USD)", value=50000)
costo_tratamiento_bbl = st.sidebar.slider("Costo Tratamiento (USD/bbl fluido)", 0.5, 5.0, 1.5)


# --- 2. CÁLCULO DE CASH FLOW REALISTA ---
# Suponiendo un corte de agua (BSW) del 30% constante para este ejemplo
bsw = 0.30 
produccion_fluido = prod_proyectada / (1 - bsw)

# El costo de emulsión sube si producimos más fluido
costo_emulsion_diario = produccion_fluido * costo_tratamiento_bbl
opex_total_diario = (opex_base / 30) + costo_emulsion_diario

# Ingreso Neto (Post-Regalías)
ingreso_neto_diario = prod_proyectada * precio_brent * (1 - regalias)

# FLUJO DE CAJA FINAL
cash_flow_diario = ingreso_neto_diario - opex_total_diario
cash_flow_acumulado = np.cumsum(cash_flow_diario)

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
    "qi": qi,
    "brent": precio_brent,
    "q_limite": q_limite,
    "opex": opex_total_diario.mean(), # Usamos el promedio diario
    "estado": "OPERACION RENTABLE" if dia_final == 200 else f"ALERTA DE CIERRE (Día {dia_final})",
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

# Ajustamos el ancho de las columnas (1 parte para imagen, 4 para el texto)
col_perfil, col_cita = st.columns([1, 4])

with col_perfil:
    
    # El parámetro use_container_width asegura que se adapte al espacio
    st.image("assets/img/imagen.png", width=120)

with col_cita:
    st.markdown(
        """
        <div style="
            padding-top: 10px;
            border-left: 3px solid #FF4B4B;
            padding-left: 20px;
            font-style: italic;
            color: #E0E0E0;
            line-height: 1.6;
        ">
            "Diseñé una herramienta de monitoreo en tiempo real que integra la declinación de Arps 
            con la volatilidad del Brent para predecir el punto de cierre económico"
        </div>
        """, 
        unsafe_allow_html=True
    )
