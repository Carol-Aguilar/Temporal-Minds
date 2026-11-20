# ==========================================
# PROYECTO TEMPORAL MINDS
# MODELO DE CADENAS DE MARKOV
# ==========================================

import pandas as pd
import numpy as np

# Cargar la base de datos original
from pathlib import Path

carpeta_proyecto = Path(__file__).parent

archivo_excel = carpeta_proyecto / "Base_datos_TRM_Brent_DXY_VIX_2016_2019_documentada.xlsx"

df = pd.read_excel(
    archivo_excel,
    sheet_name="Base_diaria"
)
# Organizar las fechas
df["Fecha"] = pd.to_datetime(df["Fecha"])
df = df.sort_values("Fecha")
df = df.set_index("Fecha")

# Verificar los datos
print("\nBASE DE DATOS PARA MARKOV")
print(df.head())

print("\nDIMENSIONES DE LA BASE:")
print(df.shape)

print("\nCOLUMNAS:")
print(df.columns.tolist())

# ==========================================
# RENDIMIENTOS DIARIOS DE LA TRM
# ==========================================

trm_retornos = df["TRM (COP/USD)"].pct_change().dropna()

print("\nRESUMEN DE RENDIMIENTOS DIARIOS DE LA TRM")
print(trm_retornos.describe())

print("\nCUANTIL 33:")
print(trm_retornos.quantile(0.33))

print("\nCUANTIL 66:")
print(trm_retornos.quantile(0.66))

# ==========================================
# CLASIFICACIÓN DE LOS ESTADOS DE MARKOV
# ==========================================

q1 = trm_retornos.quantile(0.33)
q2 = trm_retornos.quantile(0.66)

def asignar_estado(x):
    if x <= q1:
        return "Rendimiento bajo"
    elif x <= q2:
        return "Rendimiento intermedio"
    else:
        return "Rendimiento alto"

estados = trm_retornos.apply(asignar_estado)

print("\nFRECUENCIA DE LOS ESTADOS")
print(estados.value_counts())

print("\nPROPORCIÓN DE LOS ESTADOS")
print(estados.value_counts(normalize=True))

# ==========================================
# MATRIZ DE TRANSICIÓN DE MARKOV
# ==========================================

transiciones = pd.crosstab(
    estados.iloc[:-1].to_numpy(),
    estados.iloc[1:].to_numpy(),
    normalize="index"
)

orden_estados = [
    "Rendimiento bajo",
    "Rendimiento intermedio",
    "Rendimiento alto"
]

transiciones = transiciones.reindex(
    index=orden_estados,
    columns=orden_estados
)

print("\nMATRIZ DE TRANSICIÓN DE MARKOV")
print(transiciones)

print("\nSUMA DE LAS FILAS")
print(transiciones.sum(axis=1))

# ==========================================
# DISTRIBUCIÓN EMPÍRICA DE LOS ESTADOS
# ==========================================

distribucion_empirica = estados.value_counts(normalize=True)

distribucion_empirica = distribucion_empirica.reindex(orden_estados)

print("\nDISTRIBUCIÓN EMPÍRICA DE LOS ESTADOS")
print(distribucion_empirica)

# ==========================================
# FRECUENCIAS DE TRANSICIÓN DE MARKOV
# ==========================================

conteo_transiciones = pd.crosstab(
    estados.iloc[:-1].to_numpy(),
    estados.iloc[1:].to_numpy()
)

conteo_transiciones = conteo_transiciones.reindex(
    index=orden_estados,
    columns=orden_estados,
    fill_value=0
)

print("\nFRECUENCIAS DE TRANSICIÓN")
print(conteo_transiciones)

print("\nTOTAL DE TRANSICIONES POR ESTADO ACTUAL")
print(conteo_transiciones.sum(axis=1))

# ==========================================
# PROYECCIÓN DE ESTADOS FUTUROS
# CADENA DE MARKOV
# ==========================================

ultimo_estado = estados.iloc[-1]

distribucion_inicial = pd.Series(
    0.0,
    index=orden_estados
)

distribucion_inicial[ultimo_estado] = 1.0

print("\nÚLTIMO ESTADO OBSERVADO:")
print(ultimo_estado)

horizontes = [1, 5, 10, 20]

resultados_proyeccion = []

for dia in horizontes:

    distribucion_futura = distribucion_inicial.copy()

    for _ in range(dia):
        distribucion_futura = distribucion_futura @ transiciones

    resultados_proyeccion.append(
        distribucion_futura.rename(dia)
    )

tabla_proyecciones = pd.DataFrame(resultados_proyeccion)

tabla_proyecciones.index.name = "Horizonte (días)"

print("\nTABLA DE PROYECCIONES FUTURAS")
print(tabla_proyecciones)

# ==========================================
# EXPORTAR RESULTADOS DE MARKOV A EXCEL
# ==========================================

with pd.ExcelWriter("Resultados_Markov_TRM.xlsx") as writer:

    distribucion_empirica.to_frame(
        name="Proporcion"
    ).to_excel(
        writer,
        sheet_name="Distribucion"
    )

    transiciones.to_excel(
        writer,
        sheet_name="Matriz_Markov"
    )

    conteo_transiciones.to_excel(
        writer,
        sheet_name="Frecuencias"
    )

    tabla_proyecciones.to_excel(
        writer,
        sheet_name="Proyecciones"
    )

print("\nRESULTADOS EXPORTADOS CORRECTAMENTE")
print("Archivo: Resultados_Markov_TRM.xlsx")