import json
import os
from pathlib import Path
from flask import Flask, render_template, request

BASE = Path(__file__).resolve().parent
with (BASE / "modelo.json").open(encoding="utf-8") as archivo:
    MODELO = json.load(archivo)

app = Flask(__name__)

EJEMPLOS = [
    {
        "titulo": "Escenario base",
        "consultas": 20,
        "publicidad": 200,
        "campana": 0,
        "descripcion": "Pocas consultas, inversión moderada y sin campaña escolar.",
    },
    {
        "titulo": "Semana potente",
        "consultas": 55,
        "publicidad": 800,
        "campana": 1,
        "descripcion": "Más movimiento digital, fuerte publicidad y campaña activa.",
    },
    {
        "titulo": "Máximo interés",
        "consultas": 70,
        "publicidad": 1100,
        "campana": 1,
        "descripcion": "El escenario más alto permitido por el caso de estudio.",
    },
]


def estimar(consultas, publicidad, campana):
    factores = {
        "consultas_web": consultas,
        "inversion_publicidad_soles": publicidad,
        "campana_escolar": campana,
    }
    return MODELO["intercepto"] + sum(
        coef * factores[nombre] for nombre, coef in MODELO["coeficientes"].items()
    )


def construir_insights(consultas, publicidad, campana, estimacion):
    ideas = []
    if consultas >= 50:
        ideas.append(
            "Las consultas web son altas, así que existe bastante interés del público en los kits."
        )
    elif consultas >= 30:
        ideas.append(
            "Las consultas web están en un nivel medio, lo que sugiere una demanda moderada."
        )
    else:
        ideas.append(
            "Las consultas web son relativamente bajas, por lo que el interés inicial es más limitado."
        )

    if publicidad >= 700:
        ideas.append(
            "La inversión publicitaria es fuerte; esto suele ayudar a incrementar la visibilidad del producto."
        )
    elif publicidad >= 300:
        ideas.append(
            "La inversión publicitaria es intermedia y aporta apoyo a la captación de pedidos."
        )
    else:
        ideas.append(
            "La inversión publicitaria es baja, de modo que el impulso comercial es más reducido."
        )

    if campana == 1:
        ideas.append(
            "La campaña escolar está activa, por eso el modelo añade un efecto positivo importante en la predicción."
        )
    else:
        ideas.append(
            "No hay campaña escolar, así que el pronóstico depende sobre todo de las consultas y de la publicidad."
        )

    if estimacion >= 30:
        cierre = "Por la combinación de factores, se espera una semana fuerte en pedidos."
    elif estimacion >= 18:
        cierre = "El resultado sugiere una semana aceptable con un volumen medio de pedidos."
    else:
        cierre = "La estimación apunta a una semana tranquila con una demanda limitada."

    return ideas, cierre


@app.route("/", methods=["GET", "POST"])
def inicio():
    valores = {"consultas": "20", "publicidad": "200", "campana": "0"}
    error = None
    resultado = None
    explicaciones = []
    conclusion = ""

    if request.method == "POST":
        valores = {k: request.form.get(k, "").strip() for k in valores}
        try:
            consultas = float(valores["consultas"])
            publicidad = float(valores["publicidad"])
            if valores["campana"] not in ("0", "1"):
                raise ValueError("La campaña escolar debe ser 0 o 1.")
            campana = int(valores["campana"])
            if not 5 <= consultas <= 70 or not consultas.is_integer():
                raise ValueError("Las consultas deben ser un número entero entre 5 y 70.")
            if not 0 <= publicidad <= 1100:
                raise ValueError("La inversión debe estar entre S/ 0 y S/ 1100.")

            estimacion = estimar(consultas, publicidad, campana)
            explicaciones, conclusion = construir_insights(
                consultas, publicidad, campana, estimacion
            )
            resultado = {
                "decimal": f"{estimacion:.2f}",
                "entero": max(0, round(estimacion)),
                "consultas": int(consultas),
                "publicidad": f"{publicidad:.2f}",
                "campana": "Sí" if campana == 1 else "No",
            }
        except (ValueError, OverflowError) as e:
            error = str(e) if str(e) else "Revisa los datos ingresados."

    ejemplos = []
    for ejemplo in EJEMPLOS:
        pred = estimar(
            ejemplo["consultas"], ejemplo["publicidad"], ejemplo["campana"]
        )
        nuevo = dict(ejemplo)
        nuevo["prediccion"] = max(0, round(pred))
        nuevo["prediccion_decimal"] = f"{pred:.2f}"
        ejemplos.append(nuevo)

    return render_template(
        "index.html",
        valores=valores,
        resultado=resultado,
        error=error,
        metricas=MODELO["metricas"],
        ejemplos=ejemplos,
        explicaciones=explicaciones,
        conclusion=conclusion,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)