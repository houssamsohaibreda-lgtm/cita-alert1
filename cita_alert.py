"""
Cita previa alert (toma de huellas) - nسخة dyal GitHub Actions.
Kayt'khddem merra whda f kol run. Ghir kayssifet notification, makayhjezch.
Token w chat id kayjiw men GitHub Secrets (ماشي mktoubin f lfichier).
"""
import os
import sys
import requests
from playwright.sync_api import sync_playwright

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
TEST = os.environ.get("TEST") == "1"

# ====== BDDEL HADO ILA BGHITI ======
PROVINCIA = "Madrid"
TRAMITE_KEYWORD = "TOMA DE HUELLAS"
URL = "https://icp.administracionelectronica.gob.es/icpplus/index.html"
NO_CITAS = "no hay citas disponibles"
# ===================================


def notify(msg):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": msg},
        timeout=15,
    )
    print("Telegram:", r.status_code, r.text[:200])
    r.raise_for_status()


def check_once(page):
    """True = kayn cita, False = ma kaynach, None = mouchkil (captcha...)."""
    page.goto(URL, timeout=60000)
    page.select_option("#form", label=PROVINCIA)
    page.click("#btnAceptar")

    sel = page.locator("select#tramiteGrupo\\[0\\]")
    sel.wait_for(timeout=30000)
    options = sel.locator("option").all_inner_texts()
    match = next((o for o in options if TRAMITE_KEYWORD in o.upper()), None)
    if not match:
        print("Tramite ma tlaqach. Options:", options)
        return None
    sel.select_option(label=match)
    page.click("#btnAceptar")
    page.click("#btnEntrar")

    page.wait_for_load_state("networkidle")
    text = page.inner_text("body").lower()

    if "captcha" in text or "robot" in text:
        print("Captcha / blocage")
        return None
    if NO_CITAS in text:
        return False
    return True


def main():
    if TEST:
        notify("✅ Test: GitHub Actions + Telegram khddamin.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(locale="es-ES")
        page = ctx.new_page()
        try:
            result = check_once(page)
        except Exception as e:
            print("Error:", e)
            result = None
        browser.close()

    print("Result:", result)
    if result is True:
        notify("🚨 Yemken kayn cita! Dkhel db: " + URL)
    sys.exit(0)


if __name__ == "__main__":
    main()
