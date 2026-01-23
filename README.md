# 🛢️ Monitoreo de Eficiencia y Lucro Cesante - Cuenca Neuquina

## 📋 Descripción del Proyecto
Este proyecto desarrolla un sistema de análisis de datos para la industria del **Oil & Gas**, enfocado en la optimización de la producción en **Vaca Muerta**. El algoritmo procesa datos de sensores de 100 pozos petroleros para identificar desviaciones críticas entre la producción teórica y la real.

A diferencia de un análisis académico, este sistema está orientado a la **toma de decisiones gerenciales**, priorizando las intervenciones de campo según el impacto económico (USD) y no solo por variables técnicas aisladas.

## 🛠️ Funcionalidades Técnicas
* **Data Cleaning:** Implementación de `pd.to_numeric` con manejo de errores para datos de campo inconsistentes.
* **Validación Matemática:** Gestión de indeterminaciones (división por cero) en pozos cerrados mediante reemplazo de valores por `NaN`.
* **Análisis de Eficiencia:** Cálculo automatizado del porcentaje de rendimiento por activo.
* **Cuantificación de Lucro Cesante:** Cálculo de barriles perdidos y su conversión a dólares (USD) basada en el precio del Brent.
* **Priorización Operativa:** Filtrado de pozos críticos mediante `.query()` y ordenamiento jerárquico de pérdidas.

## 🚀 Tecnologías Utilizadas
* **Python 3.x**
* **Pandas:** Manipulación y análisis de estructuras de datos.
* **Numpy:** Operaciones matemáticas vectorizadas.
* **Git:** Control de versiones con convenciones de *Conventional Commits*.

## 📊 Ejemplo de Salida del Reporte
```text
--- REPORTE DE PRIORIDAD DE INTERVENCIÓN ---
Analista: Silvio Rojas
Monitoreo: 100 Pozos activos.

TOP 5 POZOS CRÍTICOS (Mayor pérdida económica):
1. AN-X042 - Pérdida: 720.45 bpd - Impacto: $54,033.75 USD
2. AN-X015 - Pérdida: 685.20 bpd - Impacto: $51,390.00 USD
...
⚠️ Pérdida total acumulada por ineficiencia: $245,670.30 USD
