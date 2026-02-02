import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def fabricar_dataset_historico(n_dias=90, ruta_salida='../datos/produccion_historica.csv'):
    """
    Simula datos reales de Vaca Muerta para entrenamiento de modelos.
    """
    # Aseguramos que la carpeta datos exista
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    
    pozos = ['AN-001', 'AN-002', 'AN-003', 'AN-004', 'AN-005']
    datos = []
    fecha_inicio = datetime.now() - timedelta(days=n_dias)

    for pozo in pozos:
        q_inicial = np.random.uniform(400, 900)
        declinacion = np.random.uniform(0.002, 0.006)
        
        for i in range(n_dias):
            fecha = fecha_inicio + timedelta(days=i)
            # Declinación Exponencial (Arps simplificado)
            q_actual = q_inicial * np.exp(-declinacion * i)
            # El Water Cut sube a medida que el pozo envejece
            wc = min(98, 15 + (i * 0.25) + np.random.normal(0, 3))
            
            datos.append({
                'fecha': fecha.strftime('%Y-%m-%d'),
                'pozo_id': pozo,
                'q_petroleo': round(q_actual, 2),
                'water_cut': round(wc, 2),
                'presion_psi': round(1500 - (i * 3) + np.random.normal(0, 15), 2),
                'temp_c': round(70 + np.random.normal(0, 4), 2)
            })
            
    df = pd.DataFrame(datos)
    df.to_csv(ruta_salida, index=False)
    return ruta_salida