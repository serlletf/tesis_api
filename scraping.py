import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime
import searchAPI
API_URL = 'http://web:5000'  # URL de tu API

def get_webdriver():
    opts = Options()
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--disable-features=IsolateOrigins,site-per-process")
    opts.add_argument("--remote-debugging-port=9222")
    return webdriver.Chrome(options=opts)

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def extract_format(name):
    match = re.search(r'\d+\s?[a-zA-Z]+', name)
    if match:
        return name.replace(match.group(), '').strip(), match.group().strip()
    else:
        return name, ''

def parse_category(title):
    parts = title.split(" | ")
    return parts[0] if parts else title

def scraping_and_transform(url, supermercado, idSupermercado):
    driver = get_webdriver()
    driver.get(url)

    xpaths = {
        "name": '//a[@class="product-card-name"]',
        "price": '//span[@class="prices-main-price"]',
        "brand": '//a[@class="product-card-brand"]'
    }

    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, xpaths["name"])))
    time.sleep(10)

    productos = {}
    for key, xpath in xpaths.items():
        values = []
        for attempt in range(3):
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                values = [element.text for element in elements]
                break
            except Exception as e:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise e
        productos[key] = values

    categoria = parse_category(driver.title)
    transform_data(productos, categoria, supermercado, idSupermercado)
    driver.quit()

def transform_data(productos, categoria, supermercado, idSupermercado):
    for nombre, precio, marca in zip(productos["name"], productos["price"], productos["brand"]):
        nombre, formato = extract_format(nombre)
        data_producto = {
            "nombreProducto": nombre,
            "marcaProducto": marca,
            "formatoProducto": formato,
            "categoriaProducto": categoria
        }
        response = requests.post(f"{API_URL}/producto", json=data_producto)  
        if response.status_code == 201:
            producto_id = response.json().get("idProducto")
            data_precio = {
                "idProducto": producto_id,
                "precio": float(precio.replace('$', '').replace('.', '').replace(',', '.')),
                "fecha": datetime.now().isoformat(),
                "idSupermercado": idSupermercado,
            }
            requests.post(f"{API_URL}/precio", json=data_precio)
        else:
            print(f"Error al guardar el producto: {response.status_code}, Respuesta: {response.text}")


def categorias(supermercado):
    idSupermercado = 1  # Ajustar según el ID del supermercado
    urls = [
        'https://www.jumbo.cl/lacteos',
        'https://www.jumbo.cl/despensa',
        'https://www.jumbo.cl/frutas-y-verduras',
        'https://www.jumbo.cl/limpieza',
        'https://www.jumbo.cl/carniceria',
        'https://www.jumbo.cl/bebidas-aguas-y-jugos',
        'https://www.jumbo.cl/congelados',
    ]
    
    for url in urls:
        scraping_and_transform(url, supermercado, idSupermercado)

def main():
    categorias("Jumbo")
    searchAPI.main()

if __name__ == "__main__":
    main()