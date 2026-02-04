# src/petro_logic.py
import numpy as np

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
    cf_acumulado = np.cumsum(cf_diario)
    return cf_diario, cf_acumulado