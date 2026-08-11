import os
import shutil
import pandas as pd
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image

def codificar_imagen(ruta_imagen):
    with open(ruta_imagen, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

prompt_sistema = """
Eres un documentalista experto catalogando un archivo fotográfico sobre un proyecto de rescate de textilería con lana de oveja y artesanas en Chile.
Genera los metadatos en formato JSON.
REGLAS ESTRICTAS:
1. Lenguaje: Español formal, técnico y bibliográfico. CERO INGLÉS.
2. Cero muletillas: No uses "La imagen muestra", "Se observa", "Fotografía de". Inicia directo con la acción o sujeto.
3. Precisión: Describe el proceso productivo (teñido a fuego, hilado, telar, etc.), herramientas y entorno.
4. Cero ambigüedades o especulaciones: No uses palabras de duda o suposición como "posiblemente", "quizás", "probablemente", "al parecer", etc. Escribe afirmaciones objetivas y categóricas sobre lo que es visible.

Debes devolver ÚNICAMENTE un objeto JSON con esta estructura exacta:
{
    "dc.title": "Título descriptivo directo y corto (máx 10 palabras).",
    "dc.title.alternative": "Título alternativo o variante que detalle la acción.",
    "dc.description": "Descripción objetiva y técnica de la escena, herramientas y labor.",
    "dc.description.abstract": "Resumen conciso del valor del proceso o contexto mostrado en la imagen."
}
"""

def procesar_imagen_openai(client, ruta_completa, nota_general):
    if not os.path.exists(ruta_completa):
        print(f"  -> Error: No se encontró {ruta_completa}")
        return None, 0
    
    try:
        imagen_base64 = codificar_imagen(ruta_completa)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": prompt_sistema
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Contexto oficial del proyecto: {nota_general}\n\nAnaliza esta fotografía apoyándote en el contexto entregado y devuelve el JSON correspondiente."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}", "detail": "low"}}
                    ]
                }
            ],
            temperature=0.2
        )
        
        resultado_texto = response.choices[0].message.content
        datos_json = json.loads(resultado_texto)
        tokens_usados = response.usage.total_tokens if response.usage else 0
        return datos_json, tokens_usados
        
    except Exception as e:
        print(f"  -> Error con la IA: {e}")
        return None, 0

def crear_saf():
    print("=========================================================")
    print("      CREADOR Y CATALOGADOR DE PAQUETES SAF PARA DSPACE  ")
    print("=========================================================")
    
    # Cargar variables de entorno
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = None
    if api_key and api_key != "tu_llave_aqui":
        client = OpenAI(api_key=api_key)
    else:
        print("⚠️ Advertencia: No se ha configurado OPENAI_API_KEY en el archivo .env. La catalogación automática no estará disponible.")
        
    CARPETA_RED = input("Pega aquí la ruta de red de la carpeta del proyecto (o presiona Enter para seleccionar uno local):\n> ").strip()
    
    if CARPETA_RED:
        if not os.path.exists(CARPETA_RED):
            print(f"❌ Error: La ruta '{CARPETA_RED}' no existe o está vacía.")
            return
        NOMBRE_PROYECTO = os.path.basename(CARPETA_RED.rstrip('\\/'))
        if not NOMBRE_PROYECTO:
            print("❌ Error: No se pudo deducir el nombre del proyecto desde la ruta.")
            return
            
        PROYECTO_DIR = os.path.join("Proyectos", NOMBRE_PROYECTO)
        
        if not os.path.exists(PROYECTO_DIR):
            print(f"\nCopiando proyecto completo desde la red a '{PROYECTO_DIR}'...")
            try:
                shutil.copytree(CARPETA_RED, PROYECTO_DIR)
                print("¡Copia completada con éxito!\n")
            except Exception as e:
                print(f"❌ Error al copiar la carpeta de red: {e}")
                return
        else:
            print(f"\n✅ La carpeta local '{PROYECTO_DIR}' ya existe. Se usarán los archivos locales.")
    else:
        # Modo seleccion local
        base_proyectos = "Proyectos"
        if not os.path.exists(base_proyectos):
            print(f"❌ No existe la carpeta '{base_proyectos}'. Debes usar una ruta de red primero o crear la carpeta.")
            return
        carpetas = [d for d in os.listdir(base_proyectos) if os.path.isdir(os.path.join(base_proyectos, d))]
        if not carpetas:
            print(f"❌ No hay ningún proyecto en la carpeta '{base_proyectos}'.")
            return
        print("\nSelecciona un proyecto local:")
        for i, d in enumerate(carpetas, 1):
            print(f"[{i}] {d}")
        seleccion = input("\nIngresa el número del proyecto:\n> ").strip()
        try:
            idx = int(seleccion) - 1
            if idx < 0 or idx >= len(carpetas):
                raise ValueError
            NOMBRE_PROYECTO = carpetas[idx]
            PROYECTO_DIR = os.path.join("Proyectos", NOMBRE_PROYECTO)
        except ValueError:
            print("❌ Selección inválida.")
            return

    print(f"\nProyecto seleccionado: {NOMBRE_PROYECTO}\n")
    
    coleccion_handle = input("Introduce el Handle de la colección para DSpace (ej: 123456789/2) [Presiona Enter para omitir]:\n> ").strip()

    # Buscar CSV
    csv_salida = os.path.join(PROYECTO_DIR, "Catalogo_OpenAI_Completo.csv")
    csv_base_files = [f for f in os.listdir(PROYECTO_DIR) if f.lower().endswith('.csv') and not f.startswith('Catalogo_OpenAI')]
    
    if os.path.exists(csv_salida):
        ruta_csv = csv_salida
        print(f"-> Usando CSV catalogado: {ruta_csv}")
    elif csv_base_files:
        ruta_csv = os.path.join(PROYECTO_DIR, csv_base_files[0])
        print(f"-> Usando CSV base: {ruta_csv}")
    else:
        print(f"❌ Error: No se encontró ningún archivo .csv en la carpeta ({PROYECTO_DIR}).")
        return

    CARPETA_FOTOS = os.path.join(PROYECTO_DIR, "Fotos")
    if not os.path.exists(CARPETA_FOTOS):
        CARPETA_FOTOS = PROYECTO_DIR
        
    print(f"-> Carpeta de fotos: {CARPETA_FOTOS}")

    # ==========================================
    # FASE DE CATALOGACION (OPENAI)
    # ==========================================
    if client:
        procesar = input("\n¿Deseas analizar y catalogar imágenes pendientes con OpenAI? (s/n) [s]: ").strip().lower()
        if procesar in ['', 's', 'si', 'y', 'yes']:
            try:
                df = pd.read_csv(ruta_csv, dtype=str)
                columnas_destino = ['dc.title', 'dc.title.alternative', 'dc.description', 'dc.description.abstract', 'dc.format.extent', 'dc.format.medium']
                for col in columnas_destino:
                    if col not in df.columns:
                        df[col] = ''
                    df[col] = df[col].astype('object')
                    
                total = len(df)
                print(f"\nIniciando catalogación. Total: {total} registros.")
                total_tokens_acumulados = 0
                
                for index, row in df.iterrows():
                    nombre_archivo = str(row.get('nombre archivo', '')).strip()
                    if not nombre_archivo:
                        continue
                    ruta_completa = os.path.join(CARPETA_FOTOS, nombre_archivo)
                    
                    if os.path.exists(ruta_completa):
                        try:
                            size_mb = os.path.getsize(ruta_completa) / (1024 * 1024)
                            df.at[index, 'dc.format.medium'] = f"{size_mb:.2f} MB".replace('.', ',')
                            with Image.open(ruta_completa) as img:
                                df.at[index, 'dc.format.extent'] = f"{img.size[0]} x {img.size[1]} píxeles"
                        except Exception as e:
                            print(f"Error leyendo info de {nombre_archivo}: {e}")
                            
                    if 'dc.title' in df.columns and pd.notna(row.get('dc.title')) and str(row.get('dc.title')).strip() != '':
                        print(f"[{index + 1}/{total}] Saltando OpenAI (ya catalogado): {nombre_archivo}")
                        df.to_csv(csv_salida, sep=',', index=False, encoding='utf-8')
                        continue
                        
                    nota_general = str(row.get('fia.notageneral', ''))
                    metadatos, tokens = procesar_imagen_openai(client, ruta_completa, nota_general)
                    total_tokens_acumulados += tokens
                    print(f"[{index + 1}/{total}] Catalogando: {nombre_archivo} | Tokens: {tokens} | Total Acumulado: {total_tokens_acumulados}")
                    
                    if metadatos:
                        df.at[index, 'dc.title'] = metadatos.get('dc.title', '')
                        df.at[index, 'dc.title.alternative'] = metadatos.get('dc.title.alternative', '')
                        df.at[index, 'dc.description'] = metadatos.get('dc.description', '')
                        df.at[index, 'dc.description.abstract'] = metadatos.get('dc.description.abstract', '')
                        df.to_csv(csv_salida, sep=',', index=False, encoding='utf-8')
                
                print(f"\n¡Catalogación terminada! Guardado en {csv_salida}")
                ruta_csv = csv_salida  # Usar el archivo actualizado para el SAF
            except Exception as e:
                print(f"Error durante la catalogación: {e}")

    # ==========================================
    # FASE DE CREACION SAF
    # ==========================================
    saf_dir = os.path.join(PROYECTO_DIR, "SAF")
    if os.path.exists(saf_dir):
        print(f"\n⚠️ La carpeta SAF ya existe en {saf_dir}. Se sobrescribirán los archivos que coincidan.")
    os.makedirs(saf_dir, exist_ok=True)

    print("\n=========================================================")
    print("      GENERANDO ESTRUCTURA SAF                           ")
    print("=========================================================")
    
    try:
        df = pd.read_csv(ruta_csv, dtype=str)
    except Exception as e:
        print(f"❌ Error al leer el CSV: {e}")
        return
        
    df = df.fillna("")
    total = len(df)
    
    for index, row in df.iterrows():
        item_dir = os.path.join(saf_dir, f"item_{index:04d}")
        os.makedirs(item_dir, exist_ok=True)
        
        schemas = {}
        for col in df.columns:
            if '.' in col:
                parts = col.split('.')
                schema = parts[0]
                element = parts[1]
                qualifier = parts[2] if len(parts) > 2 else "none"
                
                value = str(row[col]).strip()
                if not value:
                    continue
                    
                if schema not in schemas:
                    schemas[schema] = []
                    
                values = [v.strip() for v in value.split('||') if v.strip()]
                for v in values:
                    schemas[schema].append({
                        'element': element,
                        'qualifier': qualifier,
                        'value': v
                    })
        
        for schema, tags in schemas.items():
            filename = "dublin_core.xml" if schema == "dc" else f"metadata_{schema}.xml"
            filepath = os.path.join(item_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write('<?xml version="1.0" encoding="utf-8" standalone="no"?>\n')
                f.write(f'<dublin_core schema="{schema}">\n')
                for tag in tags:
                    val = tag['value'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
                    f.write(f'  <dcvalue element="{tag["element"]}" qualifier="{tag["qualifier"]}">{val}</dcvalue>\n')
                f.write('</dublin_core>\n')
                
        nombre_archivo = str(row.get('nombre archivo', '')).strip()
        if nombre_archivo:
            contents_path = os.path.join(item_dir, "contents")
            with open(contents_path, "w", encoding="utf-8") as f:
                f.write(f"{nombre_archivo}\n")
                
            if coleccion_handle:
                collections_path = os.path.join(item_dir, "collections")
                with open(collections_path, "w", encoding="utf-8") as f:
                    f.write(f"{coleccion_handle}\n")
                
            ruta_foto = os.path.join(CARPETA_FOTOS, nombre_archivo)
            if os.path.exists(ruta_foto):
                shutil.copy2(ruta_foto, os.path.join(item_dir, nombre_archivo))
            else:
                print(f"⚠️ Advertencia: No se encontro la imagen '{nombre_archivo}' para el ítem {index:04d}")
                
        print(f"[{index + 1}/{total}] Creado SAF para: {nombre_archivo} -> {item_dir}")
        
    print("\n✅ ¡Proceso de creación SAF terminado exitosamente!")
    print(f"Puedes encontrar los paquetes listos para importar en:\n -> {saf_dir}")

if __name__ == '__main__':
    crear_saf()
