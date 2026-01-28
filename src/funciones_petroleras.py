import pandas as pd
import numpy as np
import os

#-----------------------------------------------------------------------------------------------------------------#
# Funcion para PROCESAR DATOS DE PRODUCCIÓN
#-----------------------------------------------------------------------------------------------------------------#


def procesar_datos_produccion(nombre_archivo):
    """
    Busca el archivo en la carpeta 'datos' usando rutas absolutas
    para que funcione tanto en Notebooks como en Terminal.
    """
    # 1. Calculamos la ruta absoluta de forma dinámica
    base_path = os.path.dirname(os.path.abspath(__file__)) 
    ruta_completa = os.path.join(base_path, "..", "datos", nombre_archivo)
    
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
        print(f"❌ Error: No se encuentra el archivo en: {ruta_completa}")
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

#-----------------------------------------------------------------------------------------------------------------#
# Funcion para CATEGORIZAR POZOS
#-----------------------------------------------------------------------------------------------------------------#

def categorizar_pozos(df):
    # 1. Extraemos la columna para trabajar más cómodos
    eficiencia = df['eficiencia']
    
    # 2. Definimos las condiciones (Tu lógica está perfecta)
    condiciones = [
        (eficiencia >= 90),
        (eficiencia >= 70) & (eficiencia <= 89),
        (eficiencia < 70)
    ]

    categorias = ["Óptimo", "Monitoreo", "Crítico"]

    # 3. CREAMOS la nueva columna dentro del DataFrame
    df['categoria'] = np.select(condiciones, categorias, default="Sin Datos")
    
    # 4. Devolvemos el DataFrame completo con la nueva columna
    return df

#-----------------------------------------------------------------------------------------------------------------#
# Funcion para CALCULAR LA DISTANCIA NUMERICA DE FORMA VECTORIZADA
#-----------------------------------------------------------------------------------------------------------------#
def calcular_distancia_monitoreo(df):
    """
    Calcula cuánto le falta a un pozo 'Crítico' (< 70) para llegar a 'Monitoreo' (70).
    """
    valor_objetivo = 70
    
    # 1. Realizamos el cálculo vectorizado (Tu lógica original)
    distancia = valor_objetivo - df['eficiencia']
    
    # 2. Asignamos el resultado a una nueva columna
    # "Si es < 70, poné la distancia; si no, poné 0"
    df['gap_eficiencia'] = np.where(df['eficiencia'] < valor_objetivo, distancia, 0)
    
    return df


#-----------------------------------------------------------------------------------------------------------------#
# Funcion para CALCULAR LA PRODUCCION NETA DE PETROLEO
#-----------------------------------------------------------------------------------------------------------------#

def calcular_produccion_neta(df):
    """
    Calcula el petróleo neto. Si la columna 'water_cut' no existe, 
    asume 0% para no frenar el proceso, pero informa al usuario.
    """
    if 'water_cut' not in df.columns:
        print("⚠️ Advertencia: No se encontró columna 'water_cut'. Calculando con 0%.")
        df['water_cut'] = 0
    
    # Aseguramos que los valores sean numéricos
    df['water_cut'] = pd.to_numeric(df['water_cut'], errors='coerce').fillna(0)
    
    # Aplicamos la fórmula industrial
    df['prod_neta_petroleo'] = df['prod_real_bpd'] * (1 - (df['water_cut'] / 100))
    
    return df



if __name__ == "__main__":
    print("🧪 Iniciando prueba de laboratorio...")
    
    # 1. Cargamos el archivo (esto crea el DataFrame necesario)
    # Asegurate de que la ruta sea correcta para cuando corrés desde la carpeta raíz
    df_lab = procesar_datos_produccion("datos_campo.csv")
    
    if df_lab is not None:
        # 2. Ahora sí, usamos la nueva función de categorías
        df_lab = categorizar_pozos(df_lab)
        
        # # 3. Mostramos el resultado para verificar
        # print("✅ Resultado del procesamiento:")
        # print(df_lab[['pozo_id', 'eficiencia', 'categoria']].head())

        # 3. Calculamos Petróleo Neto
        # Simulamos un Water Cut variable para que la prueba sea real
        df_lab['water_cut'] = [10, 85, 5, 95, 0] # Inventamos datos para cada pozo
        df_lab = calcular_produccion_neta(df_lab)
        
        # 4. Mostramos el ranking final
        print("✅ Resultado del Análisis de Producción Neta:")
        columnas_interes = ['pozo_id', 'prod_real_bpd', 'water_cut', 'prod_neta_petroleo', 'categoria']
        print(df_lab[columnas_interes])
    else:
        print("❌ No se pudo cargar el archivo de prueba.")
    
    print("🏁 Prueba finalizada.")