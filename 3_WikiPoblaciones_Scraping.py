import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from colorama import init, Fore, Style
import re

# Inicializa colorama para colorear la salida en terminales compatibles (especialmente en Windows)
init(autoreset=True)

def mostrar_banner():
    """
    Muestra un banner decorativo en la consola para dar la bienvenida al usuario.
    Utiliza colores y estilos para mejorar la presentación.
    """
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}
╔═════════════════════════════════════════════════════╗
║  🌍 Buscador de Poblaciones - Wikipedia Edition  🌍 ║
╠═════════════════════════════════════════════════════╣
║   ¡Descubre la población de tu ciudad favorita!     ║
║          Disfruta de una experiencia amigable       ║
╚═════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """
    print(banner)

def obtener_pagina_wikipedia(poblacion):
    """
    Busca la página de Wikipedia correspondiente a la población introducida.
    - Primero intenta acceder directamente a la URL de la población.
    - Si no existe, realiza una búsqueda en Wikipedia.
    - Todas las peticiones tienen un timeout de 10 segundos.
    Devuelve el HTML de la página encontrada y la URL usada.
    """
    # Formatea el nombre de la población para construir la URL directa
    poblacion_formateada = poblacion.title().replace(" ", "_")
    url_directa = f"https://es.wikipedia.org/wiki/{quote(poblacion_formateada)}"
    
    try:
        # Intenta acceder a la página directa
        response = requests.get(url_directa, timeout=10)
        if response.status_code == 200:
            return response.text, url_directa
        else:
            # Si no existe, busca usando el motor de búsqueda de Wikipedia
            print(Fore.YELLOW + "😮 No se encontró la página directa, buscando a través de Wikipedia...")
            url_busqueda = f"https://es.wikipedia.org/w/index.php?search={quote(poblacion)}"
            response = requests.get(url_busqueda, timeout=10)
            if response.status_code == 200:
                return response.text, response.url
            else:
                print(Fore.RED + "🚨 Error al acceder a Wikipedia. ¡Inténtalo de nuevo más tarde!")
                exit(1)
    except requests.exceptions.Timeout:
        print(Fore.RED + "🚨 Tiempo de espera agotado al conectar con Wikipedia. Comprueba tu conexión a internet.")
        exit(1)
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"🚨 Error al conectar con Wikipedia: {e}")
        exit(1)

def manejar_desambiguacion(soup, poblacion):
    """
    Si la página es de desambiguación, muestra las opciones disponibles y permite al usuario elegir.
    Devuelve el HTML de la opción seleccionada o None si se cancela.
    """
    print(Fore.YELLOW + "🤔 Se detectó página de desambiguación. Hay múltiples opciones:")
    items = soup.select(".mw-parser-output > ul li")
    
    opciones_validas = []
    # Recorre las opciones de la lista y las muestra al usuario
    for idx, item in enumerate(items, 1):
        texto_item = item.get_text(" ", strip=True)
        link = item.find("a", href=True)
        if link and not link['href'].startswith('#'):
            print(f"{Fore.CYAN}{idx}.{Style.RESET_ALL} {texto_item}")
            opciones_validas.append((idx, "https://es.wikipedia.org" + link['href'], texto_item))
    
    if not opciones_validas:
        print(Fore.RED + "😕 No se encontraron opciones válidas en la página de desambiguación.")
        return None
        
    while True:
        try:
            eleccion = input(Fore.GREEN + "Elige una opción (número) o '0' para cancelar: ")
            if eleccion == '0':
                return None
                
            eleccion = int(eleccion)
            for idx, url, texto in opciones_validas:
                if idx == eleccion:
                    print(Fore.GREEN + f"Seleccionaste: {texto}")
                    try:
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            return response.text
                    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
                        print(Fore.RED + "🚨 Error al acceder a la página seleccionada.")
                        return None
            
            print(Fore.RED + "❌ Opción no válida. Intenta de nuevo.")
        except ValueError:
            print(Fore.RED + "❌ Por favor, introduce un número válido.")

def extraer_info_adicional(soup):
    """
    Extrae información adicional de la infobox o del contenido principal:
    - Superficie
    - Densidad de población
    Devuelve un diccionario con los datos encontrados.
    """
    info = {"superficie": None, "densidad": None}
    infobox = soup.find("table", {"class": "infobox"})
    
    # Busca en la infobox
    if infobox:
        for fila in infobox.find_all("tr"):
            if fila.th and fila.td:
                etiqueta = fila.th.get_text(" ", strip=True).lower()
                if "superficie" in etiqueta:
                    info["superficie"] = fila.td.get_text(" ", strip=True)
                elif "densidad" in etiqueta:
                    info["densidad"] = fila.td.get_text(" ", strip=True)
    
    # Si no encuentra, busca en los primeros párrafos
    if not info["superficie"] or not info["densidad"]:
        parrafos = soup.select(".mw-parser-output > p")
        for p in parrafos:
            texto = p.get_text(" ", strip=True).lower()
            if not info["superficie"] and "superficie" in texto and re.search(r'\d+\s*km', texto):
                match = re.search(r'superficie\s*(?:de|es|:)?\s*([^\.;]+(?:km|hectáreas|ha))', texto, re.IGNORECASE)
                if match:
                    info["superficie"] = match.group(1).strip()
            
            if not info["densidad"] and "densidad" in texto and re.search(r'\d+\s*hab', texto):
                match = re.search(r'densidad\s*(?:de|es|:)?\s*([^\.;]+(?:hab|habitantes))', texto, re.IGNORECASE)
                if match:
                    info["densidad"] = match.group(1).strip()
    
    return info

def extraer_poblacion(html):
    """
    Extrae la población de la página HTML.
    - Busca primero en la infobox.
    - Si no existe, permite elegir al usuario en caso de desambiguación.
    - Si tampoco, intenta buscar en el contenido principal.
    Devuelve la población y un diccionario con información adicional.
    """
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.find("table", {"class": "infobox"})
    
    # Si no hay infobox, puede ser desambiguación o buscar en el contenido principal
    if not infobox:
        if "puede referirse a:" in soup.text.lower():
            nuevo_html = manejar_desambiguacion(soup, "")
            if nuevo_html:
                return extraer_poblacion(nuevo_html)
            else:
                return None, {}
        else:
            # Busca en los párrafos principales
            poblacion = buscar_poblacion_en_contenido(soup)
            if poblacion:
                info_adicional = extraer_info_adicional(soup)
                return poblacion, info_adicional
            print(Fore.YELLOW + "😕 No se encontró la infobox en la página.")
            return None, {}

    # Busca filas de la infobox relacionadas con población o habitantes
    candidates = []
    for fila in infobox.find_all("tr"):
        if fila.th and fila.td:
            etiqueta = fila.th.get_text(" ", strip=True).lower()
            if "población" in etiqueta or "habitantes" in etiqueta:
                texto = fila.td.get_text(" ", strip=True)
                if re.search(r'\d', texto):
                    candidates.append(texto)
    
    # Prioriza los candidatos que incluyan "hab"
    for cand in candidates:
        if "hab" in cand.lower():
            info_adicional = extraer_info_adicional(soup)
            return cand, info_adicional

    # Si no, elige el candidato con más dígitos
    best_candidate = None
    max_digits = 0
    for cand in candidates:
        digits = re.findall(r'\d+', cand)
        total_digits = sum(len(d) for d in digits)
        if total_digits > max_digits:
            max_digits = total_digits
            best_candidate = cand
    
    # Si no hay nada en la infobox, busca en el contenido principal
    if not best_candidate:
        best_candidate = buscar_poblacion_en_contenido(soup)
    
    info_adicional = extraer_info_adicional(soup)
    return best_candidate, info_adicional

def buscar_poblacion_en_contenido(soup):
    """
    Busca información de población en los primeros párrafos del artículo.
    Utiliza expresiones regulares para encontrar frases típicas de población.
    """
    parrafos = soup.select(".mw-parser-output > p")
    for p in parrafos[:5]:  # Solo los primeros párrafos para eficiencia
        texto = p.get_text(" ", strip=True).lower()
        if ("población" in texto or "habitantes" in texto) and re.search(r'\d+\s*hab', texto):
            match = re.search(r'(?:población|habitantes)[^\.;]*?(\d[\d\s\.\,]*\s*hab[^\d]*(?:\d{4})?)', texto)
            if match:
                return match.group(1).strip()
    return None

def main():
    """
    Función principal del programa.
    - Muestra el banner.
    - Pide al usuario el nombre de la población.
    - Busca y muestra la población, superficie y densidad.
    - Permite salir escribiendo 'salir'.
    """
    mostrar_banner()
    while True:
        mensaje = (Fore.CYAN + Style.BRIGHT +
                   "👉  Introduce el nombre de la población (o escribe 'salir' para terminar): " +
                   Style.RESET_ALL)
        poblacion = input(mensaje).strip()
        if poblacion.lower() == "salir":
            print(Fore.CYAN + "\n¡Hasta la próxima! 👋😊")
            break

        html, url_obtenida = obtener_pagina_wikipedia(poblacion)
        print(Fore.GREEN + f"\n🔍 Consultando la página: {url_obtenida}\n")

        poblacion_extraida, info_adicional = extraer_poblacion(html)
        if poblacion_extraida:
            print(Fore.MAGENTA + Style.BRIGHT +
                  f"🏙️  La población de {poblacion.title()} es: {poblacion_extraida}")
            
            # Muestra información adicional si está disponible
            if info_adicional["superficie"]:
                print(Fore.MAGENTA + f"📏 Superficie: {info_adicional['superficie']}")
            if info_adicional["densidad"]:
                print(Fore.MAGENTA + f"🧮 Densidad: {info_adicional['densidad']}")
            print()
        else:
            print(Fore.RED + "🚨 No se pudo extraer la información de población.\n")

if __name__ == "__main__":
    main()
