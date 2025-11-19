#!/usr/bin/env python3
"""
Script para actualizar descripciones de nodos Gemini y sessionKey de Postgres

CAMBIOS:
1. Actualizar descripciones de nodos Gemini (video, imagen, documento)
2. Actualizar sessionKey de Postgres de id_session a phone_number

EJECUCIÓN:
python3 update_gemini_and_postgres.py
"""

import json
import sys
from pathlib import Path

# === CONFIGURACIÓN ===
FILE_PATH = Path(__file__).parent / "utq_bot.json"
BACKUP_PATH = Path(__file__).parent / "utq_bot_backup_before_gemini_postgres_update.json"

# === NUEVAS DESCRIPCIONES PARA NODOS GEMINI ===
GEMINI_DESCRIPTIONS = {
    "video": "Analyze the video and extract key actions, text, or objects. Provide a concise summary. The response must be in Spanish and must not exceed 300 characters.",
    "image": "Analyze the image and extract relevant visual details or text. Provide a brief, clear summary. The response must be in Spanish and must not exceed 300 characters.",
    "document": "Read and analyze the document, extracting essential text and key fields. Provide a concise summary. The response must be in Spanish and must not exceed 300 characters."
}

# === NUEVA SESSION KEY PARA POSTGRES ===
NEW_SESSION_KEY = "={{ $('Extraer datos del user').first().json.phone_number }}"
OLD_SESSION_KEY = "={{ $('Extraer datos del user').first().json.id_session }}"

def load_workflow():
    """Cargar el archivo JSON del workflow"""
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {FILE_PATH}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        sys.exit(1)

def save_workflow(workflow):
    """Guardar el workflow modificado"""
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

def backup_workflow(workflow):
    """Crear backup del workflow original"""
    with open(BACKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)
    print(f"✅ Backup creado en: {BACKUP_PATH}")

def update_gemini_nodes(workflow):
    """Actualizar descripciones de nodos Gemini"""
    changes_made = []

    for node in workflow['nodes']:
        if node.get('type') == '@n8n/n8n-nodes-langchain.googleGemini':
            resource = node['parameters'].get('resource')
            node_name = node.get('name', 'Unknown')

            if resource in GEMINI_DESCRIPTIONS:
                old_text = node['parameters'].get('text', '')
                new_text = GEMINI_DESCRIPTIONS[resource]

                if old_text != new_text:
                    node['parameters']['text'] = new_text
                    changes_made.append({
                        'node': node_name,
                        'resource': resource,
                        'old': old_text[:50] + '...' if len(old_text) > 50 else old_text,
                        'new': new_text[:50] + '...' if len(new_text) > 50 else new_text
                    })

    return changes_made

def update_postgres_session_key(workflow):
    """Actualizar sessionKey del nodo Postgres"""
    changes_made = []

    for node in workflow['nodes']:
        if node.get('type') == '@n8n/n8n-nodes-langchain.memoryPostgresChat':
            node_name = node.get('name', 'Unknown')
            old_key = node['parameters'].get('sessionKey', '')

            if old_key == OLD_SESSION_KEY:
                node['parameters']['sessionKey'] = NEW_SESSION_KEY
                changes_made.append({
                    'node': node_name,
                    'old': old_key,
                    'new': NEW_SESSION_KEY
                })
            elif old_key != NEW_SESSION_KEY:
                print(f"⚠️  Advertencia: sessionKey diferente al esperado en {node_name}")
                print(f"   Esperado: {OLD_SESSION_KEY}")
                print(f"   Encontrado: {old_key}")

                # Preguntar si actualizar de todas formas
                response = input(f"   ¿Actualizar a phone_number? (s/n): ")
                if response.lower() == 's':
                    node['parameters']['sessionKey'] = NEW_SESSION_KEY
                    changes_made.append({
                        'node': node_name,
                        'old': old_key,
                        'new': NEW_SESSION_KEY
                    })

    return changes_made

def main():
    """Función principal"""
    print("\n" + "="*70)
    print("🔧 Actualizando Nodos Gemini y Postgres")
    print("="*70 + "\n")

    # Cargar workflow
    print("📖 Cargando workflow...")
    workflow = load_workflow()
    print(f"✅ Workflow cargado: {len(workflow['nodes'])} nodos\n")

    # Crear backup
    print("💾 Creando backup...")
    backup_workflow(workflow)
    print()

    # Actualizar nodos Gemini
    print("🎨 Actualizando descripciones de nodos Gemini...")
    gemini_changes = update_gemini_nodes(workflow)

    if gemini_changes:
        print(f"✅ {len(gemini_changes)} nodos Gemini actualizados:")
        for change in gemini_changes:
            print(f"   • {change['node']} ({change['resource']})")
            print(f"     Antes: {change['old']}")
            print(f"     Ahora: {change['new']}")
    else:
        print("ℹ️  No se encontraron cambios necesarios en nodos Gemini")
    print()

    # Actualizar Postgres
    print("🗄️  Actualizando sessionKey de Postgres...")
    postgres_changes = update_postgres_session_key(workflow)

    if postgres_changes:
        print(f"✅ {len(postgres_changes)} nodo(s) Postgres actualizado(s):")
        for change in postgres_changes:
            print(f"   • {change['node']}")
            print(f"     Antes: {change['old']}")
            print(f"     Ahora: {change['new']}")
    else:
        print("ℹ️  No se encontraron cambios necesarios en Postgres")
    print()

    # Guardar workflow modificado
    if gemini_changes or postgres_changes:
        print("💾 Guardando workflow modificado...")
        save_workflow(workflow)
        print(f"✅ Workflow guardado correctamente")
        print()

        # Resumen
        print("="*70)
        print("✅ ACTUALIZACIÓN COMPLETADA")
        print("="*70)
        print("\n📊 Resumen de cambios:")
        print(f"   ✅ Nodos Gemini actualizados: {len(gemini_changes)}")
        print(f"   ✅ Nodos Postgres actualizados: {len(postgres_changes)}")
        print(f"   ✅ Backup guardado en: {BACKUP_PATH}")
        print(f"\n📁 Archivo modificado: {FILE_PATH}")

        print("\n🎯 Cambios realizados:")
        print("\n1. NODOS GEMINI (Descripciones más específicas):")
        print("   - Video: Analiza video, extrae acciones/texto/objetos (máx 300 chars)")
        print("   - Imagen: Analiza imagen, extrae detalles visuales/texto (máx 300 chars)")
        print("   - Documento: Lee y analiza documento, extrae texto/campos clave (máx 300 chars)")

        print("\n2. NODO POSTGRES (SessionKey actualizado):")
        print("   - Antes: id_session (ID del mensaje)")
        print("   - Ahora: phone_number (número de teléfono del usuario)")
        print("   - Beneficio: Mantiene historial por usuario, no por mensaje")
        print()
    else:
        print("ℹ️  No se realizaron cambios (todo estaba actualizado)")
        print()

if __name__ == "__main__":
    main()
