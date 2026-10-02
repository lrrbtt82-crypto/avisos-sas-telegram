import json, os
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://www.sspa.juntadeandalucia.es/servicioandaluzdesalud/profesionales/traslados/cuadro-de-evolucion-del-concurso-de-traslado-2025/enfermeroa"
STATE_FILE = Path("state.json")
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

def get_documents():
    r = requests.get(PAGE_URL, headers={"User-Agent": "SAS-document-watcher/1.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    docs = {}
    for a in soup.find_all("a", href=True):
        url = urljoin(PAGE_URL, a["href"].strip())
        if ".pdf" in url.lower():
            title = " ".join(a.get_text(" ", strip=True).split()) or "Nuevo documento PDF"
            docs[url] = {"url": url, "title": title}
    return list(docs.values())

def load_state():
    if not STATE_FILE.exists():
        return set()
    try:
        return set(json.loads(STATE_FILE.read_text(encoding="utf-8")).get("urls", []))
    except Exception:
        return set()

def save_state(urls):
    STATE_FILE.write_text(json.dumps({"urls": sorted(urls)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False},
        timeout=30,
    )
    r.raise_for_status()

def main():
    docs = get_documents()
    current = {d["url"] for d in docs}
    old = load_state()

    # First run = baseline, no alerts for documents already present.
    if not old:
        save_state(current)
        print(f"Baseline creada: {len(current)} PDF(s).")
        return

    new = [d for d in docs if d["url"] not in old]
    for d in new:
        send_telegram(f"🔔 NUEVO DOCUMENTO EN EL SAS\n\n📄 {d['title']}\n\n🔗 {d['url']}")
        print("Aviso enviado:", d["title"])

    save_state(old | current)
    print(f"Comprobados {len(docs)} PDF(s); nuevos: {len(new)}.")

if __name__ == "__main__":
    main()
