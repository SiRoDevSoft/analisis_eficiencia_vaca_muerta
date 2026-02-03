
import os
from fpdf import FPDF
import matplotlib.pyplot as plt

# Importamos tus funciones de lógica de negocio
from funciones_petroleras import calcular_metricas_emulsion

class ReportePetroleroPro(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, 'YPF - PROYECTO ANELO 2026 - Reporte de Ingeniería', 0, 1, 'C')
        self.ln(5)

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, label, 0, 1, 'L', fill=True)
        self.ln(4)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')


def generar_reporte_avanzado(df, df_historico, dia_quiebre, produccion_futura):


    # 1. DEFINICIÓN DE RUTAS PROFESIONAL
    # Usamos la raíz del proyecto para assets y una carpeta temporal para el gráfico
    base_path = os.getcwd() # Obtiene la raíz donde está main.py
    ruta_assets = os.path.join(base_path, "assets")

    # El gráfico lo guardamos en el sistema temporal del servidor
    ruta_img = "temp_grafico.png" 
    # El PDF final lo guardamos donde Streamlit pueda encontrarlo
    ruta_final = "Reporte_Final_YPF_2026.pdf"

    pdf = ReportePetroleroPro()
    pdf.add_page()

    # 2. PROCESAMIENTO DE DATOS
    total_perdida = df['perdida_usd_dia'].sum()
    top_5 = df.sort_values('perdida_usd_dia', ascending=False).head(5)

    # 3. GRÁFICO
    plt.figure(figsize=(8, 5))
    plt.scatter(df['water_cut'], df['perdida_usd_dia'], alpha=0.6, c=df['perdida_usd_dia'], cmap='Reds')
    plt.title("Analisis de Perdidas - Proyecto Anelo 2026")
    plt.savefig(ruta_img, dpi=100)
    plt.close()  

    # Título
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 15, 'ALERTA: IMPACTO ECONOMICO DIARIO', 0, 1, 'C')

    # Imagen
    pdf.image(ruta_img, x=15, w=180)
    pdf.ln(5)

    # TABLA TOP 5 (Con celdas reforzadas)
    pdf.set_font('Arial', 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, 'Detalle de Pozos Criticos (Top 5):', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for _, row in top_5.iterrows():
        texto_fila = f"ID: {row['pozo_id']} | Agua: {row['water_cut']:.1f}% | Perdida: USD {row['perdida_usd_dia']:,.0f}"
        pdf.cell(0, 8, texto_fila, border=1, ln=1)

    # IMPACTO TOTAL (Toque personal)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Perdida Total Estimada del Yacimiento:', 0, 1)
    pdf.ln(2)
    texto_total = f"Impacto Total del Diferido: USD {total_perdida:,.2f} / dia"
    pdf.cell(0, 10, texto_total, border=1, ln=1, align='L')

    # 4. CÁLCULO DE MÉTRICAS INTEGRADAS
    df_analisis = calcular_metricas_emulsion(df_historico)
    costo_quimico_total = df_analisis['costo_quimico_usd'].sum()
    
    pdf.ln(10)
    pdf.add_page()
    # --- SECCIÓN 1: TRATAMIENTO QUÍMICO Y EMULSIÓN ---
    pdf.section_title("1. ANALISIS DE EMULSION Y COSTOS OPERATIVOS")
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 7, f"Se ha detectado un impacto acumulado de USD {costo_quimico_total:,.2f} en concepto "
                         f"de desemulsionantes. La relacion temperatura/viscosidad sugiere optimizar "
                         f"los puntos de inyeccion en fondo.")
    
    # Insertamos el gráfico de dispersión de la Celda 1
    if os.path.exists('../assets/grafico_emulsion.png'):
        pdf.image('../assets/grafico_emulsion.png', x=15, w=170)
    pdf.ln(5)

    # --- SECCIÓN 2: DECLINACIÓN Y LÍMITE ECONÓMICO ---
    pdf.add_page()
    pdf.section_title("2. PRONOSTICO DE PRODUCCION (ARPS) Y RENTABILIDAD")
    
    # Insertamos el gráfico de la curva roja de la Celda 3
    if os.path.exists('../assets/grafico_declinacion.png'):
        pdf.image('../assets/grafico_declinacion.png', x=15, w=170)
    
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    
    # Lógica de Alerta de Cierre
    if dia_quiebre:
        pdf.set_text_color(200, 0, 0)
        mensaje_bep = f"ALERTA CRITICA: El pozo alcanzara su limite economico en el dia {dia_quiebre}."
    else:
        pdf.set_text_color(0, 128, 0)
        mensaje_bep = "PRODUCCION ESTABLE: No se prevé quiebre de stock en el horizonte de 180 dias."
    
    pdf.cell(0, 10, mensaje_bep, border=1, ln=1, align='C')

    # --- SECCIÓN: ANÁLISIS DE RENTABILIDAD ---
    pdf.add_page()
    pdf.section_title("3. PROYECCION ECONOMICA Y FLUJO NETO")
    
    # Parámetros para el cálculo (los mismos de tu notebook)
    precio_brent = 75
    opex_diario = 58000
    
    # Calculamos valores clave
    q_actual = produccion_futura[0]
    q_final = produccion_futura[-1]
    ingreso_hoy = q_actual * precio_brent
    ingreso_180 = q_final * precio_brent
    
    # Definimos los datos de la tabla
    header = ['Escenario', 'Produccion', 'Ingresos (USD)', 'Flujo Neto (USD)']
    datos = [
        ['Actual (Hoy)', f"{q_actual:,.1f}", f"{ingreso_hoy:,.0f}", f"{ingreso_hoy - opex_diario:,.0f}"],
        ['Proyeccion (180d)', f"{q_final:,.1f}", f"{ingreso_180:,.0f}", f"{ingreso_180 - opex_diario:,.0f}"]
    ]

    # Dibujamos la tabla
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    col_width = 45
    
    # Encabezado
    for h in header:
        pdf.cell(col_width, 10, h, 1, 0, 'C', True)
    pdf.ln()
    
    # Filas con lógica de color
    pdf.set_font('Arial', '', 10)
    for fila in datos:
        for i, dato in enumerate(fila):
            # Si el Flujo Neto es negativo, lo ponemos en rojo
            if i == 3 and "-" in dato:
                pdf.set_text_color(200, 0, 0)
            pdf.cell(col_width, 10, dato, 1, 0, 'C')
            pdf.set_text_color(0, 0, 0)
        pdf.ln()

    # Mensaje de conclusión
    pdf.ln(5)
    pdf.set_font('Arial', 'I', 9)
    pdf.multi_cell(0, 5, f"Nota: El flujo neto considera un OPEX fijo de USD {opex_diario}/dia y un Brent de USD {precio_brent}.")

    # --- SECCIÓN: RENTABILIDAD INTEGRAL (PRODUCCIÓN + QUÍMICA) ---
    
    pdf.ln(10)
    pdf.section_title("3. MARGEN OPERATIVO E IMPACTO QUIMICO")

    # 1. Recuperamos métricas de las funciones petroleras
    # Usamos el promedio del costo químico del DF para la estimación
    costo_quimico_promedio = df_historico['costo_quimico_usd'].mean()
    opex_fijo = 58000
    precio_brent = 75

    # 2. Cálculos de flujo neto real (Ingreso - OPEX - Químicos)
    def calcular_neto(q):
        ingreso = q * precio_brent
        return ingreso - opex_fijo - costo_quimico_promedio

    q_hoy = produccion_futura[0]
    q_fin = produccion_futura[-1]

    # 3. Estructura de la Tabla
    header = ['Concepto', 'Produccion', 'Costo Quim.', 'Flujo Neto Real']
    datos = [
        ['Estado Actual', f"{q_hoy:,.1f} bbl/d", f"USD {costo_quimico_promedio:,.0f}", f"USD {calcular_neto(q_hoy):,.0f}"],
        ['Proy. 180 dias', f"{q_fin:,.1f} bbl/d", f"USD {costo_quimico_promedio:,.0f}", f"USD {calcular_neto(q_fin):,.0f}"]
    ]

    # 4. Dibujar Tabla con Resaltado
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(45, 45, 45) # Gris oscuro
    pdf.set_text_color(255, 255, 255)
    
    col_w = 46
    for h in header:
        pdf.cell(col_w, 10, h, 1, 0, 'C', True)
    pdf.ln()

    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 10)
    for fila in datos:
        pdf.cell(col_w, 10, fila[0], 1)
        pdf.cell(col_w, 10, fila[1], 1, 0, 'C')
        pdf.set_text_color(180, 0, 0) # Rojo para costos
        pdf.cell(col_w, 10, fila[2], 1, 0, 'C')
        
        # Lógica de color para el Flujo Neto
        neto_valor = float(fila[3].replace('USD ', '').replace(',', ''))
        if neto_valor < 0:
            pdf.set_fill_color(255, 200, 200) # Fondo rojo claro si hay pérdida
            pdf.cell(col_w, 10, fila[3], 1, 0, 'C', True)
        else:
            pdf.set_text_color(0, 100, 0) # Verde si hay ganancia
            pdf.cell(col_w, 10, fila[3], 1, 0, 'C')
        
        pdf.set_text_color(0, 0, 0)
        pdf.ln()

    
    # --- CONCLUSIÓN ---
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 7, "Nota: Este reporte fue generado automaticamente integrando modelos de declinacion "
                         "exponencial y factores reologicos de emulsion.")

    pdf.output(ruta_final)
    return ruta_final
