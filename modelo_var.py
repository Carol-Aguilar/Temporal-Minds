import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.api import VAR
from statsmodels.stats.diagnostic import het_arch

# ==========================================
# 1. UBICACIÓN DEL ARCHIVO
# ==========================================

carpeta_proyecto = Path(__file__).parent

archivo_excel = carpeta_proyecto / "Base_datos_TRM_Brent_DXY_VIX_2016_2019_documentada.xlsx"

# ==========================================
# 2. CARGA DE LOS DATOS
# ==========================================

df = pd.read_excel(
    archivo_excel,
    sheet_name="Base_diaria"
)

# ==========================================
# 3. PREPARACIÓN DE LOS DATOS
# ==========================================

df["Fecha"] = pd.to_datetime(df["Fecha"])

df = df.sort_values("Fecha")
df = df.set_index("Fecha")

# ==========================================
# 3.1. RENOMBRAR VARIABLES
# ==========================================

df = df.rename(columns={
    "TRM (COP/USD)": "TRM",
    "Brent (USD/barril)": "Brent",
    "DXY (índice)": "DXY",
    "VIX (índice)": "VIX"
})

# ==========================================
# 4. VERIFICACIÓN
# ==========================================

print("DATOS CARGADOS CORRECTAMENTE")

print("\nPrimeras cinco filas:")
print(df.head())

print("\nDimensiones de la base:")
print(df.shape)

print("\nNombres de las variables:")
print(df.columns.tolist())


# ==========================================
# 5. REVISIÓN DE CALIDAD DE LOS DATOS
# ==========================================

print("\nDATOS FALTANTES POR VARIABLE:")
print(df.isnull().sum())

print("\nTOTAL DE DATOS FALTANTES:")
print(df.isnull().sum().sum())

print("\nFECHAS DUPLICADAS:")
print(df.index.duplicated().sum())

print("\nPERIODO ANALIZADO:")
print("Fecha inicial:", df.index.min())
print("Fecha final:", df.index.max())


# ==========================================
# 6. PRUEBAS DE ESTACIONARIEDAD
# ==========================================

print("\nPRUEBAS DE ESTACIONARIEDAD ADF Y KPSS")

for variable in df.columns:

    serie = df[variable].dropna()

    # Prueba ADF
    resultado_adf = adfuller(serie, autolag="AIC")

    # Prueba KPSS
    resultado_kpss = kpss(
        serie,
        regression="c",
        nlags="auto"
    )

    print("\n--------------------------------")
    print("VARIABLE:", variable)
    print("--------------------------------")

    print("ADF - Estadístico:", resultado_adf[0])
    print("ADF - Valor p:", resultado_adf[1])

    if resultado_adf[1] < 0.05:
        print("ADF: Se rechaza la hipótesis de raíz unitaria.")
    else:
        print("ADF: No se rechaza la hipótesis de raíz unitaria.")

    print("KPSS - Estadístico:", resultado_kpss[0])
    print("KPSS - Valor p:", resultado_kpss[1])

    if resultado_kpss[1] < 0.05:
        print("KPSS: Se rechaza la hipótesis de estacionariedad.")
    else:
        print("KPSS: No se rechaza la hipótesis de estacionariedad.")


# ==========================================
# 7. TRANSFORMACIÓN DE LAS VARIABLES
# ==========================================

print("\nTRANSFORMACIÓN DE LAS VARIABLES PARA EL VAR")

df_var = pd.DataFrame(index=df.index)

# Diferencias logarítmicas
df_var["TRM"] = np.log(df["TRM"]).diff()
df_var["Brent"] = np.log(df["Brent"]).diff()
df_var["DXY"] = np.log(df["DXY"]).diff()

# VIX se conserva en niveles
df_var["VIX"] = df["VIX"]

# Eliminar la primera fila, que queda vacía
df_var = df_var.dropna()

print("\nPrimeras cinco filas de la base transformada:")
print(df_var.head())

print("\nDimensiones de la base transformada:")
print(df_var.shape)

print("\nDatos faltantes después de la transformación:")
print(df_var.isnull().sum())


# ==========================================
# 8. PRUEBAS DE ESTACIONARIEDAD DESPUÉS
#    DE LAS TRANSFORMACIONES
# ==========================================

print("\nESTACIONARIEDAD DE LAS VARIABLES TRANSFORMADAS")

for variable in df_var.columns:

    serie = df_var[variable].dropna()

    # Prueba ADF
    resultado_adf = adfuller(serie, autolag="AIC")

    # Prueba KPSS
    resultado_kpss = kpss(
        serie,
        regression="c",
        nlags="auto"
    )

    print("\n--------------------------------")
    print("VARIABLE:", variable)
    print("--------------------------------")

    print("ADF - Valor p:", resultado_adf[1])
    print("KPSS - Valor p:", resultado_kpss[1])

    if resultado_adf[1] < 0.05 and resultado_kpss[1] >= 0.05:
        print("RESULTADO: Evidencia favorable de estacionariedad.")
    else:
        print("RESULTADO: Se requiere revisar la estacionariedad.")


# ==========================================
# 9. SELECCIÓN DEL NÚMERO DE REZAGOS
# ==========================================

print("\nSELECCIÓN DEL NÚMERO DE REZAGOS DEL VAR")

# Crear el modelo VAR con las variables transformadas
modelo = VAR(df_var)

# Evaluar hasta 10 rezagos
seleccion = modelo.select_order(maxlags=10)

# Mostrar los criterios de información
print("\nResultados de los criterios de selección:")
print(seleccion.summary())

# Mostrar los rezagos seleccionados
print("\nREZAGOS RECOMENDADOS POR CADA CRITERIO:")

print("AIC:", seleccion.selected_orders["aic"])
print("BIC:", seleccion.selected_orders["bic"])
print("HQIC:", seleccion.selected_orders["hqic"])
print("FPE:", seleccion.selected_orders["fpe"])
     

# ==========================================
# 10. ESTIMACIÓN DEL MODELO VAR(2)
# ==========================================

print("\nESTIMACIÓN DEL MODELO VAR(2)")

# Estimar el modelo con dos rezagos
resultado_var = modelo.fit(2)

# Mostrar resultados
print("\nRESUMEN DEL MODELO VAR(2):")
print(resultado_var.summary())

# ==========================================
# 10.1. PRUEBA DE ESTABILIDAD
# ==========================================

print("\nPRUEBA DE ESTABILIDAD DEL MODELO")

estabilidad = resultado_var.is_stable()

print("¿El modelo es estable?:", estabilidad)

if estabilidad:
    print("El modelo cumple el criterio de estabilidad.")
else:
    print("El modelo no cumple el criterio de estabilidad.")

# ==========================================
# 11. DIAGNÓSTICO DE AUTOCORRELACIÓN
# ==========================================

print("\nPRUEBA DE AUTOCORRELACIÓN DE LOS RESIDUOS")

prueba_residuos = resultado_var.test_whiteness(
    nlags=12,
    signif=0.05
)

print(prueba_residuos.summary())


# ==========================================
# 11. PRUEBA DE AUTOCORRELACIÓN DE RESIDUOS
# ==========================================

print("\nPRUEBA DE AUTOCORRELACIÓN DE LOS RESIDUOS")

prueba_residuos = resultado_var.test_whiteness(
    nlags=12,
    signif=0.05
)

print(prueba_residuos.summary())



# ==========================================
# 12. PRUEBA DE NORMALIDAD DE LOS RESIDUOS
# ==========================================

print("\nPRUEBA DE NORMALIDAD DE LOS RESIDUOS")

prueba_normalidad = resultado_var.test_normality(
    signif=0.05
)

print(prueba_normalidad.summary())


# ==========================================
# 13. CAUSALIDAD DE GRANGER SOBRE LA TRM
# ==========================================

print("\nPRUEBA DE CAUSALIDAD DE GRANGER")

prueba_granger = resultado_var.test_causality(
    caused="TRM",
    causing=["Brent", "DXY", "VIX"],
    kind="f"
)

print(prueba_granger.summary())


# ==========================================
# 14. CAUSALIDAD DE GRANGER INDIVIDUAL
# ==========================================

print("\nCAUSALIDAD DE GRANGER INDIVIDUAL")

for variable in ["Brent", "DXY", "VIX"]:

    prueba = resultado_var.test_causality(
        caused="TRM",
        causing=variable,
        kind="f"
    )

    print(f"\n¿{variable} causa en sentido de Granger a la TRM?")
    print(prueba.summary())


# ==========================================
# 15. FUNCIONES DE IMPULSO-RESPUESTA (IRF)
# ==========================================

print("\nFUNCIONES DE IMPULSO-RESPUESTA")

# Calcular respuestas durante 10 periodos
irf = resultado_var.irf(10)

# Graficar las respuestas del modelo
irf.plot(orth=False)

plt.tight_layout()
plt.show()


# ==========================================
# 15.1. RESPUESTAS DE LA TRM
# ==========================================

print("\nRESPUESTA DE LA TRM ANTE INNOVACIONES")

impulsos_trm = irf.irfs[:, 0, :]

tabla_irf = pd.DataFrame(
    impulsos_trm,
    columns=["TRM", "Brent", "DXY", "VIX"]
)

print("\nValores de las respuestas de la TRM:")
print(tabla_irf.round(6))


# ==========================================
# 16. DESCOMPOSICIÓN DE LA VARIANZA (FEVD)
# ==========================================

print("\nDESCOMPOSICIÓN DE LA VARIANZA (FEVD)")

# Calcular la descomposición para 10 periodos
fevd = resultado_var.fevd(10)

# Mostrar resultados de todas las variables
print("\nResultados completos de la FEVD:")
print(fevd.summary())

# Extraer la descomposición correspondiente a la TRM
tabla_fevd = pd.DataFrame(
    fevd.decomp[0],
    columns=["TRM", "Brent", "DXY", "VIX"]
)

print("\nDescomposición de la varianza del error de pronóstico de la TRM:")
print(tabla_fevd.round(6))


# ==========================================
# 17. ANALISIS DE LOS RESIDUOS DEL VAR
# ==========================================

print("\nANALISIS DE LOS RESIDUOS DEL VAR")

residuos = resultado_var.resid

print("\nEstadisticas descriptivas de los residuos:")
print(residuos.describe().round(6))

# Graficar la distribucion de los residuos
residuos.hist(
    bins=30,
    figsize=(12, 8)
)

plt.tight_layout()
plt.show()


# ==========================================
# 18. IDENTIFICACION DE RESIDUOS EXTREMOS EN VIX
# ==========================================

print("\nRESIDUOS EXTREMOS DE VIX")

desviacion_vix = residuos["VIX"].std()

extremos_vix = residuos[
    np.abs(residuos["VIX"]) > 3 * desviacion_vix
]

print("\nCantidad de residuos extremos:")
print(len(extremos_vix))

print("\nFechas y valores identificados:")
print(extremos_vix.round(6))


# ==========================================
# 19. REVISION DE LOS DATOS ORIGINALES DE VIX
# ==========================================

print("\nREVISION DE VIX EN FEBRERO DE 2018")

print(
    df.loc[
        "2018-02-01":"2018-02-16",
        ["VIX"]
    ]
)

print("\nRESIDUOS DEL MODELO EN ESAS FECHAS")

print(
    residuos.loc[
        "2018-02-01":"2018-02-16",
        ["VIX"]
    ].round(6)
)

# ==========================================
# 20. RESIDUOS EXTREMOS EN TODAS LAS VARIABLES
# ==========================================

print("\nRESIDUOS EXTREMOS POR VARIABLE")

for variable in residuos.columns:

    desviacion = residuos[variable].std()

    extremos = residuos[
        np.abs(residuos[variable]) > 3 * desviacion
    ]

    print(f"\nVariable: {variable}")
    print("Cantidad de residuos extremos:", len(extremos))

    print(extremos[[variable]].round(6))


# ==========================================
# 21. PRUEBA ARCH SOBRE LOS RESIDUOS
# ==========================================

print("\nPRUEBA ARCH DE HETEROCEDASTICIDAD")

for variable in residuos.columns:

    resultado_arch = het_arch(
        residuos[variable],
        nlags=5
    )

    estadistico, p_value, f_stat, f_pvalue = resultado_arch

    print(f"\nVariable: {variable}")
    print("Estadistico ARCH:", round(estadistico, 4))
    print("Valor p:", round(p_value, 6))

    if p_value < 0.05:
        print("Conclusion: hay evidencia de efectos ARCH.")
    else:
        print("Conclusion: no hay evidencia suficiente de efectos ARCH.")


# ==========================================
# 22. COMPARACION DE ESPECIFICACIONES VAR(2)
# ==========================================

print("\nCOMPARACION DE ESPECIFICACIONES VAR(2)")

# Modelo actual: constante
var_constante = modelo.fit(2, trend="c")

# Modelo alternativo: constante y tendencia
var_tendencia = modelo.fit(2, trend="ct")

# Comparar criterios de informacion
comparacion = pd.DataFrame({
    "Con constante": [
        var_constante.aic,
        var_constante.bic,
        var_constante.hqic,
        var_constante.fpe
    ],
    "Constante y tendencia": [
        var_tendencia.aic,
        var_tendencia.bic,
        var_tendencia.hqic,
        var_tendencia.fpe
    ]
}, index=["AIC", "BIC", "HQIC", "FPE"])

print("\nCriterios de informacion:")
print(comparacion.round(8))

print("\nEstabilidad de los modelos:")
print("Con constante:", var_constante.is_stable())
print("Con constante y tendencia:", var_tendencia.is_stable())


# ==========================================
# 23. SENSIBILIDAD DE LA FEVD AL ORDEN
# ==========================================

print("\nSENSIBILIDAD DE LA FEVD AL ORDEN DE VARIABLES")

# FEVD con el orden original
fevd_original = resultado_var.fevd(10)

orden_original = ["TRM", "Brent", "DXY", "VIX"]

participacion_original = pd.Series(
    fevd_original.decomp[0, -1, :],
    index=orden_original
)

# Crear una base con orden alternativo
orden_alternativo = ["VIX", "DXY", "Brent", "TRM"]

df_alternativo = df_var[orden_alternativo]

# Estimar nuevamente el VAR(2)
modelo_alternativo = VAR(df_alternativo)
resultado_alternativo = modelo_alternativo.fit(2)

# Calcular FEVD con el nuevo orden
fevd_alternativo = resultado_alternativo.fevd(10)

# TRM ahora ocupa la cuarta posición
participacion_alternativa = pd.Series(
    fevd_alternativo.decomp[3, -1, :],
    index=orden_alternativo
)

# Organizar ambas comparaciones en el mismo orden
comparacion_fevd = pd.DataFrame({
    "Orden original (%)": participacion_original * 100,
    "Orden alternativo (%)": participacion_alternativa * 100
})

print("\nParticipacion en la varianza del error de pronostico de TRM:")
print(comparacion_fevd.round(4))

print("\nEstabilidad del modelo alternativo:")
print(resultado_alternativo.is_stable())


# ==========================================
# 24. COMPARACION DE FUNCIONES IRF
# ==========================================

print("\nCOMPARACION DE IMPULSO-RESPUESTA")

# Respuestas no ortogonalizadas
irf_no_ortogonal = resultado_var.irf(10)

# Respuestas ortogonalizadas
irf_ortogonal = resultado_var.irf(10)

# Extraer las respuestas de la TRM
tabla_irf_comparacion = pd.DataFrame({
    "No ortogonalizada - Brent": irf_no_ortogonal.irfs[:, 0, 1],
    "Ortogonalizada - Brent": irf_ortogonal.orth_irfs[:, 0, 1],
    "No ortogonalizada - DXY": irf_no_ortogonal.irfs[:, 0, 2],
    "Ortogonalizada - DXY": irf_ortogonal.orth_irfs[:, 0, 2],
    "No ortogonalizada - VIX": irf_no_ortogonal.irfs[:, 0, 3],
    "Ortogonalizada - VIX": irf_ortogonal.orth_irfs[:, 0, 3]
})

print("\nRespuestas de la TRM ante innovaciones externas:")
print(tabla_irf_comparacion.round(6))

# Graficar las respuestas ortogonalizadas
irf_ortogonal.plot(orth=True)

plt.tight_layout()
plt.show()

# ==========================================
# 25. EVALUACION DEL PRONOSTICO DEL VAR
# ==========================================

print("\nEVALUACION DEL PRONOSTICO VAR(2)")

# Separar los datos cronologicamente
n_test = int(len(df_var) * 0.20)

datos_entrenamiento = df_var.iloc[:-n_test]
datos_prueba = df_var.iloc[-n_test:]

print("\nObservaciones para entrenamiento:", len(datos_entrenamiento))
print("Observaciones para prueba:", len(datos_prueba))

# Estimar el VAR(2) con los datos de entrenamiento
modelo_entrenamiento = VAR(datos_entrenamiento)
resultado_entrenamiento = modelo_entrenamiento.fit(2)

# Generar pronosticos para el periodo de prueba
pronosticos = resultado_entrenamiento.forecast(
    datos_entrenamiento.values[-2:],
    steps=len(datos_prueba)
)

# Organizar los pronosticos en una tabla
pronosticos_df = pd.DataFrame(
    pronosticos,
    index=datos_prueba.index,
    columns=df_var.columns
)

# Calcular errores de pronostico
errores = datos_prueba - pronosticos_df

mae = errores.abs().mean()
rmse = np.sqrt((errores ** 2).mean())

tabla_metricas = pd.DataFrame({
    "MAE": mae,
    "RMSE": rmse
})

print("\nMETRICAS DE ERROR DEL PRONOSTICO:")
print(tabla_metricas.round(6))

print("\nPRIMEROS PRONOSTICOS DE LA TRM:")
print(pronosticos_df["TRM"].head(10).round(6))

# ==========================================
# 26. COMPARACION CON PRONOSTICO DE REFERENCIA
# ==========================================

print("\nCOMPARACION VAR(2) VS PRONOSTICO DE REFERENCIA")

# Pronostico de referencia: cambio logaritmico igual a cero
pronostico_referencia = np.zeros(len(datos_prueba))

# Valores reales de la TRM transformada
valores_reales = datos_prueba["TRM"].values

# Pronosticos del VAR
pronostico_var = pronosticos_df["TRM"].values

# Calcular errores absolutos y cuadrados
mae_referencia = np.mean(
    np.abs(valores_reales - pronostico_referencia)
)

rmse_referencia = np.sqrt(
    np.mean((valores_reales - pronostico_referencia) ** 2)
)

mae_var = np.mean(
    np.abs(valores_reales - pronostico_var)
)

rmse_var = np.sqrt(
    np.mean((valores_reales - pronostico_var) ** 2)
)

comparacion = pd.DataFrame({
    "MAE": [mae_var, mae_referencia],
    "RMSE": [rmse_var, rmse_referencia]
}, index=["VAR(2)", "Referencia: cambio cero"])

print(comparacion.round(6))

# ==========================================
# 27. PRONOSTICO DINAMICO A UN PASO
# ==========================================

print("\nEVALUACION DEL VAR(2) A UN PASO ADELANTE")

pronosticos_un_paso = []

# Recorrer cronologicamente el periodo de prueba
for i in range(len(datos_prueba)):

    # Incorporar los datos reales disponibles hasta ese momento
    historial = pd.concat([
        datos_entrenamiento,
        datos_prueba.iloc[:i]
    ])

    # Pronosticar el siguiente periodo usando los dos ultimos registros
    pronostico = resultado_entrenamiento.forecast(
        historial.values[-2:],
        steps=1
    )[0]

    pronosticos_un_paso.append(pronostico)

# Organizar los resultados
pronosticos_un_paso_df = pd.DataFrame(
    pronosticos_un_paso,
    index=datos_prueba.index,
    columns=df_var.columns
)

# Evaluar la TRM
valores_reales = datos_prueba["TRM"].values
valores_pronosticados = pronosticos_un_paso_df["TRM"].values

mae_un_paso = np.mean(
    np.abs(valores_reales - valores_pronosticados)
)

rmse_un_paso = np.sqrt(
    np.mean((valores_reales - valores_pronosticados) ** 2)
)

# Referencia: cambio logaritmico igual a cero
mae_referencia_un_paso = np.mean(np.abs(valores_reales))

rmse_referencia_un_paso = np.sqrt(
    np.mean(valores_reales ** 2)
)

# Comparacion
comparacion_un_paso = pd.DataFrame({
    "MAE": [mae_un_paso, mae_referencia_un_paso],
    "RMSE": [rmse_un_paso, rmse_referencia_un_paso]
}, index=["VAR(2) a un paso", "Referencia: cambio cero"])

print("\nCOMPARACION DE PRONOSTICOS DE LA TRM:")
print(comparacion_un_paso.round(6))
comparacion_un_paso.to_excel(
    "Evaluacion_VAR_TRM.xlsx",
    index=True
)

print("\nPRIMEROS 10 PRONOSTICOS A UN PASO:")
print(pronosticos_un_paso_df["TRM"].head(10).round(6))

# ==========================================
# 28. GRAFICO: TRM REAL VS PRONOSTICADA
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    datos_prueba.index,
    datos_prueba["TRM"],
    label="TRM real",
    linewidth=1
)

plt.plot(
    pronosticos_un_paso_df.index,
    pronosticos_un_paso_df["TRM"],
    label="TRM pronosticada por VAR(2)",
    linewidth=1
)

plt.title("TRM real vs. pronosticada - VAR(2) a un paso")
plt.xlabel("Fecha")
plt.ylabel("Cambio logarítmico de la TRM")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()


# ==========================================
# 29. PREDICCION FUTURA DE LA TRM EN COP/USD
# ==========================================

print("\nPREDICCION FUTURA DE LA TRM")

# Horizonte de prediccion
horizonte_prediccion = 30

# Obtener los ultimos dos registros transformados
ultimos_datos = df_var.values[-2:]

# Generar predicciones conjuntas del VAR(2)
predicciones_futuras = resultado_var.forecast(
    y=ultimos_datos,
    steps=horizonte_prediccion
)

# Organizar las predicciones
predicciones_futuras_df = pd.DataFrame(
    predicciones_futuras,
    columns=df_var.columns
)

# Recuperar el ultimo valor historico de la TRM
ultimo_valor_trm = df["TRM"].iloc[-1]
print("\nVERIFICACION DE LA TRM ORIGINAL:")
print(df["TRM"].tail())

# Convertir los cambios logaritmicos pronosticados
# en niveles de TRM
predicciones_futuras_df["TRM_predicha"] = (
    ultimo_valor_trm *
    np.exp(predicciones_futuras_df["TRM"].cumsum())
)

# Crear numeracion de dias futuros
predicciones_futuras_df["Dia"] = range(
    1,
    horizonte_prediccion + 1
)

# Crear fechas futuras (excluyendo sabados y domingos)
ultima_fecha = df.index[-1]

fechas_futuras = pd.bdate_range(
    start=ultima_fecha + pd.Timedelta(days=1),
    periods=horizonte_prediccion
)

predicciones_futuras_df["Fecha"] = fechas_futuras

# Organizar columnas
predicciones_futuras_df = predicciones_futuras_df[
    ["Fecha", "Dia", "TRM", "Brent", "DXY", "VIX", "TRM_predicha"]
]


print("\nUltimo valor historico de la TRM:")
print(f"${ultimo_valor_trm:,.2f}")

print("\nPrimeros diez valores pronosticados:")
print(
    predicciones_futuras_df[
    ["Fecha", "Dia", "TRM_predicha"]
].head(10).round({"TRM_predicha": 2})
)

print("\nValor pronosticado para el dia 30:")
print(
    f"${predicciones_futuras_df['TRM_predicha'].iloc[-1]:,.2f}"
)


# Exportar predicciones futuras a Excel
archivo_predicciones = "Predicciones_Futuras_VAR_TRM.xlsx"

predicciones_futuras_df.to_excel(
    archivo_predicciones,
    index=False
)

print("\nArchivo de predicciones exportado correctamente:")
print(archivo_predicciones)

# ==========================================
# 30. GRAFICO DE PREDICCION FUTURA DE LA TRM
# ==========================================

print("\nGRAFICO DE PREDICCION FUTURA")

# Tomar los ultimos 60 valores historicos
trm_historica = df["TRM"].tail(60)

# Crear posiciones para el grafico
posiciones_historicas = range(-len(trm_historica), 0)
posiciones_futuras = range(0, horizonte_prediccion)

# Crear grafico
plt.figure(figsize=(12, 6))

plt.plot(
    posiciones_historicas,
    trm_historica.values,
    label="TRM historica",
    linewidth=2
)

plt.plot(
    posiciones_futuras,
    predicciones_futuras_df["TRM_predicha"],
    label="TRM pronosticada VAR(2)",
    linestyle="--",
    linewidth=2
)

plt.axvline(
    x=0,
    linestyle=":",
    label="Inicio de la prediccion"
)

plt.title("Prediccion futura de la TRM mediante VAR(2)")
plt.xlabel("Observaciones historicas y pasos futuros")
plt.ylabel("TRM (COP/USD)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Guardar grafico
plt.savefig("Prediccion_Futura_VAR_TRM.png", dpi=300)

plt.show()

print("\nGrafico guardado correctamente.")

