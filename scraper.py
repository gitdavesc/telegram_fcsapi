import requests
import os
import json
from datetime import datetime

API_KEY = os.environ["FCS_API_KEY"]
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

ESTADO_FILE = "estado.json"


def es_feriado_peru():
    try:
        año = datetime.now().year
        hoy = datetime.now().strftime("%Y-%m-%d")

        r = requests.get(
            f"https://date.nager.at/api/v3/PublicHolidays/{año}/PE",
            timeout=20
        )

        feriados = r.json()

        return any(f["date"] == hoy for f in feriados)

    except Exception as e:
        print(f"No se pudo verificar feriados: {e}")
        return False


def obtener_par(symbol):
    r = requests.get(
        "https://api-v4.fcsapi.com/forex/latest",
        params={
            "symbol": symbol,
            "access_key": API_KEY
        },
        timeout=20
    )

    r.raise_for_status()

    data = r.json()

    if "response" not in data or len(data["response"]) == 0:
        raise Exception(f"No se obtuvo información para {symbol}")

    return float(data["response"][0]["c"])


def cargar_estado():
    try:
        with open(ESTADO_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def guardar_estado(data):
    with open(ESTADO_FILE, "w") as f:
        json.dump(data, f, indent=2)


def variacion_pct(actual, anterior):
    return ((actual - anterior) / anterior) * 100


if es_feriado_peru():
    print("Feriado en Perú. No se consulta FCS API.")
    exit()

estado = cargar_estado()

pares = [
    "USDPEN",
    "CLPPEN"
]

mensajes = []

for par in pares:

    try:
        actual = obtener_par(par)

        if par not in estado:
            estado[par] = actual
            print(f"Inicializando {par} = {actual}")
            continue

        anterior = estado[par]

        cambio = variacion_pct(actual, anterior)

        print(
            f"{par} | Anterior={anterior} | "
            f"Actual={actual} | Cambio={cambio:.2f}%"
        )

        if abs(cambio) >= 1:

            emoji = "📈" if cambio > 0 else "📉"

            mensajes.append(
                f"{emoji} {par}\n"
                f"Anterior: {anterior}\n"
                f"Actual: {actual}\n"
                f"Variación: {cambio:.2f}%"
            )

            estado[par] = actual

    except Exception as e:
        print(f"Error procesando {par}: {e}")

guardar_estado(estado)

if mensajes:

    texto = "\n\n".join(mensajes)

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": texto
        },
        timeout=20
    )

    print("Mensaje enviado:")
    print(texto)

else:
    print("Sin variaciones >= 1%")
