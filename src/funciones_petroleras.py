import pandas as pd
import numpy as np

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