import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# URL de descarga CSV del documento Benchmarks_Industria_Piedra_2025
# (Corregida: antes estaba envuelta en sintaxis Markdown [url](url) y pd.read_csv fallaba)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1lptVa5bps0bKte-VUzgekZuTfE--5tdxo2z7ohMZA-s/export?format=csv"

# --- Caché en memoria (optimización de rendimiento) ---
# Sin esto, cada visita al dashboard descarga el Sheet completo de Google.
# Con caché de 10 minutos, Google Sheets se consulta como máximo 6 veces/hora.
_cache = {"datos": None, "timestamp": 0}
CACHE_TTL_SEGUNDOS = 600  # 10 minutos


@app.route('/api/benchmarks', methods=['GET'])
def obtener_benchmarks():
    try:
        ahora = time.time()

        # Servir desde caché si sigue vigente
        if _cache["datos"] is not None and (ahora - _cache["timestamp"]) < CACHE_TTL_SEGUNDOS:
            return jsonify(_cache["datos"])

        df = pd.read_csv(SHEET_CSV_URL)

        # Reemplazar NaN por None: NaN no es JSON válido y rompe
        # el respuesta.json() del navegador de forma silenciosa
        df = df.where(pd.notnull(df), None)

        datos_json = df.to_dict(orient='records')

        _cache["datos"] = datos_json
        _cache["timestamp"] = ahora

        return jsonify(datos_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    # Endpoint liviano para monitoreo (útil con UptimeRobot para
    # mantener despierto el servicio en el plan gratuito de Render)
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
