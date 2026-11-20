
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. CARGA DE DATOS
# ============================================================

from pathlib import Path

carpeta_proyecto = Path(__file__).parent

archivo_excel = carpeta_proyecto / "Base_datos_TRM_Brent_DXY_VIX_2016_2019_documentada.xlsx"

df = pd.read_excel(
    archivo_excel,
    sheet_name="Base_diaria"
)

df["Fecha"] = pd.to_datetime(df["Fecha"])
df = df.sort_values("Fecha")
df = df.set_index("Fecha")
# ============================================================
# 2. VERIFICACIÓN DE LOS DATOS
# ============================================================

print("\n")
print("=" * 60)
print("VERIFICACIÓN DE DATOS PARA MONTE CARLO")
print("=" * 60)

print("\nDimensiones de la base de datos:")
print(df.shape)

print("\nFecha inicial:")
print(df.index.min())

print("\nFecha final:")
print(df.index.max())

print("\nÚltimo valor observado de la TRM:")
print(df["TRM (COP/USD)"].iloc[-1])

# ============================================================
# 2. CALCULO DE RENDIMIENTOS LOGARITMICOS
# ============================================================

trm_log_retornos = np.log(df["TRM (COP/USD)"]).diff().dropna()

media = trm_log_retornos.mean()
desviacion = trm_log_retornos.std()

print("\n")
print("=" * 60)
print("ESTADISTICAS DE LOS RENDIMIENTOS DE LA TRM")
print("=" * 60)

print(f"Cantidad de rendimientos: {len(trm_log_retornos)}")
print(f"Media diaria: {media:.8f}")
print(f"Desviacion estandar: {desviacion:.8f}")

# ============================================================
# 3. SIMULACION MONTE CARLO
# ============================================================

n_simulaciones = 1000
horizonte = 30

ultimo_valor_trm = df["TRM (COP/USD)"].iloc[-1]

# Fijar semilla para reproducibilidad
np.random.seed(42)

# Generar rendimientos simulados
rendimientos_simulados = np.random.normal(
    loc=media,
    scale=desviacion,
    size=(horizonte, n_simulaciones)
)

# Convertir rendimientos en valores de TRM
trayectorias_trm = ultimo_valor_trm * np.exp(
    np.cumsum(rendimientos_simulados, axis=0)
)

print("\n")
print("=" * 60)
print("SIMULACION MONTE CARLO")
print("=" * 60)

print(f"Numero de simulaciones: {n_simulaciones}")
print(f"Horizonte de simulacion: {horizonte} dias")
print(f"Valor inicial de la TRM: {ultimo_valor_trm:.2f}")

print("\nDimensiones de las trayectorias:")
print(trayectorias_trm.shape)

print("\nPrimeros valores simulados:")
print(trayectorias_trm[:5, :5])

# ============================================================
# 4. CALCULO DE ESCENARIOS
# ============================================================

media_simulada = trayectorias_trm.mean(axis=1)

p5 = np.percentile(trayectorias_trm, 5, axis=1)
p50 = np.percentile(trayectorias_trm, 50, axis=1)
p95 = np.percentile(trayectorias_trm, 95, axis=1)

tabla_escenarios = pd.DataFrame({
    "Dia": range(1, horizonte + 1),
    "Media_TRM": media_simulada,
    "Escenario_bajo_P5": p5,
    "Escenario_central_P50": p50,
    "Escenario_alto_P95": p95
})

print("\n")
print("=" * 60)
print("ESCENARIOS DE LA TRM - MONTE CARLO")
print("=" * 60)

print("\nResultados del dia 30:")
print(f"Media simulada: ${media_simulada[-1]:,.2f}")
print(f"Escenario bajo (P5): ${p5[-1]:,.2f}")
print(f"Escenario central (P50): ${p50[-1]:,.2f}")
print(f"Escenario alto (P95): ${p95[-1]:,.2f}")

print("\nPrimeros cinco dias:")
print(tabla_escenarios.head())

# ============================================================
# 5. GRAFICA DE LA SIMULACION MONTE CARLO
# ============================================================

dias = range(1, horizonte + 1)

plt.figure(figsize=(12, 6))

plt.plot(
    dias,
    media_simulada,
    label="Media simulada",
    linewidth=2
)

plt.plot(
    dias,
    p50,
    label="Escenario central (P50)",
    linestyle="--"
)

plt.fill_between(
    dias,
    p5,
    p95,
    alpha=0.25,
    label="Intervalo de escenarios P5-P95"
)

plt.axhline(
    y=ultimo_valor_trm,
    linestyle=":",
    label="TRM inicial"
)

plt.title("Simulacion Monte Carlo - TRM")
plt.xlabel("Dias simulados")
plt.ylabel("TRM (COP/USD)")
plt.legend()
plt.grid(True)

plt.savefig(
    "MonteCarlo_TRM.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# ============================================================
# 6. EXPORTACION DE RESULTADOS A EXCEL
# ============================================================

tabla_trayectorias = pd.DataFrame(
    trayectorias_trm,
    index=range(1, horizonte + 1),
    columns=[f"Simulacion_{i+1}" for i in range(n_simulaciones)]
)

tabla_trayectorias.index.name = "Dia"

with pd.ExcelWriter("Resultados_MonteCarlo_TRM.xlsx") as writer:

    tabla_escenarios.to_excel(
        writer,
        sheet_name="Escenarios",
        index=False
    )

    tabla_trayectorias.to_excel(
        writer,
        sheet_name="Trayectorias"
    )

print("\n")
print("=" * 60)
print("EXPORTACION DE RESULTADOS")
print("=" * 60)

print("Grafica guardada: MonteCarlo_TRM.png")
print("Excel guardado: Resultados_MonteCarlo_TRM.xlsx")
print("Hojas del Excel: Escenarios y Trayectorias")

# ============================================================
# 7. COMPROBACION DE ESTABILIDAD
# ============================================================

rng = np.random.default_rng(42)

max_simulaciones = 10000

rendimientos_estabilidad = rng.normal(
    loc=media,
    scale=desviacion,
    size=(max_simulaciones, horizonte)
)

trayectorias_estabilidad = ultimo_valor_trm * np.exp(
    np.cumsum(rendimientos_estabilidad, axis=1)
)

resultados_estabilidad = []

for cantidad in [1000, 5000, 10000]:

    valores_finales = trayectorias_estabilidad[:cantidad, -1]

    resultados_estabilidad.append({
        "Simulaciones": cantidad,
        "Media_dia_30": np.mean(valores_finales),
        "P5_dia_30": np.percentile(valores_finales, 5),
        "P50_dia_30": np.percentile(valores_finales, 50),
        "P95_dia_30": np.percentile(valores_finales, 95)
    })

tabla_estabilidad = pd.DataFrame(resultados_estabilidad)

print("\n")
print("=" * 65)
print("COMPROBACION DE ESTABILIDAD MONTE CARLO")
print("=" * 65)

print(tabla_estabilidad.to_string(index=False))

