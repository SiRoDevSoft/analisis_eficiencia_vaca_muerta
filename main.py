import streamlit as st
import pandas as pd
import plotly.express as px
from src.petro_logic import calcular_q_limite, get_documentation_pdf, sanitize_production_data
from src.sanitizer import inject_demo_fault # Importamos el "inyector" de ruido


st.set_page_config(page_title="Proyecto Añelo 2026", layout="wide")
st.title("🛢️ Sistema de Gestión de Activos - VACA MUERTA 2026")

# Sanitización de datos SCADA
# 1. Simulamos la lectura del dato crudo
df_campo = pd.read_csv('datos/datos_campo_masivos.csv')


# 1.2. INTERFAZ DE CAOS (Sidebar)
st.sidebar.subheader("🧪 Stress Test: Integridad")
tipo_ruido = st.sidebar.selectbox(
    "Simular falla en sensores:",
    ["Ninguno", "Pico de Gas (Outlier Alto)", "Falla Eléctrica (Cero)", "Producción Absurda (Error Crítico)", "Inestabilidad"]
)

# 1.3. PROCESAMIENTO
raw_list = df_campo['prod_real_bpd'].tolist()

# Primero "ensuciamos" si el usuario quiere
data_to_process = inject_demo_fault(raw_list, tipo_ruido)

# Luego "sanitizamos" con tu lógica de Z-Score
clean_list = sanitize_production_data(data_to_process)


# Actualizamos el DataFrame para los gráficos
df_campo['prod_real_bpd'] = clean_list

st.divider()
# 1.4. FEEDBACK VISUAL
if tipo_ruido != "Ninguno":
    # 1. Calculamos outliers totales
    outliers = sum(1 for r, c in zip(data_to_process, clean_list) if r != c)
    
    # 2. CARTEL ROJO: Lo forzamos por el nombre de la opción o por detección
    if tipo_ruido == "Producción Absurda (Error Crítico)" or abs(data_to_process[0] - clean_list[0]) > 10:
        st.error(f"""
            ### 🚨 Detección de Ruido: Valor corregido
            Se detectó una lectura crítica de **{data_to_process[0]:,.2f} bpd**.  
            **Acción del Sistema:** El algoritmo ha filtrado el valor y lo ha reemplazado por la media estadística de **{clean_list[0]:,.2f} bpd**.
        """)
    
    # 3. WARNING SIDEBAR: Para errores menores (picos de gas, etc)
    if outliers > 0 and tipo_ruido != "Producción Absurda (Error Crítico)":
        st.sidebar.warning(f"⚠️ Filtro de Resiliencia: {outliers} anomalías detectadas.")

st.sidebar.header("Condiciones de Mercado")
precio_brent = st.sidebar.slider("Precio Brent (USD/bbl)", 40, 120, 75)
regalias = 0.12
opex_fijo_mensual = 50000 

# 4. Ahora sí, calculás rentabilidad y proyecciones con datos confiables
q_lim_estandar = calcular_q_limite(opex_fijo_mensual/30, precio_brent, regalias)

# Filtramos pozos saludables (por encima del límite)
pozos_activos = df_campo[df_campo['prod_real_bpd'] > q_lim_estandar]
prod_total = df_campo['prod_real_bpd'].sum()

df_campo['rentable'] = df_campo['prod_real_bpd'] > q_lim_estandar
pozos_riesgo = df_campo[df_campo['rentable'] == False]

# --- INTERFAZ DINÁMICA ---

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Activos", f"{len(df_campo)} Pozos", "Cuenca Neuquina")
with col2:
    st.metric("Producción Campo", f"{prod_total:,.0f} bbl/d", f"{prod_total/len(df_campo):,.1f} avg/pozo")
with col3:
    porcentaje_salud = (len(pozos_activos) / len(df_campo)) * 100
    st.metric("Eficiencia Económica", f"{porcentaje_salud:.1f}%", f"{len(pozos_activos)} pozos rentables")
with col4:
    st.metric("Pozos en Alerta", f"{len(pozos_riesgo)}", f"{(len(pozos_riesgo)/len(df_campo))*100:.1f}% del campo", delta_color="inverse")
with col5:
    st.metric("Límite Económico", f"{q_lim_estandar:.1f} bpd", delta=f"{precio_brent} USD/bbl", delta_color="off")

st.divider()

# Gráfico dinámico: Distribución de Producción
st.subheader("📊 Salud del Yacimiento")

fig_dist = px.histogram(df_campo, x="prod_real_bpd", 
                         color="rentable",
                         title="Distribución de Pozos según Rentabilidad Actual",
                         labels={'prod_real_bpd': 'Producción (bpd)', 'rentable': 'Es Rentable'},
                         color_discrete_map={True: '#00FF00', False: '#FF4B4B'},
                         template="plotly_dark",
                         range_x=[0, 1000])

# Línea de referencia del límite económico en el gráfico
fig_dist.add_vline(x=q_lim_estandar, line_dash="dash", line_color="yellow", annotation_text="Punto de Equilibrio")

st.plotly_chart(fig_dist, use_container_width=True)

st.divider()


col1, col2, col3 = st.columns([1, 2, 1]) 
with col2:
    if st.button("VER ACTIVOS EN PRODUCCIÓN", icon=":material/query_stats:"):
        st.switch_page("pages/01_Vista_Global.py")


st.divider()
st.space(30)
# Sección de Perfil Profesional (Tu firma de LinkedIn)
col_perfil, col_info = st.columns([1, 3])

with col_perfil:
    st.image("assets/img/imagen.png", width=240)

with col_info:
    # Tu titular de LinkedIn con estilo
    st.markdown(f"""
    ### **Silvio Rojas**
    #### **IT/OT Operations Analyst | Asset Integrity & Field Data | SQL · Python**
    
    *Especialista en la optimización de activos mediante el análisis de datos operativos y de integridad en tiempo real. Desarrollando soluciones analíticas para la Cuenca Neuquina.*
    
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/silviojonrojas) 
    """)

# Una pequeña caja con tu "Propuesta de Valor"
st.info("""
**Propuesta de Valor:** Transformo volúmenes de datos críticos en tableros de control ejecutivos que permiten predecir el límite económico y optimizar la vida útil de los pozos en Vaca Muerta.
""")

st.sidebar.space(500)
st.sidebar.divider()
st.sidebar.title("Documentación")
# Llamamos a la lógica para obtener el archivo
pdf_bytes = get_documentation_pdf()

if pdf_bytes:
    st.sidebar.download_button(
        label="User Manual (PDF)",
        data=pdf_bytes,
        file_name="Manual_Usuario_Vaca_Muerta.pdf",
        mime="application/pdf"
    )
else:
    st.sidebar.error("Documentación no disponible")

st.sidebar.markdown("[🔬 Engineering Manual (GitHub)](https://github.com/SiRoDevSoft/analisis_eficiencia_vaca_muerta)")