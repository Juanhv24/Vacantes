import os 
import time 
import urllib.parse
from dotenv import getenv 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy import create_engine, text 

# 1. Conexión 
load_dotenv()

def obtener_engine(): 
    usuario = os.getenv('DB_USER')
    password_plana = os.getenv('DB_PASSWORD')
    password_escapada = urllib.parse.quote_plus(password_plana)
    url_conexion = f"postgresql://{usuario}:{password_escapada}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(url_conexion)

def configurar_driver(): 
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 2. Scraping 
def iniciar_scraping_elempleo():
    engine = obtener_engine()
    driver = configurar_driver()
    wait = WebDriverWait(driver, 15)
    page = 1
    total = 0

    try: 
        while page <= 15:
            print (f'\n--- 🔎 El Empleo: Procesando página {page} ---')

            url_busqueda = f'https://www.elempleo.com/co/ofertas-empleo/bogota/trabajo-data/{page}'
            driver.get(url_busqueda)

            try: 
                offers = wait.until (EC.presence_of_all_elements_located((By.CLASS_NAME, 'js-offer-link')))
                page_links = [o.get_attribute('href') for o in offers]

                if not page_links:
                    print ('No se encontraron más links. Fin del portal.')

            except: 
                print ('No se pudo cargar la lista de ofertas en esta página.')
                break

            for link in page_links: 
                try:
                    driver.get(link)
                    wait.until (EC.presence_of_element_located((By.TAG_NAME, 'h1')))
                    time.sleep(2)

                    titulo = driver.find_element(By.TAG_NAME, 'h1').text

                    try: 
                        