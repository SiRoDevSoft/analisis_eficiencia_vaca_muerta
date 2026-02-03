import io
from fpdf import FPDF
from datetime import datetime
import matplotlib.pyplot as plt

class ReportePetrolero(FPDF):
    def header(self):
        # Titulo corporativo sin caracteres especiales
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Cuenca Operativa | 2026', 0, 1, 'R')
        self.line(10, 15, 200, 15)
        self.ln(5)

       
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()} | Firma: Rojas Silvio Jonathan - Data Analyst', 0, 0, 'C')

def generar_grafico_memoria(datos):
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(6, 2.5))
    
    categorias = ['Prod. Actual', 'Punto Quiebre']
    valores = [datos['qi'], datos['q_limite']]
    
    ax.barh(categorias, valores, color=['#2980b9', '#e74c3c'])
    ax.set_title("Comparativa de Producción (bbl/d)", fontsize=10, fontweight='bold')
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    plt.close(fig)
    buf.seek(0)
    return buf

        
def crear_informe_ejecutivo(datos):
    """
    Recibe un dict con: qi, brent, q_limite, opex, estado, dia_quiebre
    """
    # 1. Limpieza de seguridad para strings
    for clave in datos:
        if isinstance(datos[clave], str):
            datos[clave] = datos[clave].replace('ñ', 'n').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u').replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U').replace('Ñ', 'N')

    # 2. Inicializar PDF
    pdf = ReportePetrolero()
    pdf.add_page()

     # Título
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, 'INFORME OPERATIVO: VACA MUERTA', 0, 1, 'C')
    pdf.set_font('helvetica', 'I', 10)
    pdf.cell(0, 5, f'Generado: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'C')
    pdf.ln(10)
    
    pdf.set_fill_color(245, 245, 245)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, ' INDICADORES CLAVE (KPIs)', 0, 1, 'L', fill=True)
    pdf.ln(5)

    # --- SECCIÓN 1: RESUMEN ECONÓMICO ---
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, ' 1. ANALISIS DE RENTABILIDAD', 0, 1, 'L', fill=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(95, 10, f"Precio Brent Base: USD {datos['brent']}",1, 0, 'C')
    pdf.cell(95, 10, f"Punto de Quiebre (Qel): {datos['q_limite']:.2f} bbl/d",1, 1, 'C' )
    pdf.cell(95, 10, f"OPEX Diario Estimado: USD {datos['opex']:.2f}", 1, 0, 'C')
    pdf.ln(15)
    
    # --- SECCIÓN 2: ESTADO TÉCNICO ---
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, ' 2. DIAGNOSTICO DEL ACTIVO', 0, 1, 'L', fill=True)
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    pdf.cell(0, 10, f"Produccion Inicial Registrada: {datos['qi']} bbl/d", 0, 1)
    pdf.cell(0, 10, f"Vida Util Estimada (Dias de flujo positivo): {datos['dia_quiebre']} dias", 0, 1,)
    
    # Color según estado (Verde si es rentable, Rojo si no)
    if "RENTABLE" in datos['estado'].upper():
        pdf.set_text_color(0, 128, 0)
    else:
        pdf.set_text_color(255, 0, 0)
        
    pdf.set_font('Arial', 'B', 14)
    pdf.ln(5)
    pdf.multi_cell(0, 10, f"CONCLUSION: {datos['estado']}", align='C')

    # Gráfico
    pdf.ln(10)
    img_buf = generar_grafico_memoria(datos)
    # En fpdf2, pasar el buffer de BytesIO es la forma correcta
    pdf.image(img_buf, x=40, w=130)
    
    # 3. Retornar bytes puros para Streamlit
    return bytes(pdf.output())