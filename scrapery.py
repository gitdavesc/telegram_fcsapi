import requests
import os
import json

API_KEY = os.environ["FCS_API_KEY"]
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

ESTADO_FILE = "estado.json"

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

return float(data["response"][0]["c"])
```

def cargar_estado():
try:
with open(ESTADO_FILE, "r") as f:
return json.load(f)
except:
return {}

def guardar_estado(data):
with open(ESTADO_FILE, "w") as f:
json.dump(data, f)

def variacion_pct(actual, anterior):
return ((actual - anterior) / anterior) * 100

estado = cargar_estado()

pares = [
"USDPEN",
"CLPPEN"
]

mensajes = []

for par in pares:

```
actual = obtener_par(par)

if par not in estado:
    estado[par] = actual
    continue

anterior = estado[par]

cambio = variacion_pct(actual, anterior)

if abs(cambio) >= 1:

    emoji = "📈" if cambio > 0 else "📉"

    mensajes.append(
        f"{emoji} {par}\n"
        f"Anterior: {anterior}\n"
        f"Actual: {actual}\n"
        f"Variación: {cambio:.2f}%"
    )

    estado[par] = actual
```

guardar_estado(estado)

if mensajes:

```
texto = "\n\n".join(mensajes)

requests.post(
    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": texto
    },
    timeout=20
)

print(texto)
```

else:
print("Sin variaciones >= 1%")
