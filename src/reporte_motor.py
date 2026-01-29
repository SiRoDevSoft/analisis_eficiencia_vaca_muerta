import os
from fpdf import FPDF
import matplotlib.pyplot as plt

class ReportePetrolero(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'PROYECTO ANELO 2026 - Reporte Operativo', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_reporte_profesional(df):
    # 1. DEFINICIÓN DE RUTAS (Al principio para evitar errores)
    base_path = os.path.dirname(os.path.abspath(__file__))
    ruta_assets = os.path.join(base_path, "..", "assets")
    if not os.path.exists(ruta_assets):
        os.makedirs(ruta_assets)

    ruta_img = os.path.join(ruta_assets, "temp_grafico.png")
    ruta_final = os.path.join(ruta_assets, "Reporte_Final_YPF_2026.pdf")

    # 2. PROCESAMIENTO DE DATOS
    total_perdida = df['perdida_usd_dia'].sum()
    top_5 = df.sort_values('perdida_usd_dia', ascending=False).head(5)

    # 3. GRÁFICO
    plt.figure(figsize=(8, 5))
    plt.scatter(df['water_cut'], df['perdida_usd_dia'], alpha=0.6, c=df['perdida_usd_dia'], cmap='Reds')
    plt.title("Analisis de Perdidas - Proyecto Anelo 2026")
    plt.savefig(ruta_img, dpi=100)
    plt.close()

    # 4. CONSTRUCCIÓN DEL PDF
    pdf = ReportePetrolero()
    pdf.add_page()
    
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

    # IMPACTO TOTAL (Tu toque personal)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, 'Perdida Total Estimada del Yacimiento:', 0, 1)
    pdf.ln(2)
    texto_total = f"Impacto Total del Diferido: USD {total_perdida:,.2f} / dia"
    pdf.cell(0, 10, texto_total, border=1, ln=1, align='L')

    # Guardar
    pdf.output(ruta_final)
    
    # Limpieza
    if os.path.exists(ruta_img):
        os.remove(ruta_img)
        
    return ruta_final