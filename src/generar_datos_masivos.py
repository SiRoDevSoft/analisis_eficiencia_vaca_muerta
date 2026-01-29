from fpdf import FPDF
from datetime import datetime
import pandas as pd

# 1. DEFINICIÓN DEL MOTOR (La Clase y Función)
class ReportePetrolero(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'PROYECTO ANELO 2026 - Reporte Operativo', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Pagina {self.page_no()}', 0, 0, 'C')

def generar_pdf_final(df_analisis):
    pdf = ReportePetrolero()
    pdf.add_page()
    pdf.set_font('Arial', '', 10)
    
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    pdf.cell(0, 10, f'Fecha de Emision: {fecha_hoy}', 0, 1)
    pdf.ln(5)

    # Alerta Crítica
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, 'ALERTA DE SEGURIDAD OPERATIVA: POZOS CRITICOS', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.set_text_color(0, 0, 0)
    
    # Buscamos al pozo AN-005 que encontramos ayer
    if 'AN-005' in df_analisis['pozo_id'].values:
        pozo_falla = df_analisis[df_analisis['pozo_id'] == 'AN-005'].iloc[0]
        pdf.multi_cell(0, 10, f"Se ha detectado una ineficiencia critica en el pozo {pozo_falla['pozo_id']}. "
                              f"Con un Water Cut de apenas {pozo_falla['water_cut']:.2f}%, "
                              f"presenta una perdida estimada de USD {pozo_falla['perdida_usd_dia']:,.2f} por dia.")
    
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'ID Pozo', 1)
    pdf.cell(40, 10, 'WC %', 1)
    pdf.cell(60, 10, 'Perdida Diaria (USD)', 1)
    pdf.ln()
    
    pdf.set_font('Arial', '', 10)
    top_5 = df_analisis.sort_values('perdida_usd_dia', ascending=False).head(5)
    for index, row in top_5.iterrows():
        pdf.cell(40, 10, str(row['pozo_id']), 1)
        pdf.cell(40, 10, f"{row['water_cut']:.2f}", 1)
        pdf.cell(60, 10, f"{row['perdida_usd_dia']:,.2f}", 1)
        pdf.ln()

    pdf.output('Reporte_Produccion_Anelo.pdf')
    print("✅ ¡EXITO! Archivo 'Reporte_Produccion_Anelo.pdf' generado en tu carpeta.")

# 2. EJECUCIÓN (Usando el combustible que recargamos antes)
generar_pdf_final(df_masivo)

# Verificamos que df_masivo tenga los datos necesarios
if 'perdida_usd_dia' in df_masivo.columns:
    crear_pdf_productividad(df_masivo)
    print("🚀 ¡Listo! Buscá el archivo 'Reporte_Produccion_Anelo.pdf' en la carpeta de tu proyecto.")
else:
    print("⚠️ Error: Primero debés calcular la columna 'perdida_usd_dia' como hicimos ayer.")