# src/petro_logic.py
import numpy as np
from pathlib import Path

from src.sanitizer import filter_by_integrity 

def sanitize_production_data(raw_data_list):
    """
    Sanitiza la producción usando Z-Score sobre el set completo.
    Detecta valores absurdos y ruidos estadísticos.
    """
    if not raw_data_list:
        return []

    data = np.array(raw_data_list)
    mean = np.nanmean(data)
    std = np.nanstd(data)
    
    # Definimos un umbral de Z-Score (3 es el estándar industrial)
    # También agregamos un límite físico para Vaca Muerta (ej: 2500 bpd)
    clean_data = []
    for value in data:
            # Si el valor es nulo, absurdo (>2500) o estadísticamente loco
            if np.isnan(value) or value > 2500 or abs((value - mean) / std) > 3:
                clean_data.append(mean)
            else:
                clean_data.append(value)
                
    return clean_data


def calcular_q_limite(opex_diario, precio_brent, regalias=0.12):
    """Calcula el punto de equilibrio económico (Qel) con blindaje."""
    try:
        # Validación de seguridad
        if precio_brent <= 0:
            return 0.0
        
        denominador = precio_brent * (1 - regalias)
        if denominador <= 0:
            return 0.0
            
        return opex_diario / denominador
    except Exception:
        return 0.0

def proyectar_produccion(qi, di, dias_proyeccion=200):
    """Genera la curva de declinación exponencial."""
    try:
        dias = np.arange(0, dias_proyeccion)
        prod = qi * np.exp(-di * dias)
        return dias, prod
    except Exception as e:
        print(f"Error en proyección: {e}")
        return np.array([0]), np.array([0])

def calcular_flujo_caja(prod_proyectada, precio_brent, opex_total_diario, regalias=0.12):
    """Calcula el cash flow diario y acumulado."""
    ingreso_neto = prod_proyectada * precio_brent * (1 - regalias)
    cf_diario = ingreso_neto - opex_total_diario
    mascara_rentabilidad = cf_diario > 0
    cf_diario_positivo = np.where(mascara_rentabilidad, cf_diario, 0)
    cf_acumulado = np.cumsum(cf_diario_positivo)
    return cf_diario, cf_acumulado

def get_documentation_pdf():
 # Detecta la raíz del proyecto dinámicamente
    project_root = Path(__file__).resolve().parent.parent
    pdf_path = project_root / "assets" / "pdf" / "documentation.pdf"

    if pdf_path.exists():
        return pdf_path.read_bytes()
    return None