# 📊 Temporal Minds

## Análisis del comportamiento de la TRM de Colombia (2016-2019)

Proyecto integrador de la asignatura **Análisis e Interpretación de Datos a través de Python**.

### 1. Descripción del proyecto

Este proyecto analiza el comportamiento histórico de la Tasa Representativa del Mercado (TRM) de Colombia durante el periodo comprendido entre el 4 de enero de 2016 y el 31 de diciembre de 2019.

Se estudia la relación de la TRM con tres variables internacionales: el precio del petróleo Brent, el índice del dólar estadounidense (DXY) y el índice de volatilidad financiera (VIX).

Para desarrollar el análisis se utilizan técnicas de series de tiempo, cadenas de Markov y simulación Monte Carlo. Los resultados se integran en una aplicación interactiva desarrollada con Streamlit.

### 2. Pregunta central

¿Cómo se comportó la TRM colombiana durante el periodo 2016-2019, qué relaciones presentó con las variables internacionales Brent, DXY y VIX, y qué patrones y escenarios posibles pueden identificarse mediante los modelos VAR, cadenas de Markov y simulación Monte Carlo?

### 3. Objetivo general

Analizar el comportamiento de la TRM colombiana durante el periodo 2016-2019 y su relación con las variables internacionales Brent, DXY y VIX, mediante la aplicación de modelos VAR, cadenas de Markov y simulación Monte Carlo, con el propósito de identificar relaciones dinámicas, patrones de comportamiento y posibles escenarios de evolución.

### 4. Datos utilizados

La base de datos contiene 1.042 registros diarios correspondientes al periodo 2016-2019.
### Fuentes de información

Los datos utilizados en el proyecto provienen de las siguientes entidades y plataformas:

- **TRM:** Banco de la República, a través de SUAMECA. Serie Tasa Representativa del Mercado (TRM), expresada en COP/USD.
- **Brent:** FRED / ALFRED, de la Reserva Federal de St. Louis. Serie DCOILBRENTEU, cuyo origen primario es la U.S. Energy Information Administration.
- **DXY:** Investing.com. Serie histórica *US Dollar Index Historical Data*, utilizando la columna Price (cierre). Enlace de consulta: https://www.investing.com/indices/usdollar-historical-data
- **VIX:** FRED, de la Reserva Federal de St. Louis. Serie VIXCLS, correspondiente al índice de volatilidad CBOE.

Las cuatro series corresponden al periodo comprendido entre el 4 de enero de 2016 y el 31 de diciembre de 2019. Las frecuencias y los tratamientos de datos faltantes se encuentran documentados en la ficha técnica y las hojas metodológicas de la base de datos.

**Nota:** los valores faltantes de Brent y VIX fueron tratados durante la preparación de la base de datos. La metodología y las cantidades se encuentran documentadas en el archivo Excel definitivo.

**Variables de estudio:**

- TRM (COP/USD): variable objetivo.
- Brent (USD/barril): precio internacional del petróleo.
- DXY (índice): indicador del comportamiento del dólar estadounidense.
- VIX (índice): indicador de volatilidad del mercado financiero.

El archivo de datos utilizado es:

`Base_datos_TRM_Brent_DXY_VIX_2016_2019_documentada.xlsx`

La metodología de preparación, las fuentes de información y el tratamiento de los datos se encuentran documentados en las hojas técnicas y metodológicas de este archivo.

### 5. Modelos implementados

**Modelo VAR(2)**

Permite estudiar las relaciones dinámicas entre la TRM y las variables internacionales Brent, DXY y VIX. También se evalúa su capacidad predictiva y se analizan sus resultados mediante pruebas estadísticas.

**Cadenas de Markov**

Permiten clasificar los rendimientos de la TRM en tres estados: bajo, intermedio y alto. Se estiman las probabilidades de permanencia y transición entre estos estados.

**Simulación Monte Carlo**

Genera 1.000 trayectorias posibles de la TRM durante un horizonte de 30 días, utilizando parámetros históricos de los rendimientos para explorar diferentes escenarios y analizar la incertidumbre.

### 6. Aplicación interactiva

Los resultados se presentan mediante una aplicación desarrollada en Streamlit que permite:

- Consultar la información general de la base de datos.
- Visualizar indicadores y estadísticas descriptivas.
- Explorar la evolución de las variables.
- Seleccionar periodos mediante un filtro de fechas para el análisis descriptivo.
- Consultar los resultados del modelo VAR.
- Explorar las probabilidades de transición de Markov.
- Visualizar los escenarios de Monte Carlo.

**Nota:** los resultados de los modelos fueron calculados utilizando información histórica de 2016-2019. No representan pronósticos actualizados para 2026. El filtro de fechas de la aplicación modifica el análisis descriptivo, no recalcula los modelos.

### 7. Estructura principal del proyecto

- `app.py`: aplicación principal de Streamlit.
- `modelo_var.py`: implementación del modelo VAR.
- `modelo_markov.py`: implementación de las cadenas de Markov.
- `modelo_montecarlo.py`: implementación de la simulación Monte Carlo.
- `requirements.txt`: dependencias necesarias para ejecutar el proyecto.
- `Base_datos_TRM_Brent_DXY_VIX_2016_2019_documentada.xlsx`: base de datos definitiva.
- Archivos Excel de resultados: contienen los resultados utilizados por la aplicación.

### 8. Instalación y ejecución

Se requiere tener Python instalado.

**Paso 1.** Crear y activar un entorno virtual.

En macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

**Paso 2.** Instalar las dependencias:

```bash
pip install -r requirements.txt
```

**Paso 3.** Ejecutar la aplicación:

```bash
streamlit run app.py
```

La aplicación se abrirá en el navegador web.

### 9. Consideraciones metodológicas

Los resultados dependen de los supuestos y las limitaciones de cada modelo.

- El VAR presenta limitaciones predictivas según el horizonte de evaluación y evidencia de no normalidad y efectos ARCH en sus residuos.
- Markov supone probabilidades de transición constantes durante el periodo analizado.
- Monte Carlo supone rendimientos independientes, normalmente distribuidos y con parámetros constantes.

Los tres modelos se estiman de manera independiente y proporcionan perspectivas complementarias del comportamiento histórico de la TRM.

---

**Equipo:** Temporal Minds

**Asignatura:** Análisis e Interpretación de Datos a través de Python.