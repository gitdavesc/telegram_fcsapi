import requests
import os
import json
from datetime import datetime

API_KEY = os.environ["FCS_API_KEY"]
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

CHANNEL = "@canaldolarperu"

ESTADO_FILE = "estado.json"

def es_feriado_peru():
try:
año = datetime.now().year
hoy = datetime.now().strftime("%Y-%m-%d")

```
    r = requests.get(
        f"https://date.nager.at/api/v3/PublicHolidays/{año}/PE",
        timeout=20
    )

    feriados = r.json()

    return any(f["date"] == hoy for f in feriados)

except Exception as e:
    print(f"No se pudo verificar feriados: {e}")
    return False
```

def obtener_par(symbol):
r = requests.get(
"https://api-v4.fcsapi.com/forex/latest",
params={
"symbol": symbol,
"access_key": API_KEY
},
timeout=20
)

```
r.raise_for_status()

data = r.json()

if "response" not in data or len(data["response"]) == 0:
    raise Exception(f"No hay datos para {symbol}")

return float(data["response"][0]["active"]["c"])
```

def cargar_estado():
try:
with open(ESTADO_FILE, "r") as f:
return json.load(f)
except:
return {}

def guardar_estado(data):
with open(ESTADO_FILE, "w") as f:
json.dump(data, f, indent=2)

def variacion_pct(actual, base):
return ((actual - base) / base) * 100

if es_feriado_peru():
print("Feriado Perú. No se ejecuta.")
exit()

estado = cargar_estado()

hoy = datetime.now().strftime("%Y-%m-%d")

if estado.get("fecha") != hoy:
estado = {
"fecha": hoy,
"primer_envio_realizado": False,
"referencia": {}
}

pares = {
"USDPEN": "Dólar estadounidense / Sol peruano",
"CLPPEN": "Peso chileno / Sol peruano"
}

mensajes = []

primera_corrida = not estado.get("primer_envio_realizado", False)

for ticker, nombre in pares.items():

```
try:

    actual = obtener_par(ticker)

    if primera_corrida:

        estado["referencia"][ticker] = actual

        mensajes.append(
            f"💱 {ticker} ({nombre})\n"
            f"Actual: {actual}"
        )

    else:

        base = estado["referencia"].get(ticker)

        if base is None:
            estado["referencia"][ticker] = actual
            continue

        cambio = variacion_pct(actual, base)

        print(
            f"{ticker} | Base={base} | "
            f"Actual={actual} | Cambio={cambio:.2f}%"
        )

        if abs(cambio) >= 1:

            emoji = "📈" if cambio > 0 else "📉"

            mensajes.append(
                f"{emoji} {ticker} ({nombre})\n"
                f"Actual: {actual}\n"
                f"Hoy fuerte cambio: {cambio:.2f}%"
            )

except Exception as e:
    print(f"Error en {ticker}: {e}")
```

if primera_corrida:
estado["primer_envio_realizado"] = True

guardar_estado(estado)

if mensajes:

```
texto = "\n\n".join(mensajes)

r1 = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": texto
    },
    timeout=20
)

print("Chat:", r1.text)

r2 = requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHANNEL,
        "text": texto
    },
    timeout=20
)

print("Canal:", r2.text)

print(texto)
```

else:

```
print("Sin cambio >= 1%")
```
