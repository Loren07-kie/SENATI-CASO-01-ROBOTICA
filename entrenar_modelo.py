"""Caso 02 SENATI: entrenar modelo de costo de transporte agrícola.

Ejecución: python entrenar_modelo.py
Separa 80/20 con semilla 42 y exporta coeficientes a modelo.json.
"""
import json
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

BASE = Path(__file__).resolve().parent
VARIABLES = ["distancia_km", "carga_kg", "via_no_asfaltada"]
OBJETIVO = "costo_transporte_soles"

datos = pd.read_csv(BASE / "datos.csv", encoding="utf-8-sig")
print("Dimensiones del conjunto de datos:", datos.shape)
print("\nPrimeros registros:\n", datos.head().to_string(index=False))
print("\nValores faltantes:\n", datos.isna().sum().to_string())

if datos[VARIABLES + [OBJETIVO]].isna().any().any():
    raise ValueError("Hay valores faltantes que deben revisarse antes de entrenar.")
if not datos["via_no_asfaltada"].isin([0, 1]).all():
    raise ValueError("La variable de tipo de vía debe contener solo 0 o 1.")

X = datos[VARIABLES]
y = datos[OBJETIVO]
X_ent, X_prueba, y_ent, y_prueba = train_test_split(
    X, y, test_size=0.20, random_state=42
)

modelo = LinearRegression()
modelo.fit(X_ent, y_ent)
y_pred = modelo.predict(X_prueba)
mae = float(mean_absolute_error(y_prueba, y_pred))
r2 = float(r2_score(y_prueba, y_pred))

reporte = {
    "intercepto": float(modelo.intercept_),
    "coeficientes": {n: float(c) for n, c in zip(VARIABLES, modelo.coef_)},
    "variables": VARIABLES,
    "objetivo": OBJETIVO,
    "metricas": {
        "mae": mae, "r2": r2,
        "filas_entrenamiento": len(X_ent), "filas_prueba": len(X_prueba)
    },
    "nota": "Modelo académico basado en 130 viajes simulados. No es una tarifa contractual."
}
(BASE / "modelo.json").write_text(
    json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("\nIntercepto (S/):", round(reporte["intercepto"], 4))
for var, coef in reporte["coeficientes"].items():
    print(var, ":", round(coef, 5))
print(f"\nMAE prueba: S/ {mae:.4f}; R² prueba: {r2:.4f}")
for distancia, carga, via in [(25,400,0),(100,1200,1)]:
    pred = modelo.predict(pd.DataFrame([{
        "distancia_km": distancia, "carga_kg": carga, "via_no_asfaltada": via
    }]))[0]
    print(f"Prueba {distancia} km, {carga} kg, vía {via}: S/ {pred:.2f}")
