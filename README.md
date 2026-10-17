# SENATI — Caso 02 | AgroRuta: sistema de estimación de costos de transporte agrícola

Proyecto académico con **regresión lineal múltiple, Python, Scikit-learn, Flask, HTML y CSS**. Se basa en los **130 viajes simulados** del material original proporcionado por el instructor.

## Archivos

- `02_Caso_02_Resuelto.ipynb`: respuestas razonadas del caso, entrenamiento, métricas, pruebas y conclusiones.
- `datos.csv`: conjunto de datos original (simulado).
- `entrenar_modelo.py`: reproduce la separación 80/20, entrena el modelo y escribe `modelo.json`.
- `modelo.json`: intercepto, coeficientes y resultados del conjunto de prueba.
- `app.py`: aplicación Flask; utiliza el JSON para estimar costos y valida rangos.
- `templates/index.html`, `static/estilos.css` y `static/*.svg`: interfaz de usuario, sin JavaScript.
- `evidencias/`: instrucciones para anexar capturas de las dos pruebas realizadas desde el navegador.

## Entrenar y comprobar resultados

```bash
pip install -r requirements_entrenamiento.txt
python entrenar_modelo.py
```

Se usa `train_test_split(..., test_size=0.20, random_state=42)`; se entrenan **104 filas** y se reservan **26 filas**. Resultados esperados del CSV original:

- MAE: aproximadamente **S/ 17.79**.
- R²: aproximadamente **0.9772**.
- Prueba obligatoria 1: 25 km, 400 kg, asfaltada → **S/ 133.79**.
- Prueba obligatoria 2: 100 km, 1200 kg, no asfaltada → **S/ 454.13**.

## Ejecutar la web localmente

```bash
pip install -r requirements.txt
python app.py
```

Abrir `http://localhost:5000`. Render usa:

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`
- Plan: **Free**

La app necesita tres valores: distancia (3–165 km), carga (50–2050 kg) y tipo de vía (0 asfaltada, 1 no asfaltada). Tiene ejemplos, desglose monetario y explicación educativa, **sin JavaScript**.

## Página web publicada

**URL:** https://senati-caso-02-transporte-agricola.onrender.com

Se debe pegar el enlace público final en el cuaderno `02_Caso_02_Resuelto.ipynb` y tomar las dos capturas obligatorias desde la web.

## Advertencia

Este modelo usa **datos simulados**. Las predicciones son aproximaciones de aprendizaje y no tarifas reales de transporte ni presupuestos comerciales. El MAE es un error medio, no garantiza un error menor en todos los viajes.