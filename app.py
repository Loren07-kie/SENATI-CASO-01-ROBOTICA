import json
import os
from pathlib import Path
from flask import Flask, render_template, request

BASE = Path(__file__).resolve().parent
with (BASE / "modelo.json").open(encoding="utf-8") as f:
    MODELO = json.load(f)
app = Flask(__name__)

def estimar(consultas, publicidad, campana):
    c = MODELO["coeficientes"]
    return (MODELO["intercepto"] + c["consultas_web"] * consultas +
            c["inversion_publicidad_soles"] * publicidad + c["campana_escolar"] * campana)

@app.route("/", methods=["GET", "POST"])
def inicio():
    valores = {"consultas": "20", "publicidad": "200", "campana": "0"}
    error, resultado = None, None
    if request.method == "POST":
        valores = {k: request.form.get(k, "").strip() for k in valores}
        try:
            consultas = float(valores["consultas"])
            publicidad = float(valores["publicidad"])
            if valores["campana"] not in ("0", "1"):
                raise ValueError("La campaña debe ser 0 o 1.")
            campana = int(valores["campana"])
            if not (5 <= consultas <= 70) or not consultas.is_integer():
                raise ValueError("Las consultas deben ser un entero entre 5 y 70.")
            if not (0 <= publicidad <= 1100):
                raise ValueError("La inversión debe estar entre S/ 0 y S/ 1100.")
            prediccion = estimar(consultas, publicidad, campana)
            resultado = {"decimal": f"{prediccion:.2f}", "entero": max(0, round(prediccion))}
        except (ValueError, OverflowError) as exc:
            error = str(exc) or "Revisa los datos ingresados."
    return render_template("index.html", valores=valores, resultado=resultado,
                           error=error, metricas=MODELO["metricas"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
