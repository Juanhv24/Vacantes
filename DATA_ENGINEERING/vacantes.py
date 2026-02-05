import os
import time
import urllib.parse
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import create_engine, text

# 1. CARGA DE CONFIGURACIÓN
load_dotenv()

def obtener_engine():
    usuario = os.getenv('DB_USER')
    password_plana = os.getenv('DB_PASSWORD')
    password_escapada = urllib.parse.quote_plus(password_plana)
    url_conexion = f"postgresql://{usuario}:{password_escapada}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(url_conexion)

def configurar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def iniciar_scraping():
    engine = obtener_engine()
    driver = configurar_driver()
    wait = WebDriverWait(driver, 15)
    page = 1
    total = 0
    
    try:
        while page <= 15:
            print(f"\n--- 🔎 Procesando página {page} ---")
            driver.get(f"https://www.computrabajo.com.co/trabajo-de-data-en-bogota-dc?p={page}")
            
            try:
                ofertas = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article h1 a, a.js-o-link")))
                links_pagina = [o.get_attribute("href") for o in ofertas]
            except:
                break

            for link in links_pagina:
                try:
                    driver.get(link)
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fs24")))
                    time.sleep(2) 

                    # EXTRACCIÓN SIMPLIFICADA
                    titulo = driver.find_element(By.CLASS_NAME, "fs24").text
                    
                    try:
                        contenedor_oferta = driver.find_element(By.CSS_SELECTOR, 'div[div-link="oferta"]')
                        descripcion = contenedor_oferta.text
                    except:
                        descripcion = "No encontrada"

                    # GUARDADO (Sin la columna empresa)
                    with engine.connect() as conn:
                        query = text("""
                            INSERT INTO vacantes (titulo, descripcion, url_vacante) 
                            VALUES (:t, :d, :u)
                        """)
                        conn.execute(query, {"t": titulo, "d": descripcion, "u": link})
                        conn.commit()
                    
                    total += 1
                    print(f"✅ [{total}] {titulo}")

                except Exception:
                    continue
            
            page += 1
            if page % 3 == 0:
                driver.quit()
                driver = configurar_driver()
                wait = WebDriverWait(driver, 15)

    finally:
        driver.quit()
        print(f"\n🚀 PROCESO TERMINADO. Total: {total}")

if __name__ == "__main__":
    iniciar_scraping()