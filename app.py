"""AgroRuta SENATI: web de predicción de costos de transporte (solo Flask/HTML/CSS).
Los coeficientes provienen del entrenamiento reproducible de datos.csv.
"""
import json
import math
import os
from pathlib import Path
from flask import Flask, render_template, request

BASE = Path(__file__).resolve().parent
with (BASE / "modelo.json").open(encoding="utf-8") as archivo:
    MODELO = json.load(archivo)

app = Flask(__name__)

EJEMPLOS = [
    {"nombre": "Ruta corta", "subtitulo": "Caso del instructor · 01", "distancia": 25, "carga": 400, "via": 0,
     "detalle": "Trayecto corto y asfaltado con carga ligera.", "etiqueta": "ASFALTADA"},
    {"nombre": "Ruta exigente", "subtitulo": "Caso del instructor · 02", "distancia": 100, "carga": 1200, "via": 1,
     "detalle": "Más distancia, más carga y carretera no asfaltada.", "etiqueta": "NO ASFALTADA"},
    {"nombre": "Ruta intermedia", "subtitulo": "Exploración adicional", "distancia": 70, "carga": 850, "via": 0,
     "detalle": "Una combinación intermedia para comparar el costo.", "etiqueta": "ASFALTADA"},
]


def predecir_y_desglosar(distancia, carga, via):
    """Regresión múltiple: intercepto + distancia·b1 + carga·b2 + vía·b3."""
    c = MODELO["coeficientes"]
    base = MODELO["intercepto"]
    por_distancia = c["distancia_km"] * distancia
    por_carga = c["carga_kg"] * carga
    por_via = c["via_no_asfaltada"] * via
    return base + por_distancia + por_carga + por_via, {
        "base": round(base, 2),
        "distancia": round(por_distancia, 2),
        "carga": round(por_carga, 2),
        "via": round(por_via, 2),
    }


def interpretar(distancia, carga, via):
    return [
        f"Según el modelo, {distancia:g} km aportan un componente de costo por recorrido; una ruta más larga aumenta la estimación.",
        f"Transportar {carga:g} kg añade un componente por peso, porque la ecuación asocia mayor carga con mayor costo.",
        "La vía no asfaltada suma un recargo estimado respecto de una ruta asfaltada con la misma distancia y carga."
        if via == 1 else
        "La vía asfaltada no incorpora el recargo que la ecuación asigna a los caminos no asfaltados.",
    ]


@app.route("/", methods=["GET", "POST"])
def inicio():
    valores = {"distancia": "25", "carga": "400", "via": "0"}
    error, resultado = None, None
    if request.method == "POST":
        valores = {k: request.form.get(k, "").strip() for k in valores}
        try:
            distancia = float(valores["distancia"])
            carga = float(valores["carga"])
            if not math.isfinite(distancia) or not (3 <= distancia <= 165):
                raise ValueError("La distancia debe estar entre 3 y 165 kilómetros.")
            if not math.isfinite(carga) or not (50 <= carga <= 2050):
                raise ValueError("La carga debe estar entre 50 y 2050 kilogramos.")
            if valores["via"] not in ("0", "1"):
                raise ValueError("Selecciona vía asfaltada o no asfaltada.")
            via = int(valores["via"])
            prediccion, desglose = predecir_y_desglosar(distancia, carga, via)
            resultado = {
                "importe": f"{max(0, prediccion):,.2f}",
                "distancia": f"{distancia:g}",
                "carga": f"{carga:g}",
                "tipo_via": "No asfaltada" if via else "Asfaltada",
                "desglose": desglose,
                "interpretaciones": interpretar(distancia, carga, via),
            }
        except (ValueError, OverflowError) as exc:
            error = str(exc) or "Revisa los valores ingresados."

    ejemplos = []
    for ejemplo in EJEMPLOS:
        importe, _ = predecir_y_desglosar(ejemplo["distancia"], ejemplo["carga"], ejemplo["via"])
        ejemplos.append({**ejemplo, "costo": f"{importe:,.2f}"})

    return render_template(
        "index.html", valores=valores, error=error, resultado=resultado,
        metricas=MODELO["metricas"], coeficientes=MODELO["coeficientes"],
        intercepto=MODELO["intercepto"], ejemplos=ejemplos,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
