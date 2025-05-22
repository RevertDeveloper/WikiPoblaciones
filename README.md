# WikiPoblaciones

**WikiPoblaciones** es una aplicación de consola en Python que permite consultar de forma interactiva la población, superficie y densidad de cualquier ciudad o municipio del mundo utilizando datos extraídos en tiempo real desde Wikipedia.

## Descripción

Esta herramienta facilita la búsqueda de información demográfica de ciudades y municipios, mostrando los datos más relevantes de manera amigable y colorida en la terminal. Si el nombre introducido corresponde a varias localidades (página de desambiguación), el usuario puede elegir la opción correcta. Además, la aplicación es capaz de extraer información adicional como la superficie y la densidad de población, incluso si no están en la tabla principal de Wikipedia.

## Características

- Consulta de población, superficie y densidad de cualquier localidad.
- Extracción automática y robusta de datos desde Wikipedia.
- Manejo de páginas de desambiguación con selección interactiva.
- Colores y mensajes amigables en la terminal.
- Manejo de errores y timeouts en las peticiones HTTP.

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tuusuario/WikiPoblaciones.git
   cd WikiPoblaciones
   ```

2. Instala las dependencias necesarias:

   ```bash
   pip install requests beautifulsoup4 colorama
   ```

## Uso

Ejecuta el script principal:

```bash
python 3_Poblacion_Habitantes_Scraping.py
```

Sigue las instrucciones en pantalla para introducir el nombre de la población que deseas consultar. Escribe `salir` para terminar el programa.

## Ejemplo

```
👉  Introduce el nombre de la población (o escribe 'salir' para terminar): Madrid

🔍 Consultando la página: https://es.wikipedia.org/wiki/Madrid

🏙️  La población de Madrid es: 3 305 408 hab. (2023)
📏 Superficie: 604,3 km²
🧮 Densidad: 5 470 hab./km²
```

## Autor

Desarrollado por RevertDev
