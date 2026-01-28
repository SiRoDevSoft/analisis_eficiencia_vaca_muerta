import pandas as pd
import numpy as np
import os

def generar_yacimiento_anelo(cantidad_pozos=50):
    np.random.seed(42) # Para que siempre nos de los mismos "aleatorios"
    
    # 1. Creamos IDs de pozos (AN-001, AN-002, etc.)
    pozos = [f"AN-{str(i).zfill(3)}" for i in range(1, cantidad_pozos + 1)]
    
    # 2. Generamos Producción Teórica (Capacidad instalada del pozo)
    prod_teorica = np.random.randint(400, 1200, size=cantidad_pozos)
    
    # 3. Generamos Producción Real (con algunas fallas)
    # Multiplicamos la teórica por un factor de eficiencia aleatorio entre 0.1 y 1.0
    eficiencia_azar = np.random.uniform(0.1, 1.0, size=cantidad_pozos)
    prod_real = prod_teorica * eficiencia_azar
    
    # 4. Generamos Water Cut (Porcentaje de agua)
    water_cut = np.random.uniform(5, 95, size=cantidad_pozos)
    
    # 5. Creamos el DataFrame
    df_masivo = pd.DataFrame({
        'pozo_id': pozos,
        'prod_teorica_bpd': prod_teorica,
        'prod_real_bpd': prod_real,
        'water_cut': water_cut
    })
    
    # Inyectamos algunos errores para probar tu robustez (Outliers)
    df_masivo.loc[5, 'prod_real_bpd'] = -10  # Un sensor roto
    df_masivo.loc[10, 'prod_real_bpd'] = np.nan  # Un dato faltante
    
    # Guardamos en la carpeta de datos
    ruta = os.path.join("datos", "datos_campo_masivos.csv")
    df_masivo.to_csv(ruta, index=False)
    print(f"✅ Se han generado {cantidad_pozos} pozos en {ruta}")

if __name__ == "__main__":
    generar_yacimiento_anelo(100) # ¡Vamos por 100 pozos!