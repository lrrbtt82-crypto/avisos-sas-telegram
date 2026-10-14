import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup

URL = "https://administracion.gob.es/empleopublico/resultadosEmpleo/detalle-empleo?selectorServicio=bolsa_empleo&selectorget=215181"
INAP_URL = "https://sede.inap.gob.es/es/procedimientos-y-servicios/seleccion/escala-de-funcionarios-de-administracion-local-con-habilitacion-de-caracter-nacional/procesos-selectivos-vigentes/intervencion-tesoreria-categoria-de-entrada-acceso-libre-convocatoria-extraordinaria-oep-2023"

STATE_FILE = "state_inap.json"

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def obtener_seguimiento():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    texto = soup.get_text("\n", strip=True)

    inicio = texto.find("Seguimiento")

    if inicio == -1:
        raise Exception("No se encontró la sección Seguimiento")

    seguimiento = texto[inicio:]

    # Eliminamos posibles textos posteriores irrelevantes
    fin = seguimiento.find("(*)")
    if fin != -1:
        seguimiento = seguimiento[:fin]

    return seguimiento.strip()


def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": mensaje,
            "disable_web_page_preview": False,
        },
        timeout=30,
    )

    response.raise_for_status()


def cargar_estado():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_estado(huella):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"hash": huella},
            f,
            ensure_ascii=False,
            indent=2,
        )


def main():
    seguimiento = obtener_seguimiento()

    huella = hashlib.sha256(
        seguimiento.encode("utf-8")
    ).hexdigest()

    estado_anterior = cargar_estado()

    # Primera ejecución: guardar estado sin enviar aviso
    if estado_anterior is None:
        guardar_estado(huella)
        print("Primera ejecución: estado inicial guardado.")
        return

    # No hay cambios
    if estado_anterior.get("hash") == huella:
        print("No hay novedades.")
        return

    # Hay cambios
    mensaje = (
        "🔔 NUEVA ACTUALIZACIÓN: INTERVENCIÓN-TESORERÍA\n\n"
        "Se ha detectado un cambio en el seguimiento del proceso "
        "selectivo de Intervención-Tesorería, categoría de entrada.\n\n"
        f"🔗 Página oficial del INAP:\n{INAP_URL}\n\n"
        f"🔗 Seguimiento oficial:\n{URL}"
    )

    enviar_telegram(mensaje)

    guardar_estado(huella)

    print("¡Nueva actualización detectada y enviada a Telegram!")


if __name__ == "__main__":
    main()
