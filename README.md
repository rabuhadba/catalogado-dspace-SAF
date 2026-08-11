# Creador y Catalogador SAF para DSpace

Herramienta "Todo en Uno" escrita en Python que permite automatizar la creación de paquetes **Simple Archive Format (SAF)** para importar ítems a DSpace, incluyendo una fase de catalogación impulsada por inteligencia artificial (OpenAI).

## 🚀 Características
- **Catalogación con IA integrada:** Analiza imágenes mediante OpenAI para extraer metadatos de forma automatizada y con lenguaje bibliográfico estricto.
- **Generador Nativo en Python:** Emula el funcionamiento de la herramienta oficial `SAFBuilder` de Java, permitiéndote generar tu paquete de importación sin dependencias externas de Java.
- **Mapeo Inteligente:** Traduce dinámicamente cualquier columna de un CSV (ej. `dc.title.alternative`, `fia.region`) en su archivo XML correspondiente (`dublin_core.xml`, `metadata_fia.xml`, etc.).
- **Soporte Multivalor:** Separa automáticamente los valores por esquema (utilizando el delimitador `||`).
- **Asignación de Colección:** Permite incluir el archivo de `collections` con el Handle directamente en los ítems de manera interactiva.

## 📋 Requisitos
Necesitarás Python 3 y las siguientes dependencias instaladas:

```bash
pip install pandas openai python-dotenv Pillow
```

## ⚙️ Configuración inicial
1. Renombra o crea un archivo llamado `.env` en el directorio raíz del script.
2. Agrega tu clave de la API de OpenAI (necesaria para el proceso de catalogación):
```env
OPENAI_API_KEY="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```
*(Si no provees una API Key, el script omitirá la catalogación con IA y pasará directo a la generación de SAF basándose en los metadatos existentes de tu CSV).*

## 📁 Estructura del Input
Para que el script reconozca tu proyecto, debes tener una carpeta con esta estructura básica:

```text
Mi_Proyecto/
 ├── Un_archivo.csv (o Catalogo_OpenAI_Completo.csv)
 ├── foto_1.jpg
 ├── foto_2.jpg
 └── foto_3.png
```
*(Nota: Opcionalmente puedes guardar tus imágenes dentro de una subcarpeta llamada `Fotos/`).*

### Formato del CSV
- Obligatorio tener una columna llamada **`nombre archivo`** (en minúscula) con el nombre exacto de la imagen correspondiente.
- Usa los prefijos de DSpace en el encabezado para los metadatos (ej: `dc.description`, `dc.subject`, `dc.type`).

## 🛠️ Modo de Uso
Ejecuta el script desde tu terminal:

```bash
python creador_saf.py
```

El script te guiará paso a paso:
1. Te pedirá elegir la carpeta de red a copiar, o te listará los proyectos locales que tengas.
2. Te preguntará si quieres añadir el Handle para el archivo `collections` de forma general.
3. Si el CSV tiene celdas vacías, **te preguntará si quieres catalogar las imágenes pendientes con OpenAI**.
4. ¡El script hará todo el trabajo! Dejará tus paquetes listos dentro de una carpeta llamada `SAF/` en el directorio de tu proyecto.
