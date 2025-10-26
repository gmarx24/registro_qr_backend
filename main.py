from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from google.oauth2 import service_account
from datetime import datetime
import pygame

# Inicializar sonido
pygame.mixer.init()
pygame.mixer.Sound("entry_sound.wav")

app = Flask(__name__)
CORS(app)

# Conectar con Google Sheets
SCOPE = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]
CREDS = service_account.Credentials.from_service_account_file(
    "service_account.json", scopes=SCOPE)
gc = gspread.authorize(CREDS)

SPREADSHEET_NAME = "Registro_Vehiculos"

try:
    sh = gc.open(SPREADSHEET_NAME)
except Exception as e:
    print("Error al abrir Google Sheets:", e)


@app.route("/registrar", methods=["POST"])
def registrar_vehiculo():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No se recibieron datos"}), 400

    try:
        codigo = data["codigo"]
        placa = data["placa"]
        tipo_unidad = data["tipo_unidad"]
        sub_contrata = data["sub_contrata"]
        operador = data["operador"]
        hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Verificar si la hoja existe o crear una nueva
        if tipo_unidad not in [ws.title for ws in sh.worksheets()]:
            sh.add_worksheet(title=tipo_unidad, rows="100", cols="10")
            ws = sh.worksheet(tipo_unidad)
            ws.append_row(["Código", "Placa", "Tipo de Unidad",
                          "Sub Contrata", "Operador", "Fecha y Hora"])
        else:
            ws = sh.worksheet(tipo_unidad)

        # Registrar los datos
        ws.append_row([codigo, placa, tipo_unidad,
                      sub_contrata, operador, hora_actual])
        pygame.mixer.Sound("entry_sound.wav").play()

        return jsonify({"status": "ok", "message": "Registro exitoso"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
