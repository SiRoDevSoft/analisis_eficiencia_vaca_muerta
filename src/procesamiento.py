import pandas as pd
import numpy as np

def procesar_datos_produccion(ruta_archivo):
    """
    Función para cargar y analizar la eficiencia de los pozos.
    """
    try:
        # 1. Intentamos leer el archivo que nos mandan del campo
        df = pd.read_csv(ruta_archivo)
        print(f"✅ Conexión establecida. Procesando {len(df)} pozos...")

        # 2. Aplicamos la lógica de limpieza que ya sabés
        df['prod_real_bpd'] = pd.to_numeric(df['prod_real_bpd'], errors='coerce')
        df['prod_teorica_bpd'] = pd.to_numeric(df['prod_teorica_bpd'], errors='coerce')

        # 3. Calculamos la eficiencia y la pérdida (tu especialidad)
        df['eficiencia'] = (df['prod_real_bpd'] / df['prod_teorica_bpd'].replace(0, np.nan)) * 100
        df['barriles_perdidos'] = df['prod_teorica_bpd'] - df['prod_real_bpd']

        return df

    except FileNotFoundError:
        # Este es nuestro "escudo". Si el archivo no está, el script avisa.
        print(f"❌ ERROR: El archivo '{ruta_archivo}' no existe en la carpeta.")
        print("Asegurate de que el reporte de sensores esté descargado.")
        return None

# --- BLOQUE DE EJECUCIÓN ---
archivo = 'datos_campo.csv'
datos_finales = procesar_datos_produccion(archivo)

if datos_finales is not None:
    # Si todo salió bien, mostramos el Top 5 que hicimos el otro día
    top_criticos = datos_finales.query('eficiencia < 70').sort_values(by='barriles_perdidos', ascending=False)
    print("\n--- INFORME DE POZOS CRÍTICOS ---")
    print(top_criticos.head(5))