# Creador y Catalogador SAF para DSpace

Este es un script en Python que permite automatizar la creacion de paquetes Simple Archive Format (SAF) para importar items a DSpace. Ademas, incluye una fase automatizada de catalogacion utilizando inteligencia artificial (OpenAI).

## Caracteristicas principales
- Catalogacion automatica: Analiza imagenes mediante OpenAI para extraer metadatos de forma automatizada y con lenguaje bibliografico estricto, sin que tengas que escribirlos uno por uno.
- Generador de SAF directo: Emula el funcionamiento de la herramienta oficial SAFBuilder de Java, permitiendote generar tu paquete de importacion sin necesidad de instalar ni depender de Java.
- Mapeo inteligente: Traduce automaticamente cualquier columna de un Excel/CSV (por ejemplo, dc.title o fia.region) en los archivos XML que DSpace necesita para entender los datos.

---

## Guia paso a paso para comenzar

Si no tienes experiencia programando, sigue estos pasos al pie de la letra para usar el script:

### 1. Preparar el entorno de trabajo
1. Abre este proyecto en Visual Studio Code.
2. Abre la terminal de Visual Studio Code. Para hacerlo, presiona las teclas `CTRL + Ñ` (o `CTRL + Shift + \`` dependiendo de tu teclado), o ve al menu superior "Terminal" > "Nuevo Terminal".
3. En la terminal que aparece abajo, escribe el siguiente comando y presiona Enter para instalar las dependencias necesarias:
   ```bash
   pip install pandas openai python-dotenv Pillow
   ```

### 2. Configurar la clave de Inteligencia Artificial
Para que el script pueda "ver" las imagenes y describirlas, necesita conectarse a OpenAI.
1. En el panel de la izquierda (donde se ven los archivos), haz clic derecho y selecciona "Nuevo archivo".
2. Nombralo exactamente `.env` (no olvides el punto al inicio).
3. Abre ese archivo `.env` y pega tu clave de API de la siguiente manera:
   ```env
   OPENAI_API_KEY="sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
   ```
   *Nota: Si no haces este paso, el script no podra catalogar con IA, pero si podra armar el SAF asumiendo que tu CSV ya tiene toda la informacion llena.*

### 3. Preparar tus archivos (Imagenes y CSV)
El script necesita saber donde estan tus fotos y tu tabla de datos. Para que funcione sin problemas, pon tus archivos organizados de la siguiente forma dentro de una carpeta:

```text
Nombre_de_tu_Proyecto/
 ├── Catalogo_Datos.csv (tu archivo con la informacion)
 ├── foto_1.jpg
 ├── foto_2.jpg
 └── foto_3.png
```

Reglas muy importantes para tu archivo CSV:
- Debe estar guardado como archivo CSV (separado por comas), no como libro de Excel (.xlsx).
- Debe tener obligatoriamente una columna llamada **nombre archivo** (todo en minuscula), la cual debe contener el nombre exacto de la foto (por ejemplo: foto_1.jpg).
- Los encabezados para los datos deben usar el formato de DSpace (ejemplo: dc.description, dc.subject).

### 4. Ejecutar el script
Una vez tengas todo listo, vuelve a la terminal de Visual Studio Code (`CTRL + Ñ`), escribe lo siguiente y presiona Enter:

```bash
python creador_saf.py
```

El programa se iniciara y te ira guiando paso a paso mediante preguntas en pantalla:
1. Te pedira ingresar la ruta de la carpeta donde tienes tus fotos y tu CSV (puedes copiar la ruta y pegarla).
2. Te preguntara si quieres asociar todas las imagenes a una Coleccion en especifico de DSpace mediante un Handle (por ejemplo, 12345/6).
3. Si a tu CSV le faltan los titulos o descripciones, el programa detectara esto y te preguntara si quieres que la IA procese y describa las fotos faltantes.

Cuando el programa termine, encontraras una nueva carpeta llamada "SAF" lista para ser importada directamente a tu servidor de DSpace.
