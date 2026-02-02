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

#-----------------------------------------------------------------------------------------------------------------#
# Funcion para CALCULAR El Factor de Emulsión ($F_e$)
#-----------------------------------------------------------------------------------------------------------------#
# En la industria, la emulsión no es lineal. 
# Se vuelve más difícil de romper (requiere más químico) cuanto más agua hay y más baja es la temperatura

def calcular_factor_emulsion(water_cut, temp_c):
    """
    Calcula el Factor de Emulsión basado en condiciones de fondo.
    A mayor WC y menor Temp, el factor aumenta (más difícil de separar).
    """
    # Una fórmula empírica para simular la viscosidad de la emulsión
    factor = (water_cut / 100) * (100 / max(temp_c, 1))
    return round(factor, 4)

def estimar_costo_quimico(water_cut, temp_c, volumen_total):
    """
    Estima el costo en USD de desemulsionante necesario.
    """
    fe = calcular_factor_emulsion(water_cut, temp_c)
    # Supongamos 0.5 USD por unidad de factor por barril
    costo = fe * volumen_total * 0.5 
    return round(costo, 2)



def calcular_metricas_emulsion(df):
    """
    Calcula el Factor de Emulsión y el costo de tratamiento.
    Lógica: A menor temperatura y mayor Water Cut, la emulsión es más 'apretada' 
    y requiere más inversión en desemulsionantes.
    """
    # 1. Factor de Emulsión (F_e): Escala de 0 a 10
    # Usamos una constante de viscosidad simulada
    df['factor_emulsion'] = (df['water_cut'] / 100) * (80 / df['temp_c'])
    
    # 2. Costo Químico (USD): 
    # Supongamos que el químico cuesta 1.2 USD por unidad de factor por barril total
    df['costo_quimico_usd'] = df['factor_emulsion'] * df['q_petroleo'] * 1.2
    
    return df


#-----------------------------------------------------------------------------------------------------------------#
# Funcion para CALCULAR las Curvas de Declinación de Arps
#-----------------------------------------------------------------------------------------------------------------#

def predecir_declinacion_arps(q_inicial, tasa_d, tiempo_dias):
    """
    Calcula la producción futura usando Declinación Exponencial (Arps).
    q_inicial: Producción actual (bbl/d)
    tasa_d: Tasa de declinación diaria (ej: 0.003)
    tiempo_dias: Días a proyectar hacia adelante
    """
    # Fórmula: q(t) = qi * e^(-D*t)
    produccion_proyectada = q_inicial * np.exp(-tasa_d * tiempo_dias)
    return round(produccion_proyectada, 2)


#-----------------------------------------------------------------------------------------------------------------#
# Funcion para CALCULAR LIMITE ECONÓMICO
#-----------------------------------------------------------------------------------------------------------------#

def calcular_limite_economico(produccion_proyectada, costo_op_diario, precio_barril=70):
    """
    Determina en qué punto la ganancia por petróleo ya no cubre los costos.
    """
    dias = len(produccion_proyectada)
    dia_limite = None
    
    for t in range(dias):
        ingreso = produccion_proyectada[t] * precio_barril
        if ingreso <= costo_op_diario:
            dia_limite = t
            break
            
    return dia_limite



# if __name__ == "__main__":
#     print("🧪 Iniciando prueba de laboratorio INTEGRADA...")
    
#     # 1. Carga (Lo que ya tenías)
#     df_lab = procesar_datos_produccion("datos_campo.csv")
    
#     if df_lab is not None:
#         # 2. Lógica de ayer (Categorías y Neto)
#         df_lab = categorizar_pozos(df_lab)
#         df_lab['water_cut'] = [10, 85, 5, 95, 0] 
#         df_lab = calcular_produccion_neta(df_lab)
        
#         # --- 🆕 LO NUEVO DE HOY: Emulsión y Temperatura ---
#         print("🛠️ Calculando Factor de Emulsión...")
#         # Simulamos temperatura para la prueba (60°C es estándar en tratamiento)
#         df_lab['temp_c'] = [65, 55, 70, 45, 60] 
        
#         # Invocamos la función de hoy
#         df_lab = calcular_metricas_emulsion(df_lab)
        
#         # 4. Mostramos el ranking final con TODO
#         print("✅ Resultado del Análisis Completo:")
#         columnas_finales = [
#             'pozo_id', 'prod_neta_petroleo', 'categoria', 
#             'factor_emulsion', 'costo_quimico_usd'
#         ]
#         print(df_lab[columnas_finales])
#     else:
#         print("❌ No se pudo cargar el archivo de prueba.")
    
#     print("🏁 Prueba finalizada.")

# ... (tus funciones anteriores: calcular_factor_emulsion, etc.)


if __name__ == "__main__":
    import pandas as pd
    # Creamos un pozo de prueba: 500 bbl, 30% agua, 60 grados
    test_data = {
        'pozo_id': ['TEST-01'],
        'q_petroleo': [500],
        'water_cut': [30],
        'temp_c': [60]
    }
    df_test = pd.DataFrame(test_data)
    
    # Ejecutamos la lógica
    resultado = calcular_metricas_emulsion(df_test)
    
    print("🧪 PRUEBA DE LABORATORIO:")
    print(resultado[['pozo_id', 'factor_emulsion', 'costo_quimico_usd']])   