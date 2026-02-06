# 🛢️ Proyecto Monitoreo de Eficiencia 2026: Sistema de Gestión de Activos Críticos y Lucro Cesante

![Vaca Muerta](https://img.shields.io/badge/Basin-Vaca%20Muerta-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-gold?style=for-the-badge&logo=python)
![Industry](https://img.shields.io/badge/Industry-Oil%20%26%20Gas-green?style=for-the-badge)

### **IT/OT Operations Specialist | Data Analytics for Oil & Gas**
**Desarrollado por: Silvio Jonathan Rojas**

---

## 📌 Visión General
Este sistema es una solución integral para el monitoreo y análisis de viabilidad económica de pozos en la **Cuenca Neuquina - Vaca Muerta**. 
El algoritmo procesa datos de sensores de 100 pozos petroleros para identificar desviaciones críticas entre la producción teórica y la real. 
La herramienta integra modelos matemáticos de declinación de producción con variables financieras de mercado en tiempo real, permitiendo predecir el **Límite Económico (Qel)** y optimizar el EBITDA de los activos.
A diferencia de un análisis académico, este sistema está orientado a la **toma de decisiones gerenciales**, priorizando las intervenciones de campo según el impacto económico (USD) y no solo por variables técnicas aisladas.

---

## 🌐 Demo En Vivo
Puedes interactuar con el Dashboard en tiempo real aquí:
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://controldeoperaciones.streamlit.app/)

---


## 🛠️ Capacidades del Sistema

* **Análisis Masivo de Datos:** Procesamiento y sanitización de 100 pozos con capas de resiliencia para manejar inconsistencias de sensores.
* **Modelado Arps Dinámico:** Proyección de curvas de declinación exponencial para cálculo de reservas y vida útil del pozo.
* **Motor de Sensibilidad Brent:** Dashboards interactivos que recalculan la rentabilidad del yacimiento ante la volatilidad del precio internacional del crudo.
* **Costo de Emulsión Variable:** Algoritmo que estima el impacto del OPEX químico basado en el *Water Cut* y la temperatura de fondo.
* **Generación de Reportes PDF One-Paper:** Exportación automatizada de informes ejecutivos de una sola página, diseñados para comunicación técnica directa y toma de decisiones inmediata.


## 📊 Arquitectura de Ingeniería (Lógica de Negocio)

El núcleo del software aplica fórmulas estandarizadas de la industria:

1.  **Punto de Equilibrio (Qel):**
    $$Qel = \frac{OPEX_{diario}}{Precio_{Brent} \times (1 - Regalías)}$$

2.  **Factor de Emulsión ($F_e$):**
    Cálculo de la "dureza" de la emulsión para estimar costos de desemulsionantes:
    $$F_e = \frac{WC}{100} \times \frac{K_{viscosidad}}{Temp_{°C}}$$

## 🚀 Stack Tecnológico
* **Backend:** Python 3.12 (Pandas para ETL, NumPy para modelado vectorial).
* **Frontend:** Streamlit para despliegue de Dashboards de alta disponibilidad.
* **Visualización:** Plotly Graph Objects para gráficos dinámicos de ingeniería.
* **Reporting:** FPDF2 e IO para generación de documentos en tiempo real.

---

## 📂 Estructura del Repositorio
* `main.py`: Portal de acceso y métricas consolidadas del área.
* `/pages`: Módulos de Vista Global (EBITDA) y Detalle por Pozo (Forecast).
* `/src`: Motores de lógica petrolera y generadores de reportes.
* `/datos`: Datasets históricos y operativos simulados.

---

## 💡 Propuesta de Valor
Transformo volúmenes de datos críticos en tableros de control ejecutivos que permiten predecir el límite económico y optimizar la vida útil de los pozos en Vaca Muerta, reduciendo el riesgo operativo y maximizando el margen neto por barril.

---

### 📫 Contacto
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/silviojonrojas)
**Silvio Jonathan Rojas** - Especialista en IT/OT & Asset Integrity.
