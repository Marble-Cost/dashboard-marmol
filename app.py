import os
import time
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# REGLA CRÍTICA: Forzar a Flask a respetar los caracteres en español (UTF-8) en la respuesta JSON
app.config['JSON_AS_ASCII'] = False 

# URL directa a tu Google Sheets
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1lptVa5bps0bKte-VUzgekZuTfE--5tdxo2z7ohMZA-s/export?format=csv"

_cache = {"datos": None, "timestamp": 0}
CACHE_TTL_SEGUNDOS = 600

@app.route('/api/benchmarks', methods=['GET'])
def obtener_benchmarks():
    try:
        ahora = time.time()

        # Servir desde caché si sigue vigente (optimización)
        if _cache["datos"] is not None and (ahora - _cache["timestamp"]) < CACHE_TTL_SEGUNDOS:
            return jsonify(_cache["datos"])

        # Lectura directa desde Google Sheets
        df = pd.read_csv(SHEET_CSV_URL)
        
        # Prevenir errores de parseo JSON en el navegador manejando los nulos
        df = df.where(pd.notnull(df), None)

        datos_json = df.to_dict(orient='records')

        _cache["datos"] = datos_json
        _cache["timestamp"] = ahora

        return jsonify(datos_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)
