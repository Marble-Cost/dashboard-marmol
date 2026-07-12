import os
from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
# Permite que tu index.html lea los datos sin bloqueos de seguridad
CORS(app)

# Enlace de descarga directa en formato CSV de tu Google Sheet 'Benchmarks_Industria_Piedra_2025'
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1lptVa5bps0bKte-VUzgekZuTfE--5tdxo2z7ohMZA-s/export?format=csv"

@app.route('/api/benchmarks', methods=['get'])
def obtener_benchmarks():
    try:
        # Python lee la base de datos directamente desde Google Sheets
        df = pd.read_csv(SHEET_CSV_URL)
        
        # Convierte la tabla limpia en formato JSON para el frontend
        datos_json = df.to_dict(orient='records')
        return jsonify(datos_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Configuración requerida para que funcione en servidores en la nube
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=puerto)