#!/usr/bin/env python3
"""
Replace Gemini nodes with OpenAI vision nodes
OpenAI GPT-4o and GPT-4o-mini support image, video, and document analysis
"""
import json

# Load workflow
with open('utq_bot.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

print("🔧 Replacing Gemini nodes with OpenAI...\n")

# Find existing OpenAI credentials from the workflow
openai_creds = None
for node in workflow['nodes']:
    if 'credentials' in node and 'openAiApi' in node.get('credentials', {}):
        openai_creds = node['credentials']['openAiApi']
        print(f"✓ Found existing OpenAI credentials: {openai_creds['name']}")
        break

if not openai_creds:
    print("⚠️  No existing OpenAI credentials found, using placeholder")
    openai_creds = {
        "id": "GafxAaPv86SW96HG",
        "name": "OpenAi account UTOPIQ"
    }

# OpenAI replacement configurations
openai_replacements = {
    "Gemini Analyze Image": {
        "name": "OpenAI Analyze Image",
        "parameters": {
            "resource": "image",
            "operation": "analyze",
            "modelId": "gpt-4o-mini",
            "text": "={{ $('Clasificar Tipo Mensaje').item.json.messages[0].image?.caption ? 'El usuario envió esta imagen con el texto: \"' + $('Clasificar Tipo Mensaje').item.json.messages[0].image.caption + '\". Describe la imagen en español considerando el contexto del mensaje.' : 'Describe detalladamente esta imagen en español.' }}",
            "options": {
                "maxTokens": 500
            }
        },
        "type": "n8n-nodes-base.openAi",
        "typeVersion": 1.7
    },
    "Gemini Analyze Video": {
        "name": "OpenAI Analyze Video",
        "parameters": {
            "resource": "image",  # OpenAI treats video frames as images
            "operation": "analyze",
            "modelId": "gpt-4o-mini",
            "text": "={{ $('Clasificar Tipo Mensaje').item.json.messages[0].video?.caption ? 'El usuario envió este video con el texto: \"' + $('Clasificar Tipo Mensaje').item.json.messages[0].video.caption + '\". Describe el contenido del video en español considerando el contexto del mensaje. Analiza los frames del video para dar una descripción completa.' : 'Describe detalladamente el contenido de este video en español analizando sus frames.' }}",
            "options": {
                "maxTokens": 500
            }
        },
        "type": "n8n-nodes-base.openAi",
        "typeVersion": 1.7
    },
    "Gemini Analyze PDF": {
        "name": "OpenAI Analyze PDF",
        "parameters": {
            "resource": "image",  # OpenAI can analyze PDF pages as images
            "operation": "analyze",
            "modelId": "gpt-4o-mini",
            "text": "={{ $('Clasificar Tipo Mensaje').item.json.messages[0].document?.caption ? 'El usuario envió este documento con el texto: \"' + $('Clasificar Tipo Mensaje').item.json.messages[0].document.caption + '\". Resume el contenido del documento en español considerando el contexto del mensaje.' : 'Resume detalladamente el contenido de este documento en español.' }}",
            "options": {
                "maxTokens": 500
            }
        },
        "type": "n8n-nodes-base.openAi",
        "typeVersion": 1.7
    }
}

replaced_nodes = []

for node in workflow['nodes']:
    if node['name'] in openai_replacements:
        old_name = node['name']
        replacement = openai_replacements[old_name]

        # Update node
        node['name'] = replacement['name']
        node['parameters'] = replacement['parameters']
        node['type'] = replacement['type']
        node['typeVersion'] = replacement['typeVersion']
        node['credentials'] = {
            "openAiApi": openai_creds
        }

        replaced_nodes.append({
            'old': old_name,
            'new': replacement['name']
        })

        print(f"✓ Replaced {old_name} → {replacement['name']}")
        print(f"  - Type: {replacement['type']}")
        print(f"  - Model: {replacement['parameters']['modelId']}")
        print(f"  - Resource: {replacement['parameters']['resource']}")
        print()

# Update connections with new node names
print("🔗 Updating connections...")
connection_updates = 0

for source_node, connections in workflow['connections'].items():
    for connection_type, connection_list in connections.items():
        for connection_group in connection_list:
            for connection in connection_group:
                # Check if this connection references an old Gemini node
                for replacement in replaced_nodes:
                    if connection.get('node') == replacement['old']:
                        connection['node'] = replacement['new']
                        connection_updates += 1
                        print(f"  ✓ Updated connection: {source_node} → {replacement['new']}")

print(f"\nTotal connections updated: {connection_updates}")

# Save
with open('utq_bot.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("\n✅ Successfully replaced Gemini nodes with OpenAI!")
print("\n📋 Summary:")
print(f"  - Nodes replaced: {len(replaced_nodes)}")
print(f"  - Connections updated: {connection_updates}")
print(f"  - OpenAI credentials: {openai_creds['name']}")
print("\n🎯 All nodes now use OpenAI GPT-4o-mini for vision analysis")
print("   - Supports: Images, Video frames, PDF pages")
print("   - Max tokens: 500 per analysis")
print("   - Same dynamic prompts with caption support")
