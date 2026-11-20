
# ==========================================
# PROYECTO INTEGRADOR - TEMPORAL MINDS
# Aplicación desarrollada con Streamlit
# ==========================================

import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. CONFIGURACIÓN DE LA APLICACIÓN
# ==========================================

st.set_page_config(
    page_title="Temporal Minds",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. TÍTULO Y PRESENTACIÓN
# ==========================================

st.title("📊 Temporal Minds")

st.header(
    "Análisis del comportamiento de la TRM de Colombia"
)

st.write("""
Proyecto integrador de la asignatura
Análisis e Interpretación de Datos a través de Python.

Nuestro objetivo es estudiar el comportamiento de la
Tasa Representativa del Mercado (TRM) de Colombia
durante el periodo 2016-2019.
""")

st.divider()

# ==========================================
# 3. UBICACIÓN DEL ARCHIVO EXCEL
# ==========================================

# Identificar automáticamente la carpeta
# donde se encuentra este archivo app.py.

carpeta_proyecto = Path(__file__).parent

# Nombre definitivo de nuestra base de datos.

archivo = (
    carpeta_proyecto /
    "Base_datos_TRM_Brent_DXY_VIX_2016_2019_documentada.xlsx"
)
# ==========================================
# 4. FUNCIÓN PARA CARGAR LOS DATOS
# ==========================================

@st.cache_data
def cargar_datos(ruta):

    datos = pd.read_excel(
        ruta,
        sheet_name="Base_diaria"
    )

    datos["Fecha"] = pd.to_datetime(datos["Fecha"])

    datos = datos.sort_values("Fecha")

    return datos


# ==========================================
# 5. VERIFICAR Y CARGAR LA BASE DE DATOS
# ==========================================

if archivo.exists():

    try:

        df = cargar_datos(str(archivo))

        st.success(
            "¡Base de datos cargada correctamente!"
        )

        # Comprobar las columnas necesarias

        columnas_necesarias = [
            "Fecha",
            "TRM (COP/USD)",
            "Brent (USD/barril)",
            "DXY (índice)",
            "VIX (índice)"
        ]

        faltantes = [
            columna
            for columna in columnas_necesarias
            if columna not in df.columns
        ]

        if faltantes:

            st.error(
                f"Faltan estas columnas en el Excel: {faltantes}"
            )

            st.stop()

        # ==========================================
        # FILTRO DE FECHAS
        # ==========================================

        st.sidebar.header("Filtros de análisis")

        st.sidebar.write(
            "Selecciona el periodo que deseas consultar."
        )

        fecha_inicio, fecha_fin = st.sidebar.date_input(
            "Periodo de análisis",
            value=(
                df["Fecha"].min().date(),
                df["Fecha"].max().date()
            ),
            min_value=df["Fecha"].min().date(),
            max_value=df["Fecha"].max().date()
        )

        # Aplicar el filtro a los datos

        df = df[
            (df["Fecha"].dt.date >= fecha_inicio) &
            (df["Fecha"].dt.date <= fecha_fin)
        ]

        st.sidebar.success(
            f"Registros seleccionados: {len(df)}"
        )


        # ==========================================
        # 6. INFORMACIÓN GENERAL DE LOS DATOS
        # ==========================================

        st.subheader("Información general de la base de datos")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total de registros",
            len(df)
        )

        col2.metric(
            "Fecha inicial",
            df["Fecha"].min().strftime("%d/%m/%Y")
        )

        col3.metric(
            "Fecha final",
            df["Fecha"].max().strftime("%d/%m/%Y")
        )

        st.divider()

        # ==========================================
        # 7. PRESENTACIÓN DE LAS VARIABLES
        # ==========================================

        st.subheader("Variables de estudio")

        col1, col2 = st.columns(2)

        with col1:

            st.write("**Variable objetivo**")
            st.write("TRM (COP/USD)")

            st.write("**Variables explicativas**")
            st.write("- Brent (USD/barril)")
            st.write("- DXY (índice)")
            st.write("- VIX (índice)")

        with col2:

            st.write("**Frecuencia:** diaria")
            st.write("**Periodo:** 2016-2019")
            st.write("**Equipo:** Temporal Minds")

        st.divider()

        # ==========================================
        # 8. TABLA DE DATOS
        # ==========================================

        st.subheader("Base de datos diaria")

        st.write(
            "A continuación se presentan los registros "
            "utilizados en el análisis."
        )

        st.dataframe(
    df,
    width="stretch"
)
        
        # ==========================================
        # DESCARGAR DATOS DEL PERIODO SELECCIONADO
        # ==========================================

        st.subheader("Descargar datos")

        archivo_excel = io.BytesIO()

        with pd.ExcelWriter(archivo_excel, engine="openpyxl") as writer:
            df.to_excel(
                writer,
                index=False,
                sheet_name="Datos_filtrados"
            )

        st.download_button(
            label="Descargar datos en Excel",
            data=archivo_excel.getvalue(),
            file_name="Datos_TRM_periodo_seleccionado.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

       
        # ==========================================
        # INDICADORES PRINCIPALES DE LA TRM
        # ==========================================

        st.subheader("Indicadores principales de la TRM")

        trm_inicial = df["TRM (COP/USD)"].iloc[0]
        trm_final = df["TRM (COP/USD)"].iloc[-1]

        trm_promedio = df["TRM (COP/USD)"].mean()
        trm_minima = df["TRM (COP/USD)"].min()
        trm_maxima = df["TRM (COP/USD)"].max()

        variacion_trm = (
            (trm_final / trm_inicial) - 1
        ) * 100

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "TRM promedio",
            f"${trm_promedio:,.2f}"
        )

        col2.metric(
            "TRM mínima",
            f"${trm_minima:,.2f}"
        )

        col3.metric(
            "TRM máxima",
            f"${trm_maxima:,.2f}"
        )

        col4.metric(
            "Variación del periodo",
            f"{variacion_trm:.2f}%"
        )
 

        # ==========================================
        # 9. GRÁFICOS DE LAS CUATRO VARIABLES
        # ==========================================

        st.subheader("Evolución de las variables")

        variables = [
            "TRM (COP/USD)",
            "Brent (USD/barril)",
            "DXY (índice)",
            "VIX (índice)"
        ]

        for variable in variables:

            st.markdown(f"### {variable}")

            fig, ax = plt.subplots(figsize=(12, 4))

            ax.plot(
                df["Fecha"],
                df[variable]
            )

            ax.set_title(
                f"Evolución diaria de {variable}"
            )

            ax.set_xlabel("Fecha")

            ax.set_ylabel(variable)

            ax.grid(True)

            fig.tight_layout()

            st.pyplot(fig)

            plt.close(fig)

        st.divider()


        # ==========================================
        # 9. RESUMEN ESTADÍSTICO
        # ==========================================

        st.subheader("Resumen estadístico de las variables")

        st.write(
            "Estadísticas descriptivas de las variables "
            "durante el periodo seleccionado."
        )

        variables = [
            "TRM (COP/USD)",
            "Brent (USD/barril)",
            "DXY (índice)",
            "VIX (índice)"
        ]

        resumen = df[variables].agg(
            ["mean", "median", "min", "max", "std"]
        ).T

        resumen = resumen.rename(columns={
            "mean": "Media",
            "median": "Mediana",
            "min": "Mínimo",
            "max": "Máximo",
            "std": "Desviación estándar"
        })

        st.dataframe(resumen, width="stretch")


        # ==========================================
        # 10. SECCIONES DE LOS TRES MODELOS
        # ==========================================

        st.subheader("Métodos de análisis del proyecto")

        tab1, tab2, tab3 = st.tabs([
            "Modelo VAR",
            "Cadenas de Markov",
            "Monte Carlo"
        ])

        with tab1:

            st.write("### Modelo VAR")

            st.write("""
            **Objetivo del modelo**

            Analizar las relaciones dinámicas entre la
            TRM colombiana y las variables internacionales
            Brent, DXY y VIX.
            """)

            st.write("**Variables del modelo**")

            st.markdown("""
            - TRM (COP/USD)
            - Brent (USD/barril)
            - DXY (índice)
            - VIX (índice)
            """)

            st.write("**Análisis que se presentará**")

            st.markdown("""
            - Relaciones dinámicas entre las variables.
            - Selección del número de rezagos.
            - Resultados del modelo VAR.
            - Pronósticos de la TRM.
            """)

            archivo_var = carpeta_proyecto / "Predicciones_Futuras_VAR_TRM.xlsx"

            if archivo_var.exists():

                predicciones_var = pd.read_excel(archivo_var)

                st.success("Resultados del modelo VAR cargados correctamente.")

                st.write("### Pronóstico futuro de la TRM")

                st.write(
                    "El modelo VAR(2) genera una proyección de "
                    "30 días a partir del último dato disponible "
                    "en la base histórica."
                )

                st.info(
                    "Nota metodológica: la base histórica utilizada "
                    "comprende el periodo 2016-2019 y finaliza el "
                    "31 de diciembre de 2019. Por tanto, esta "
                    "proyección corresponde a enero y febrero de 2020 "
                    "y no representa un pronóstico actualizado para 2026."
                )

                st.write("### Interpretación del pronóstico")

                st.markdown("""
                El modelo VAR(2) utiliza el comportamiento pasado de
                la TRM, el Brent, el DXY y el VIX para estimar la
                evolución futura de las variables del sistema.

                La proyección muestra una trayectoria estimada de la
                TRM durante los siguientes 30 días del horizonte
                analizado. Estos valores son estimaciones del modelo,
                no valores observados ni resultados garantizados.
                """)

                st.dataframe(
                    predicciones_var[["Fecha", "Dia", "TRM_predicha"]],
                    width="stretch"
                )
                st.write("### Gráfico de predicción futura de la TRM")

                fig_var, ax_var = plt.subplots(figsize=(12, 5))

                ax_var.plot(
                    predicciones_var["Fecha"],
                    predicciones_var["TRM_predicha"],
                    marker="o",
                    label="TRM proyectada"
                )

                ax_var.set_title("Predicción de la TRM mediante VAR(2)")
                ax_var.set_xlabel("Fecha")
                ax_var.set_ylabel("TRM (COP/USD)")
                ax_var.legend()
                ax_var.grid(True)

                fig_var.tight_layout()

                st.pyplot(fig_var)

                plt.close(fig_var)
                st.divider()

                st.write("### Evaluación de la capacidad predictiva")

                archivo_evaluacion_var = (
                    carpeta_proyecto / "Evaluacion_VAR_TRM.xlsx"
                )

                if archivo_evaluacion_var.exists():

                    evaluacion_var = pd.read_excel(
                        archivo_evaluacion_var,
                        index_col=0
                    )

                    st.write("""
                    Se comparan los errores del modelo VAR(2)
                    con los de un modelo de referencia que supone
                    un cambio cero en el rendimiento de la TRM.
                    """)

                    st.dataframe(
                        evaluacion_var,
                        width="stretch"
                    )

                    st.caption("""
                    MAE: error absoluto medio.
                    RMSE: raíz del error cuadrático medio.
                    En ambas métricas, valores menores indican
                    un menor error de pronóstico.
                    """)

                else:

                    st.warning(
                        "No se encontró el archivo de evaluación del VAR."
                    )

            else:

                st.error("No se encontró el archivo de predicciones VAR.")

        with tab2:

            st.write("### Cadenas de Markov")

            st.write("""
            **Objetivo del modelo**

            Analizar los posibles estados de comportamiento
            de la TRM colombiana y las probabilidades de
            transición entre dichos estados.
            """)

            st.write("**Elementos del modelo**")

            st.markdown("""
            - Definición de los estados de la TRM.
            - Matriz de transición.
            - Probabilidades de permanencia.
            - Probabilidades de cambio de estado.
            """)

            st.write("**Análisis que se presentará**")

            st.markdown("""
            - Clasificación de los estados de la TRM.
            - Construcción de la matriz de transición.
            - Análisis de las probabilidades.
            - Interpretación de los resultados.
            """)

            archivo_markov = carpeta_proyecto / "Resultados_Markov_TRM.xlsx"

            if archivo_markov.exists():

                distribucion = pd.read_excel(
                    archivo_markov,
                    sheet_name="Distribucion"
                )

                matriz_markov = pd.read_excel(
                    archivo_markov,
                    sheet_name="Matriz_Markov"
                )

                frecuencias = pd.read_excel(
                    archivo_markov,
                    sheet_name="Frecuencias"
                )

                proyecciones = pd.read_excel(
                    archivo_markov,
                    sheet_name="Proyecciones"
                )

                st.success("Resultados de Markov cargados correctamente.")
                st.info(
                    "Nota metodológica: los estados bajo, intermedio "
                    "y alto se construyeron a partir de los rendimientos "
                    "porcentuales diarios de la TRM, no de su valor en pesos."
                )

                st.write("### ¿Cómo se interpretan los estados?")

                st.markdown("""
                Para clasificar el comportamiento diario de la TRM se
                utilizaron dos puntos de corte calculados mediante
                cuantiles de la distribución histórica:

                - **Rendimiento bajo:** variaciones iguales o inferiores
                  a -0,2425 %.
                - **Rendimiento intermedio:** variaciones superiores a
                  -0,2425 % e iguales o inferiores a 0,2315 %.
                - **Rendimiento alto:** variaciones superiores a 0,2315 %.

                Esta clasificación permite estudiar cómo cambia el
                comportamiento diario de la TRM entre las tres categorías.
                """)

                st.write("### ¿Qué representa la matriz de transición?")

                st.markdown("""
                La matriz muestra la probabilidad de pasar de un estado
                actual a otro en el siguiente periodo.

                Cada fila representa el estado de origen y cada columna
                el estado al que puede pasar la TRM. La diagonal principal
                representa la probabilidad de permanecer en el mismo estado.
                """)

                st.write("### Distribución de los estados")

                st.dataframe(
                    distribucion,
                    width="stretch"
                )
                st.markdown("""
                **Interpretación de las proyecciones**

                Las proyecciones muestran cómo evolucionan las
                probabilidades de los tres estados a diferentes
                horizontes de tiempo.

                - A un día, las probabilidades dependen del último
                  estado observado de la TRM.
                - A cinco días, las probabilidades comienzan a
                  aproximarse a una distribución más equilibrada.
                - A diez y veinte días, las probabilidades se
                  estabilizan alrededor de un tercio para cada estado.

                Esto indica que, a medida que aumenta el horizonte,
                la distribución proyectada tiende a perder la
                influencia del último estado observado y se aproxima
                a una distribución de largo plazo.

                Estas cifras representan probabilidades de estados,
                no valores futuros de la TRM en pesos.
                """)

                st.info(
                    "La proyección de Markov se basa en las transiciones "
                    "históricas observadas entre 2016 y 2019. No constituye "
                    "una predicción actualizada de la TRM para 2026."
                )
                st.markdown("""
                **Interpretación de la matriz**

                Los resultados muestran que:

                - Cuando la TRM se encuentra en el estado bajo,
                  tiene una probabilidad aproximada del 39,07 %
                  de permanecer en ese estado.
                - Cuando se encuentra en el estado intermedio,
                  tiene una probabilidad del 36,73 % de permanecer.
                - Cuando se encuentra en el estado alto,
                  tiene una probabilidad del 40,40 % de permanecer.

                Estas probabilidades indican que existe cierta
                persistencia en los estados, aunque también hay
                posibilidades de transición hacia las otras categorías.
                """)

                st.write("### Matriz de probabilidades de transición")

                matriz_markov = matriz_markov.rename(
                    columns={"row_0": "Estado de origen"}
                ).set_index("Estado de origen")

                st.dataframe(
                    matriz_markov,
                    width="stretch"
                )

                st.write("### Frecuencias de transición")

                frecuencias = frecuencias.rename(
                    columns={"row_0": "Estado de origen"}
                ).set_index("Estado de origen")

                st.dataframe(
                    frecuencias,
                    width="stretch"
                )
                st.write("#### Gráfico de frecuencias de transición")

                st.bar_chart(
                    frecuencias,
                    x_label="Estado de origen",
                    y_label="Número de transiciones"
                )

                st.write("### Proyecciones de los estados")

                st.dataframe(
                    proyecciones,
                    width="stretch"
                )
                st.write("#### Gráfico de proyecciones de los estados")

                st.line_chart(
                    proyecciones,
                    x="Horizonte (días)",
                    y=[
                        "Rendimiento bajo",
                        "Rendimiento intermedio",
                        "Rendimiento alto"
                    ],
                    x_label="Horizonte (días)",
                    y_label="Probabilidad"
                )

            else:

                st.error("No se encontró el archivo de resultados de Markov.")

        with tab3:

            st.write("### Simulación de Monte Carlo")

            st.write("""
            **Objetivo del modelo**

            Simular posibles escenarios futuros del
            comportamiento de la TRM colombiana mediante
            múltiples trayectorias aleatorias.
            """)

            st.write("**Elementos de la simulación**")

            st.markdown("""
            - Parámetros del modelo.
            - Generación de escenarios aleatorios.
            - Número de simulaciones.
            - Trayectorias posibles de la TRM.
            """)

            st.write("**Análisis que se presentará**")

            st.markdown("""
            - Distribución de los escenarios simulados.
            - Comportamiento esperado de la TRM.
            - Escenarios posibles.
            - Interpretación de la incertidumbre.
            """)

            archivo_montecarlo = carpeta_proyecto / "Resultados_MonteCarlo_TRM.xlsx"

            if archivo_montecarlo.exists():

                escenarios_mc = pd.read_excel(
                    archivo_montecarlo,
                    sheet_name="Escenarios"
                )

                st.success("Resultados de Monte Carlo cargados correctamente.")

                st.write("### Escenarios futuros de la TRM")

                st.write("""
                La simulación Monte Carlo genera 1.000 trayectorias
                posibles para analizar la incertidumbre de la TRM
                durante un horizonte de 30 días.
                """)

                st.info(
                    "Nota metodológica: la simulación utiliza "
                    "información histórica de 2016 a 2019 y parte "
                    "del último valor observado de la TRM al cierre "
                    "de 2019. Por tanto, no representa un pronóstico "
                    "actualizado para 2026."
                )

                st.write("### ¿Cómo funciona la simulación?")

                st.markdown("""
                El modelo genera múltiples trayectorias posibles
                de la TRM mediante rendimientos aleatorios.

                Para ello utiliza:

                - **1.000 simulaciones:** cada una representa una
                  posible trayectoria.
                - **Horizonte de 30 días:** periodo durante el cual
                  se proyectan las trayectorias.
                - **Media histórica:** representa el rendimiento
                  promedio utilizado en la simulación.
                - **Desviación estándar histórica:** representa
                  la variabilidad de los rendimientos.

                El modelo supone que los rendimientos siguen una
                distribución normal y son independientes entre
                periodos, con media y desviación estándar constantes.
                Estos son supuestos de simulación, no condiciones
                que necesariamente se cumplan en el mercado.
                """)

                
                st.markdown("""
                ### Interpretación de los escenarios

                Los resultados se presentan mediante tres percentiles:

                - **P5 (escenario bajo):** representa el valor por
                  debajo del cual se encuentra el 5 % de las
                  trayectorias simuladas.
                - **P50 (escenario central):** corresponde a la
                  mediana; la mitad de las trayectorias queda por
                  debajo de este valor y la otra mitad por encima.
                - **P95 (escenario alto):** representa el valor por
                  debajo del cual se encuentra el 95 % de las
                  trayectorias simuladas.

                En conjunto, P5 y P95 permiten observar un intervalo
                central que contiene aproximadamente el 90 % de los
                resultados simulados.

                Estos escenarios permiten analizar la incertidumbre
                y la dispersión de los posibles valores de la TRM.
                No representan límites garantizados ni predicciones
                exactas.
                """)

                st.write("### Gráfico de escenarios simulados")

                fig_mc, ax_mc = plt.subplots(figsize=(12, 5))

                ax_mc.plot(
                    escenarios_mc["Dia"],
                    escenarios_mc["Media_TRM"],
                    label="Media simulada"
                )

                ax_mc.plot(
                    escenarios_mc["Dia"],
                    escenarios_mc["Escenario_bajo_P5"],
                    label="Escenario bajo (P5)"
                )

                ax_mc.plot(
                    escenarios_mc["Dia"],
                    escenarios_mc["Escenario_central_P50"],
                    label="Escenario central (P50)"
                )

                ax_mc.plot(
                    escenarios_mc["Dia"],
                    escenarios_mc["Escenario_alto_P95"],
                    label="Escenario alto (P95)"
                )

                ax_mc.set_title("Simulación Monte Carlo de la TRM")
                ax_mc.set_xlabel("Días de proyección")
                ax_mc.set_ylabel("TRM (COP/USD)")
                ax_mc.legend()
                ax_mc.grid(True)

                fig_mc.tight_layout()

                st.pyplot(fig_mc)
                st.write("### Tabla de resultados de Monte Carlo")

                st.dataframe(
                    escenarios_mc,
                    width="stretch"
                )

                plt.close(fig_mc)

            else:

                st.error("No se encontró el archivo de resultados de Monte Carlo.")

        # ==========================================
                # 11. CONCLUSIONES INTEGRADAS
        # ==========================================

        st.header("Conclusiones integradas")

        st.write("""
        El análisis del comportamiento de la TRM colombiana
        mediante los modelos VAR, cadenas de Markov y simulación
        Monte Carlo permite estudiar diferentes aspectos de
        su comportamiento histórico.
        """)

        st.subheader("Principales aportes de los modelos")

        st.markdown("""
               **1. Modelo VAR(2)**

        Permite analizar las relaciones dinámicas entre la TRM
        colombiana y las variables internacionales Brent, DXY
        y VIX. La prueba de causalidad de Granger indica que
        estas variables aportan información predictiva
        estadísticamente significativa sobre la TRM dentro
        del modelo. Sin embargo, la evaluación del pronóstico
        muestra resultados diferentes según el horizonte:
        el VAR(2) supera al modelo de referencia de cambio
        cero en las predicciones a un paso, pero no presenta
        una mejora en la evaluación de varios pasos. Por tanto,
        su capacidad predictiva debe interpretarse considerando
        estas limitaciones.

        **2. Cadenas de Markov**

        Permiten analizar las probabilidades de permanencia y transición entre los estados de rendimiento bajo, intermedio y alto de la TRM. Los resultados muestran que la probabilidad de permanecer en el mismo estado se encuentra aproximadamente entre el 36,73 % y el 40,40 %. Además, las proyecciones indican que las probabilidades de los tres estados tienden a estabilizarse a partir de los 10 días, acercándose a una distribución relativamente equilibrada.

        **3. Simulación Monte Carlo**

        Permite explorar la incertidumbre del comportamiento de la TRM mediante 1.000 trayectorias simuladas durante un horizonte de 30 días. Al finalizar la simulación, la media de los escenarios es de aproximadamente $3.283,29 COP/USD, mientras que los percentiles P5, P50 y P95 son $3.070,39, $3.281,76 y $3.502,00 COP/USD, respectivamente. Estos resultados muestran la dispersión de los escenarios posibles y dependen de los supuestos estadísticos establecidos para la simulación.
                """)
        st.subheader("Interpretación conjunta")
        st.write("""
        Los tres modelos ofrecen perspectivas complementarias
        para analizar el comportamiento histórico de la TRM
        colombiana durante el periodo 2016-2019.

        El modelo VAR(2) permite estudiar las relaciones
        dinámicas entre la TRM y las variables internacionales
        Brent, DXY y VIX, así como evaluar su capacidad
        predictiva. Las cadenas de Markov permiten identificar
        patrones de permanencia y transición entre los estados
        de rendimiento bajo, intermedio y alto. Por su parte,
        la simulación Monte Carlo permite explorar la
        incertidumbre mediante múltiples trayectorias posibles.

        En conjunto, estos enfoques proporcionan diferentes
        perspectivas estadísticas del comportamiento de la
        TRM. Sin embargo, sus resultados deben interpretarse
        considerando los supuestos y las limitaciones
        particulares de cada modelo.
        """)
        st.subheader("Limitaciones del análisis")

        st.markdown("""
        - Los modelos utilizan información histórica del periodo
          2016-2019, por lo que sus resultados no representan
          pronósticos actualizados para 2026.

        - El modelo VAR(2) presenta limitaciones en su capacidad
          predictiva: mejora frente al modelo de referencia en
          pronósticos a un paso, pero no en la evaluación de
          varios pasos.

        - Las pruebas de diagnóstico del VAR identificaron
          desviaciones de normalidad y presencia de efectos
          ARCH en los residuos, aspectos que deben considerarse
          al interpretar sus resultados.

        - Las cadenas de Markov suponen probabilidades de
          transición constantes en el tiempo y dependen de
          la clasificación de los rendimientos en tres estados.

        - Monte Carlo supone rendimientos independientes,
          con distribución normal y parámetros constantes.
          Por tanto, no incorpora cambios en la volatilidad
          ni relaciones con las variables internacionales.

        - Los tres modelos se estiman de manera independiente;
          sus resultados ofrecen perspectivas complementarias,
          pero no constituyen un único modelo combinado.
        """)
        # ==========================================
        # 12. MENSAJE FINAL
        # ==========================================

        st.divider()

        st.markdown(
            """
            <div style="text-align: center; padding: 15px;">
                <h3>Temporal Minds</h3>
                <p>Proyecto Integrador | 2026</p>
                <p>Análisis e Interpretación de Datos a través de Python</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as error:

        st.error(
            f"Se presentó un problema al leer los datos: {error}"
        )

else:

    st.error(
        "No se encontró el archivo Excel."
    )

    st.write(
        "Comprueba que el archivo esté dentro de "
        "la carpeta Temporal_Minds y que su nombre "
        "sea exactamente:"
    )

    st.code(
        "Base_datos_TRM_Brent_DXY_VIX_2016_2019.xlsx"
    )

