import pandas as pd
import numpy as np

#-----------------------------------------------------------------------------------------------------------------#
# Funcion para PROCESAR DATOS DE PRODUCCIÓN
#-----------------------------------------------------------------------------------------------------------------#

def procesar_datos_produccion(nombre_archivo):
    """
    Busca el archivo en la carpeta 'datos' y calcula la eficiencia.
    """
    # Construimos la ruta: sube un nivel y entra a 'datos'
    ruta_completa = f"../datos/{nombre_archivo}"
    
    try:
        df = pd.read_csv(ruta_completa)
        
        # Limpieza de datos
        df['prod_real_bpd'] = pd.to_numeric(df['prod_real_bpd'], errors='coerce')
        df['prod_teorica_bpd'] = pd.to_numeric(df['prod_teorica_bpd'], errors='coerce')

        # Cálculos core
        df['eficiencia'] = (df['prod_real_bpd'] / df['prod_teorica_bpd'].replace(0, np.nan)) * 100
        df['barriles_perdidos'] = df['prod_teorica_bpd'] - df['prod_real_bpd']
        
        return df

    except FileNotFoundError:
        print(f"❌ Error: No se encuentra el archivo en {ruta_completa}")
        return None

#-----------------------------------------------------------------------------------------------------------------#
# Funcion para REPORTE .PDF
#-----------------------------------------------------------------------------------------------------------------#

def generar_resumen_ejecutivo(df):
    """
    Genera métricas clave para la toma de decisiones.
    """
    if df is None or df.empty:
        return None
    
    resumen = {
        'eficiencia_promedio': df['eficiencia'].mean(),
        'total_barriles_perdidos': df['barriles_perdidos'].sum(),
        'pozo_critico_id': df.sort_values(by='barriles_perdidos', ascending=False).iloc[0]['pozo_id'],
        'cantidad_pozos_alerta': len(df[df['eficiencia'] < 70]),
        'potencial_mejora_usd': df['barriles_perdidos'].sum() * 75 # Supongamos el barril a 75 USD
    }
    
    return resumen