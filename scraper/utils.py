import requests
from bs4 import BeautifulSoup

def scrapear_libros(busqueda):
    """ Descarga el catálogo de Books to Scrape y filtra por el término de búsqueda"""
    # URL de búsqueda
    url_base = "http://books.toscrape.com/index.html"
    
    # Headers para parecer un navegador real (importante para que no bloquee la interacción)
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    # }

    try:
        response = requests.get(url_base)
        response.raise_for_status() # Lanza error si falla la conexión
        
        soup = BeautifulSoup(response.text, 'html.parser')
        resultados = []

        # En BooksToScrape, cada libro es un <article class="product_pod">
        libros = soup.find_all('article', class_='product_pod')

        for libro in libros:
            # 1. Extraer Título
            # El título completo está en el atributo 'title' del enlace dentro de h3
            tag_titulo = libro.find('h3').find('a')
            titulo = tag_titulo['title']
            
            # ⚠️ FILTRO MANUAL: Si la búsqueda NO está en el título, saltamos este libro
            if busqueda.lower() not in titulo.lower():
                continue

            # 2. Extraer Precio
            precio = libro.find('p', class_='price_color').text
            
            # 3. Extraer Disponibilidad
            stock = libro.find('p', class_='instock availability').text.strip()

            resultados.append({
                'titulo': titulo,
                'precio': precio,
                'stock': stock,
                'sitio': 'Books to Scrape'
            })

        return resultados

    except Exception as e:
        print(f"Error en scraping: {e}")
        return []


def scrapear_jedbangers(busqueda):
    url_base = "https://tienda.jedbangers.com.ar/search/"
    params = {'q': busqueda}
    
    # Headers para simular ser un humano
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        print(f"--- INICIANDO SCRAPING ---")
        print(f"URL: {url_base}?q={busqueda}")
        
        response = requests.get(url_base, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        resultados = []

        # 1. BUSCAR CONTENEDORES
        # Prueba las clases más comunes de Tienda Nube actualizadas
        clases_contenedor = ['js-item-product', 'item-product', 'product-item', 'item']
        productos_html = []
        
        for clase in clases_contenedor:
            productos_html = soup.find_all('div', class_=clase)
            if productos_html:
                print(f"✅ ÉXITO: Se encontraron {len(productos_html)} contenedores con la clase '{clase}'")
                break
        
        if not productos_html:
            print("❌ ERROR: No se encontraron contenedores de productos. El HTML puede haber cambiado.")
            return []

        # 2. EXTRAER DATOS
        print("--- INTENTANDO EXTRAER DATOS ---")
        
        for i, item in enumerate(productos_html):
            try:
                # A. TÍTULO (Varias estrategias)
                tag_titulo = (
                    item.find('a', class_='item-name') or 
                    item.find('div', class_='item-name') or 
                    item.find('h3') or
                    item.find('a', title=True) # Cualquier enlace con título
                )
                
                if not tag_titulo:
                    print(f"⚠️ Item {i+1}: Saltado (No se encontró Título)")
                    continue

                titulo = tag_titulo.get_text(strip=True) or tag_titulo.get('title')
                link_producto = tag_titulo.get('href')
                
                # Corregir enlace si es relativo
                if link_producto and not link_producto.startswith('http'):
                    link_producto = 'https://tienda.jedbangers.com.ar' + link_producto

                # B. PRECIO
                tag_precio = (
                    item.find('span', class_='js-price-display') or 
                    item.find('span', class_='item-price') or 
                    item.find('div', class_='price') or
                    item.find('span', class_='price')
                )
                
                precio = tag_precio.get_text(strip=True) if tag_precio else "Consultar"

                # C. IMAGEN
                tag_img = item.find('img')
                imagen_url = ""
                if tag_img:
                    # Priorizamos data-srcset o data-src que usan para lazy loading
                    imagen_url = tag_img.get('data-srcset') or tag_img.get('data-src') or tag_img.get('src')
                    # A veces vienen varios links separados por coma, tomamos el primero
                    if imagen_url:
                        imagen_url = imagen_url.split(' ')[0] 
                        if imagen_url.startswith('//'):
                            imagen_url = 'https:' + imagen_url

                # Éxito al parsear este ítem
                resultados.append({
                    'titulo': titulo,
                    'precio': precio,
                    'link': link_producto,
                    'imagen': imagen_url,
                    'sitio': 'Jedbangers'
                })

            except Exception as e:
                print(f"❌ Error al procesar ítem {i+1}: {e}")
                continue

        print(f"--- FIN: Se extrajeron {len(resultados)} productos válidos ---")
        return resultados

    except Exception as e:
        print(f"❌ Error crítico de conexión/parsing: {e}")
        return []