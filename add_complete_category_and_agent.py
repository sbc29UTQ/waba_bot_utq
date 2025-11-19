#!/usr/bin/env python3
"""
Script para agregar la categoría COMPLETE y el agente Complete al workflow utq_bot.json

PROPÓSITO:
- Manejar cuando el usuario termina un flujo completo
- Ofrecer cierre adecuado y opciones para continuar
- Detectar palabras de despedida, agradecimiento o finalización

EJECUCIÓN:
python3 add_complete_category_and_agent.py
"""

import json
import sys
from pathlib import Path

# === CONFIGURACIÓN ===
FILE_PATH = Path(__file__).parent / "utq_bot.json"
BACKUP_PATH = Path(__file__).parent / "utq_bot_backup_before_complete.json"

# === NUEVA CATEGORÍA PARA TEXTCLASSIFIER ===
NEW_CATEGORY_COMPLETE = {
    "category": "COMPLETE",
    "description": """=**Trigger Conditions**

Route to COMPLETE when the user:

- Expresses EXPLICIT completion and farewell ("Ya terminé todo, gracias, adiós")
- Wants to close the current workflow entirely and start completely fresh
- Says goodbye with clear finality ("Hasta luego", "Nos vemos", "Goodbye")
- Explicitly states they want to end the session ("Es todo por hoy", "Ya no necesito más")
- Wants to reset and start a completely different project (not related to current work)

**IMPORTANT - CONTINUITY FIRST:**

❌ **DO NOT route to COMPLETE if:**
- User is answering agent's questions (CONTINUITY RULE 1 applies - maintain agent)
- User is in middle of framework execution (maintain current agent)
- User just says "gracias" or "ok" but continues conversation (maintain agent)
- User asks follow-up questions after thanking (maintain agent)
- User shows interest in continuing or refining (maintain agent)

✅ **ONLY route to COMPLETE if:**
- User explicitly closes conversation: "Ya terminé, gracias, hasta luego"
- User wants completely new unrelated project: "Quiero trabajar en algo totalmente diferente"
- User signals clear end: "Eso es todo, nos vemos"
- No active conversation thread (user initiating closure)

**Route to COMPLETE EVEN IF:**

✔ The framework is incomplete but user explicitly wants to stop and end
✔ Context shows completed OPTIMIZE phase and user says final goodbye
✔ User explicitly requests to "empezar de cero" or "reset everything"

**NOT Included:**

❌ Simple thanks mid-conversation → maintain current agent (CONTINUITY)
❌ Asks for next steps → OPTIMIZE (not closure)
❌ Sends work for final review → REVIEW
❌ Wants to refine current work → maintain current agent
❌ Asks questions after thanking → maintain current agent
❌ "Gracias" + continues conversation → NOT closure, maintain agent

**Purpose:**

Provide closure, celebrate achievements, and offer options:
- End session with summary of accomplishments
- Start a completely new framework from scratch (reset context)
- Return to explore a different unrelated business area

**Examples:**

✅ **Route to COMPLETE:**
- "Ya terminé todo, muchas gracias, hasta luego"
- "Perfecto, eso es todo lo que necesitaba. Nos vemos"
- "Gracias por todo, adiós"
- "Quiero cerrar esto y empezar un proyecto completamente nuevo"
- "I'm done for today, thank you and goodbye"
- "That's all I needed, thanks and see you later"

❌ **DO NOT route to COMPLETE (maintain agent):**
- "Gracias" + [continues asking questions] → maintain agent
- "Ok, gracias. ¿Y qué pongo aquí?" → APPLY (continuity)
- "Gracias, ¿qué sigue?" → OPTIMIZE (not closure)
- "Gracias. Revisa esto por favor" → REVIEW (not closure)
"""
}

# === NUEVO AGENTE COMPLETE ===
NEW_AGENT_COMPLETE = {
    "parameters": {
        "promptType": "define",
        "text": "={{ $('Extraer datos del user').first().json.message }}",
        "options": {
            "systemMessage": """=# Rol
You are a completion and transition agent and your mission is to provide closure, celebrate user's achievements, and offer pathways to either start fresh or end the session gracefully.

You are a business success coach working for the company "UTOPIQ" which specializes in business strategy, process optimization, and innovation.
You have been working for the company for the last 5 years helping entrepreneurs celebrate milestones and plan new beginnings.

## Personality

- You're warm and celebratory about user accomplishments
- You provide meaningful closure and acknowledge progress
- You communicate like a supportive mentor at the end of a session
- You're clear about next options without being pushy
- You balance celebration with forward momentum

# User Background

Here's what you know about the user from your long term memory (this could be from a conversation from today or 6 months ago, have that in mind).

<memory>{{ $('code2').first().json.facts_text }}</memory>

You also have a short term memory of the last 5 messages.

<short_memory>{{ $('code3').item.json.formatted_memories }}</short_memory>

# 📸 Media Type Context

**IMPORTANT**: The user's message may come from different media sources.

Check the media type: $('Extraer datos del user').first().json.type_message

Media types:
- **text**: User typed this message directly (normal text conversation)
- **image**: User sent an image. The message is an AI-generated description of that image
- **video**: User sent a video. The message is an AI-generated description of the video
- **document**: User sent a PDF/document. The message is an AI-generated summary

## How to respond based on media type:

### If type_message is 'image':
- Acknowledge: "I can see from the image you sent that..."
- Be specific: "Looking at the final version in your image..."
- Celebrate visual completion: "Your completed framework looks solid!"

### If type_message is 'video':
- Acknowledge: "From the video you shared, I can see..."
- Celebrate documented work: "Great to see your process documented in video!"

### If type_message is 'document':
- Acknowledge: "Based on the document you sent..."
- Celebrate documentation: "Excellent work documenting everything in the PDF!"

### If type_message is 'text' or undefined:
- Normal text conversation
- Respond naturally without media acknowledgment

## Agent-specific media handling:

**COMPLETE agent**:
- Any media sent → treat as final artifact to celebrate
- Example: "I can see your final work in the image you shared - excellent progress!"
- Acknowledge completion and offer closure

# Your Mission

Your goal is to:
1. **Acknowledge** what they've accomplished in the conversation
2. **Celebrate** specific milestones or frameworks completed
3. **Summarize** key takeaways (2-3 bullet points)
4. **Offer options** for what's next:
   - 🆕 Start a new framework or project
   - 🎯 Explore a different business area
   - 📋 Get a summary of work completed
   - 👋 End session with encouragement
5. **Leave the door open** for return

# Detection Scenarios

## Scenario 1: User completed full workflow
**User message:** "Ya terminé todo, gracias"
**Your response:** Celebrate complete journey → Summarize accomplishments → Offer new start

## Scenario 2: User wants to stop mid-work
**User message:** "Es suficiente por hoy"
**Your response:** Validate progress → Note where they stopped → Offer to continue later or start new

## Scenario 3: User wants to switch topics completely
**User message:** "Quiero trabajar en algo diferente ahora"
**Your response:** Acknowledge current work → Offer clean slate with EXPLORE → Reset context

## Scenario 4: User just saying thanks
**User message:** "Gracias por la ayuda"
**Your response:** Acknowledge gratitude → Ask if they're done or want to continue → Offer options

# Rules

You have to follow, ALWAYS, the following rules:

- You will never mention that you are an AI or a virtual assistant
- ALWAYS acknowledge specific work done (check short_memory for context)
- Celebrate at least 1-2 concrete accomplishments
- Keep summary brief (2-3 key takeaways max)
- Offer clear next options using emojis (🆕🎯📋👋)
- Don't call framework_use tool (this is closure, not new work)
- If user wants to start fresh → guide them: "Great! Tell me what business challenge you want to tackle"
- If user wants to end → provide warm closure
- Reference specific frameworks they worked on from short_memory
- Keep it personal and specific, not generic

# Output Format

**If user is ending session:**
1. Warm acknowledgment
2. Summary of accomplishments (2-3 bullets)
3. Encouragement
4. Invitation to return anytime

**If user wants to start fresh:**
1. Celebrate current work completion
2. Reset mindset: "Let's start with a clean slate"
3. Open question: "What's the new challenge or project you want to work on?"
4. (This will route them back to EXPLORE)

**If user is uncertain:**
1. Acknowledge their gratitude
2. Validate progress made
3. Offer clear options:
   - 🆕 "Start a new framework or project"
   - 🎯 "Explore a different business area"
   - 👋 "End for today and return later"

Write warmly and personally (150-200 words).
Use the user's actual accomplishments from short_memory.
End with clear call-to-action or warm goodbye.
""",
            "returnIntermediateSteps": True
        }
    },
    "type": "@n8n/n8n-nodes-langchain.agent",
    "typeVersion": 1.9,
    "position": [
        -3696,
        1632
    ],
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",  # ID único temporal
    "name": "Complete",
    "alwaysOutputData": False,
    "onError": "continueErrorOutput"
}

# === NODO PARA SEPARAR MENSAJES (Complete) ===
NEW_CODE_NODE_SEPARATE_COMPLETE = {
    "parameters": {
        "jsCode": """// 1. Obtener mensaje del usuario
const humanMessage = $('Extraer datos del user').first().json.message || "";

// 2. Obtener mensaje generado por la IA desde el nodo "Complete"
const agentNode = $('Complete').item.json || {};
const aiMessage = agentNode.output || "";

// 3. Devolver solo los dos items pedidos
return [{
  json: {
    humanMessage,
    aiMessage
  }
}];
"""
    },
    "type": "n8n-nodes-base.code",
    "typeVersion": 2,
    "position": [
        -2928,
        1632
    ],
    "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",  # ID único temporal
    "name": "separar mensajes5"
}

# === NODO PARA CREAR ROW EN SUPABASE (Complete) ===
NEW_SUPABASE_NODE_COMPLETE = {
    "parameters": {
        "tableId": "conversations_utq_bot",
        "fieldsUi": {
            "fieldValues": [
                {
                    "fieldId": "conversation_id",
                    "fieldValue": "={{ $('Extraer datos del user').first().json.phone_number }}"
                },
                {
                    "fieldId": "phone_number",
                    "fieldValue": "={{ $('Extraer datos del user').first().json.phone_number }}"
                },
                {
                    "fieldId": "message_ai",
                    "fieldValue": "={{ $('separar mensajes5').item.json.aiMessage }}"
                },
                {
                    "fieldId": "message_user",
                    "fieldValue": "={{ $('separar mensajes5').item.json.humanMessage }}"
                },
                {
                    "fieldId": "agent_name",
                    "fieldValue": "Complete"
                },
                {
                    "fieldId": "classification",
                    "fieldValue": "COMPLETE"
                }
            ]
        }
    },
    "type": "n8n-nodes-base.supabase",
    "typeVersion": 1,
    "position": [
        -2704,
        1632
    ],
    "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",  # ID único temporal
    "name": "Create a row5",
    "credentials": {
        "supabaseApi": {
            "id": "dwjOm2bQbMgkmttQ",
            "name": "UTOPIQ_BBDD"
        }
    }
}

# === NODO PARA ENVIAR MENSAJE (Complete) ===
NEW_SEND_MESSAGE_NODE_COMPLETE = {
    "parameters": {
        "operation": "send",
        "phoneNumberId": "730111076863264",
        "recipientPhoneNumber": "={{ $('Extraer datos del user').first().json.phone_number }}",
        "textBody": "={{ $('Complete').item.json.output }}",
        "additionalFields": {}
    },
    "type": "n8n-nodes-base.whatsApp",
    "typeVersion": 1.1,
    "position": [
        -3152,
        1632
    ],
    "id": "d4e5f6a7-b8c9-0123-def0-1234567890ab",  # ID único temporal
    "name": "Send message5",
    "webhookId": "75735ec1-9780-4082-8147-f641a0aa829e",
    "alwaysOutputData": False,
    "credentials": {
        "whatsAppApi": {
            "id": "0duhem9Atjb1fCMb",
            "name": "WhatsApp send UTQ-BOT-V1"
        }
    }
}

# === NODO PARA LLAMAR WORKFLOW DE ACTUALIZACIÓN (Complete) ===
NEW_CALL_UPDATE_MEMORY_COMPLETE = {
    "parameters": {
        "workflowId": {
            "__rl": True,
            "mode": "list",
            "value": "",
            "cachedResultName": "Actualizar_memoria_utq_bot"
        },
        "fields": {
            "values": [
                {
                    "name": "phone_number",
                    "value": "={{ $('Extraer datos del user').first().json.phone_number }}"
                },
                {
                    "name": "user_message",
                    "value": "={{ $('separar mensajes5').item.json.humanMessage }}"
                },
                {
                    "name": "ai_message",
                    "value": "={{ $('separar mensajes5').item.json.aiMessage }}"
                }
            ]
        }
    },
    "type": "n8n-nodes-base.executeWorkflow",
    "typeVersion": 1.3,
    "position": [
        -3152,
        1808
    ],
    "id": "e5f6a7b8-c9d0-1234-ef01-234567890abc",  # ID único temporal
    "name": "Call 'Actualizar_memoria_utq_bot'5"
}

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

def find_text_classifier_node(workflow):
    """Encontrar el nodo TextClassifier"""
    for node in workflow['nodes']:
        if node.get('name') == 'Clasificacion de intencion':
            return node
    return None

def add_complete_category(workflow):
    """Agregar la categoría COMPLETE al TextClassifier"""
    classifier_node = find_text_classifier_node(workflow)

    if not classifier_node:
        print("❌ No se encontró el nodo TextClassifier")
        return False

    # Verificar si ya existe
    categories = classifier_node['parameters']['categories']['categories']
    if any(cat['category'] == 'COMPLETE' for cat in categories):
        print("⚠️  La categoría COMPLETE ya existe")
        return False

    # Agregar nueva categoría
    categories.append(NEW_CATEGORY_COMPLETE)
    print(f"✅ Categoría COMPLETE agregada al TextClassifier")
    print(f"   Total de categorías ahora: {len(categories)}")

    # Actualizar el systemPromptTemplate para incluir COMPLETE
    system_prompt = classifier_node['parameters']['options']['systemPromptTemplate']

    # Agregar COMPLETE a la lista de outputs
    if "OPTIMIZE" in system_prompt and "COMPLETE" not in system_prompt:
        system_prompt = system_prompt.replace(
            "EXPLORE\nLEARN\nAPPLY\nREVIEW\nOPTIMIZE",
            "EXPLORE\nLEARN\nAPPLY\nREVIEW\nOPTIMIZE\nCOMPLETE"
        )

        # Agregar regla especial de COMPLETE después de las reglas de continuidad
        complete_rule = """

## 🏁 COMPLETE CATEGORY RULE (AFTER CONTINUITY RULES)

**This rule applies AFTER continuity rules have been checked.**

### RULE: Only COMPLETE when explicit session closure

**IF** user message signals EXPLICIT and CLEAR session closure:
→ **ROUTE TO COMPLETE** (session ending)

**Closure signals (Spanish):**
- "Ya terminé todo, gracias, hasta luego"
- "Perfecto, eso es todo. Nos vemos"
- "Gracias por todo, adiós"
- "Quiero cerrar esto y empezar algo totalmente nuevo"
- "Es todo por hoy, nos vemos"

**Closure signals (English):**
- "I'm done for today, thank you and goodbye"
- "That's all I needed, thanks and see you"
- "Thank you for everything, goodbye"
- "I want to close this and start something completely new"

**CRITICAL - DO NOT route to COMPLETE if:**
- ❌ User is answering agent's questions (CONTINUITY applies)
- ❌ Simple "gracias" or "ok" mid-conversation (CONTINUITY applies)
- ❌ User asks follow-up after thanking (CONTINUITY applies)
- ❌ User asks "¿qué sigue?" (→ OPTIMIZE, not COMPLETE)
- ❌ User says "gracias" but continues conversation (CONTINUITY applies)

**Priority hierarchy for closure detection:**
1. ⚠️ CONTINUITY RULES (highest) - if user answering questions, maintain agent
2. 🎯 NEXT STEPS DETECTION - if "qué sigue", route to OPTIMIZE
3. 🏁 COMPLETE - only if explicit goodbye/closure with no continuation

**Rationale:**
- COMPLETE is for session endings and major resets
- Simple gratitude or acknowledgment ≠ session closure
- Continuity rules prevent false positives
- User must explicitly signal they want to end or restart completely

**Examples:**

✅ **ROUTE TO COMPLETE:**
```
Last agent: Optimize
User: "Perfecto, muchas gracias por todo. Hasta luego"
→ **COMPLETE** (explicit closure)
```

```
User (new conversation): "Quiero empezar de cero con un proyecto nuevo"
→ **COMPLETE** (explicit reset request)
```

❌ **DO NOT ROUTE TO COMPLETE:**
```
Last agent: Apply
Apply: "¿Qué customer segments tienes?"
User: "Gracias por preguntar. Tengo SMEs y startups"
→ **APPLY** (answering question - continuity)
```

```
Last agent: Review
User: "Gracias por el feedback. ¿Qué sigue ahora?"
→ **OPTIMIZE** (next steps request, not closure)
```

```
Last agent: Learn
User: "Ok gracias, ¿y cómo lo aplico?"
→ **APPLY** (wants to apply - phase change, not closure)
```

---
"""

        # Insertar COMPLETE rule antes de "## CLASSIFICATION CATEGORIES"
        if "## CLASSIFICATION CATEGORIES" in system_prompt:
            system_prompt = system_prompt.replace(
                "## CLASSIFICATION CATEGORIES",
                complete_rule + "\n## CLASSIFICATION CATEGORIES"
            )

        classifier_node['parameters']['options']['systemPromptTemplate'] = system_prompt
        print("✅ SystemPromptTemplate actualizado con COMPLETE y reglas de prioridad")

    return True

def add_complete_agent_nodes(workflow):
    """Agregar todos los nodos necesarios para el agente Complete"""
    nodes = workflow['nodes']

    # Agregar nodos
    nodes.append(NEW_AGENT_COMPLETE)
    nodes.append(NEW_CODE_NODE_SEPARATE_COMPLETE)
    nodes.append(NEW_SUPABASE_NODE_COMPLETE)
    nodes.append(NEW_SEND_MESSAGE_NODE_COMPLETE)
    nodes.append(NEW_CALL_UPDATE_MEMORY_COMPLETE)

    print(f"✅ Agregados 5 nodos para el agente Complete:")
    print(f"   - Complete (agent)")
    print(f"   - separar mensajes5 (code)")
    print(f"   - Create a row5 (supabase)")
    print(f"   - Send message5 (whatsapp)")
    print(f"   - Call 'Actualizar_memoria_utq_bot'5 (executeWorkflow)")

    return True

def add_connections(workflow):
    """Agregar conexiones necesarias en el workflow"""
    connections = workflow.get('connections', {})

    # Conexión desde TextClassifier a Complete
    if 'Clasificacion de intencion' not in connections:
        connections['Clasificacion de intencion'] = {}

    if 'main' not in connections['Clasificacion de intencion']:
        connections['Clasificacion de intencion']['main'] = []

    # Agregar conexión COMPLETE (índice 5)
    connections['Clasificacion de intencion']['main'].append([
        {
            "node": "Complete",
            "type": "main",
            "index": 0
        }
    ])

    # Conexiones del agente Complete
    connections['Complete'] = {
        "main": [
            [
                {
                    "node": "separar mensajes5",
                    "type": "main",
                    "index": 0
                },
                {
                    "node": "Send message5",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

    connections['separar mensajes5'] = {
        "main": [
            [
                {
                    "node": "Create a row5",
                    "type": "main",
                    "index": 0
                },
                {
                    "node": "Call 'Actualizar_memoria_utq_bot'5",
                    "type": "main",
                    "index": 0
                }
            ]
        ]
    }

    workflow['connections'] = connections
    print("✅ Conexiones agregadas para el flujo Complete")

    return True

def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🚀 Agregando categoría COMPLETE y agente Complete")
    print("="*60 + "\n")

    # Cargar workflow
    print("📖 Cargando workflow...")
    workflow = load_workflow()
    print(f"✅ Workflow cargado: {len(workflow['nodes'])} nodos existentes\n")

    # Crear backup
    print("💾 Creando backup...")
    backup_workflow(workflow)
    print()

    # Agregar categoría COMPLETE
    print("📝 Agregando categoría COMPLETE al TextClassifier...")
    if not add_complete_category(workflow):
        print("⚠️  Continuando de todas formas...\n")
    else:
        print()

    # Agregar nodos del agente
    print("🔧 Agregando nodos del agente Complete...")
    add_complete_agent_nodes(workflow)
    print()

    # Agregar conexiones
    print("🔗 Agregando conexiones...")
    add_connections(workflow)
    print()

    # Guardar workflow modificado
    print("💾 Guardando workflow modificado...")
    save_workflow(workflow)
    print(f"✅ Workflow guardado: {len(workflow['nodes'])} nodos totales")
    print()

    # Resumen
    print("="*60)
    print("✅ IMPLEMENTACIÓN COMPLETADA")
    print("="*60)
    print("\n📊 Resumen de cambios:")
    print("   ✅ Nueva categoría COMPLETE en TextClassifier")
    print("   ✅ 5 nodos nuevos agregados para agente Complete")
    print("   ✅ Conexiones configuradas")
    print(f"   ✅ Backup guardado en: {BACKUP_PATH}")
    print(f"\n📁 Archivo modificado: {FILE_PATH}")
    print("\n🎯 Casos de uso para COMPLETE:")
    print("   - Usuario termina su trabajo: 'Ya terminé todo, gracias'")
    print("   - Usuario quiere parar: 'Es suficiente por hoy'")
    print("   - Usuario quiere empezar nuevo: 'Quiero algo completamente diferente'")
    print("   - Usuario se despide: 'Gracias por la ayuda, hasta luego'")
    print("\n🚀 Flujo completo ahora:")
    print("   EXPLORE → LEARN → APPLY ⟷ REVIEW → OPTIMIZE → COMPLETE")
    print("                                ↑                      ↓")
    print("                                └──────────────────────┘")
    print("                                (reinicio de ciclo)")
    print()

if __name__ == "__main__":
    main()
