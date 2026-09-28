"""
Scraper de historial de Loteka (Quiniela) desde Conectate.com.do
Usa Playwright para simular un navegador real y evitar el bloqueo 403.
Guarda los resultados en resultados_loteka.json dentro del propio repositorio.
"""

import json
import time
from datetime import date, timedelta
from playwright.sync_api import sync_playwright

URL_BASE = "https://www.conectate.com.do/loterias/loteka/quiniela-mega-decenas/"
ARCHIVO_SALIDA = "resultados_loteka.json"

FECHA_INICIO = date(2023, 1, 1)   # ajustar segun cuantos anos quieras traer
FECHA_FIN = date.today()


def cargar_datos_existentes():
    try:
        with open(ARCHIVO_SALIDA, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def guardar_datos(datos):
    with open(ARCHIVO_SALIDA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def extraer_numeros_de_pagina(pagina):
    """
    Busca en el HTML ya renderizado los numeros ganadores.
    OJO: los selectores (clases/IDs) hay que ajustarlos una vez veamos
    el HTML real que devuelve el sitio para una fecha con resultado.
    """
    try:
        texto = pagina.inner_text("body")
    except Exception:
        return None
    return texto  # de momento devolvemos el texto crudo para inspeccionarlo


def main():
    datos = cargar_datos_existentes()
    fechas_ya_guardadas = {d["fecha"] for d in datos}

    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )

        fecha_actual = FECHA_INICIO
        while fecha_actual <= FECHA_FIN:
            fecha_texto = fecha_actual.isoformat()

            if fecha_texto in fechas_ya_guardadas:
                fecha_actual += timedelta(days=1)
                continue

            url_con_fecha = f"{URL_BASE}?fecha={fecha_texto}"

            try:
                pagina.goto(url_con_fecha, timeout=30000)
                pagina.wait_for_timeout(2000)
                contenido = extraer_numeros_de_pagina(pagina)

                datos.append({
                    "loteria": "Loteka - Quiniela",
                    "fecha": fecha_texto,
                    "contenido_crudo": contenido
                })
                fechas_ya_guardadas.add(fecha_texto)
                print(f"OK {fecha_texto}")

            except Exception as e:
                print(f"ERROR en {fecha_texto}: {e}")

            guardar_datos(datos)
            time.sleep(1)
            fecha_actual += timedelta(days=1)

        navegador.close()


if __name__ == "__main__":
    main()
