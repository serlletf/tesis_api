import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from selenium.webdriver.common.keys import Keys
import unicodedata
from selenium.common.exceptions import TimeoutException

API_URL = 'http://web:5000'  # URL de tu API

def get_webdriver():
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
    #opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--disable-features=IsolateOrigins,site-per-process")
    opts.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1920, 1080)  # Ajustar el tamaño de la ventana
    return driver

def clear_browser_cache(driver):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get('chrome://settings/clearBrowserData')
    time.sleep(2)
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3)  # Navegar en el menú y seleccionar "Todo"
    actions.perform()
    time.sleep(1)
    actions = webdriver.ActionChains(driver)
    actions.send_keys(Keys.TAB * 4 + Keys.ENTER)  # Navegar al botón de "Borrar datos" y hacer clic
    actions.perform()
    time.sleep(5)  # Esperar a que se complete el borrado
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

def obtener_productos_de_api():
    response = requests.get(f"{API_URL}/productos")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error al obtener productos de la API.")
        return []

def eliminar_tildes(texto):
    texto_normalizado = unicodedata.normalize('NFD', texto)
    texto_sin_tildes = ''.join(c for c in texto_normalizado if unicodedata.category(c) != 'Mn')
    return texto_sin_tildes

def buscar_info_santa_isabel(driver, productos):
    driver.get("https://www.santaisabel.cl/")  # Asegúrate de tener la URL correcta  
    time.sleep(5)

    for producto in productos:
        nombreProducto = producto["nombreProducto"]
        marcaProducto = producto["marcaProducto"]
        idProducto = producto["idProducto"]

        buscador = driver.find_element(By.XPATH, '(//input)[1]')
        buscador.send_keys(Keys.CONTROL + "a")  
        buscador.send_keys(Keys.DELETE) 
        buscador.send_keys(nombreProducto+" "+marcaProducto)
        button = driver.find_element(By.XPATH, '//button[@class = "new-header-search-submit"]')
        button.click() 


        try:
            element = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, "//h1[contains(text(),'No hay productos que')]"))
            )
            is_visible = element.is_displayed()
            return
        except:
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, "(//span[contains(text(),'Agregar a tus listas')])[2]"))
                )
                is_visible = element.is_displayed()
                preciotmp= driver.find_element(By.XPATH,'(//*[@id="scraping-tmp"])[2]')
                data_precio = {
                    "idProducto": idProducto,
                    "precio": float(preciotmp.text.replace('$', '').replace('.', '').replace(',', '.')),
                    "fecha": datetime.now().isoformat(),
                    "idSupermercado": 2,
                }
                requests.post(f"{API_URL}/precio", json=data_precio)               
            except:
                clickProduc = driver.find_element(By.XPATH,'(//a[@class = "product-card-name"])[1]')
                clickProduc.click()
                time.sleep(2)
                preciotmp= driver.find_element(By.XPATH,'(//*[@id="scraping-tmp"])[2]')
                data_precio = {
                    "idProducto": idProducto,
                    "precio": float(preciotmp.text.replace('$', '').replace('.', '').replace(',', '.')),
                    "fecha": datetime.now().isoformat(),
                    "idSupermercado": 2,
                }
                requests.post(f"{API_URL}/precio", json=data_precio)  
        time.sleep(2)

def buscar_info_unimarc(driver, productos):
    driver.get("https://www.unimarc.cl/")  
    time.sleep(5)

    for producto in productos:
        nombreProducto = producto["nombreProducto"]
        marcaProducto = producto["marcaProducto"]
        idProducto = producto["idProducto"]

        buscador = driver.find_element(By.XPATH, '(//input)[1]')
        buscador.send_keys(Keys.CONTROL + "a")  
        buscador.send_keys(Keys.DELETE) 
        buscador.send_keys(nombreProducto)
        button = driver.find_element(By.XPATH, '//*[@id="SearchCart"]')
        button.click()

        nombreProducto = eliminar_tildes(nombreProducto)
        nombreProducto = nombreProducto.lower()
        marcaProducto = marcaProducto.lower()

        try:
            element = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'¡Ups! Lo sentimos')]"))
            )
            is_visible = element.is_displayed()
            return
        except:
            try:
                clickProduc = driver.find_element(By.XPATH,"//p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + nombreProducto + "')    and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + "')   and contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '" + marcaProducto + "')]")
            except:
                time.sleep(2)
                clickProduc = driver.find_element(By.XPATH,'//*[@id="__next"]/div/main/div/div/div/section/div/div/div[1]')

            clickProduc.click()
            time.sleep(4)
 
            #precio = driver.find_element(By.XPATH,"(//article)[3]//p[contains(text(),'$')][1]")
            data_precio = {
                "idProducto": idProducto,
                #"precio": float(precio.text.replace('$', '').replace('.', '').replace(',', '.')),
                "fecha": datetime.now().isoformat(),
                "idSupermercado": 4,
            }
            requests.post(f"{API_URL}/precio", json=data_precio)  
            time.sleep(1)
            buttonClose = driver.find_element(By.XPATH, '//*[@id="__next"]/div/main/div/div/div/section/div/div/div[1]/article/div')
            buttonClose.click()
        time.sleep(2)

def scraping_y_envio_a_api():
    
    productos = obtener_productos_de_api()
    if not productos:
        return

    driver = get_webdriver()

    # Buscar productos en Santa Isabel
    buscar_info_santa_isabel(driver, productos)
    
    # Buscar productos en Unimarc
    buscar_info_unimarc(driver, productos)

    driver.quit()

def main():
    scraping_y_envio_a_api()
    
if __name__ == "__main__":
    main()
