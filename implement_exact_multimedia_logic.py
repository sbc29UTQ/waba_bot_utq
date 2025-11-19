#!/usr/bin/env python3
"""
Implement EXACT multimedia logic from user's working structure.
This replaces the previous multimedia implementation with the exact structure that works.
"""

import json

def implement_exact_multimedia_logic():
    # Load current workflow
    with open('utq_bot.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    # Find the WhatsApp Trigger node
    whatsapp_trigger = None
    extraer_datos_node = None

    for node in workflow['nodes']:
        if node.get('type') == 'n8n-nodes-base.whatsAppTrigger':
            whatsapp_trigger = node
        if node.get('name') == 'Extraer datos del user':
            extraer_datos_node = node

    if not whatsapp_trigger:
        print("❌ WhatsApp Trigger not found!")
        return

    if not extraer_datos_node:
        print("❌ Extraer datos del user node not found!")
        return

    print(f"✓ Found WhatsApp Trigger: {whatsapp_trigger['name']}")
    print(f"✓ Found Extraer datos del user at position: {extraer_datos_node['position']}")

    # Remove old multimedia nodes (OpenAI, old Switch, old Gemini, etc.)
    old_multimedia_node_names = [
        "Clasificar Tipo Mensaje",
        "WA Get Image URL",
        "WA Get Video URL",
        "WA Get PDF URL",
        "Download Image",
        "Download Video",
        "Download PDF",
        "OpenAI Analyze Image",
        "OpenAI Analyze Video",
        "OpenAI Analyze PDF",
        "Gemini Analyze Image",
        "Gemini Analyze Video",
        "Gemini Analyze PDF",
        "Preparar Texto",
        "Preparar Imagen",
        "Preparar Video",
        "Preparar PDF",
        "Merge Media Types",
        "Switch",
        "WhatsApp Business Cloud",
        "WhatsApp Business Cloud1",
        "WhatsApp Business Cloud2",
        "HTTP Request",
        "HTTP Request1",
        "HTTP Request2",
        "Analyze video",
        "Analyze an image",
        "Analyze document",
        "Edit Fields1"
    ]

    # Keep track of nodes to remove
    nodes_to_remove = []
    for node in workflow['nodes']:
        if node['name'] in old_multimedia_node_names:
            nodes_to_remove.append(node)

    # Remove old nodes
    for node in nodes_to_remove:
        workflow['nodes'].remove(node)
        print(f"  - Removed old node: {node['name']}")

    # Get WhatsApp trigger position to place new nodes relative to it
    trigger_x, trigger_y = whatsapp_trigger['position']

    # Create new nodes with EXACT structure from user

    # 1. Switch node
    switch_node = {
        "parameters": {
            "rules": {
                "values": [
                    {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict",
                                "version": 2
                            },
                            "conditions": [
                                {
                                    "leftValue": "={{ $json.messages[0].type }}",
                                    "rightValue": "video",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals"
                                    },
                                    "id": "c17f62d7-353c-4fec-b4ea-2835d97dbd38"
                                }
                            ],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "video"
                    },
                    {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict",
                                "version": 2
                            },
                            "conditions": [
                                {
                                    "id": "61f1ba91-2b09-4922-a92b-84d9615b5c9f",
                                    "leftValue": "={{ $json.messages[0].type }}",
                                    "rightValue": "image",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals",
                                        "name": "filter.operator.equals"
                                    }
                                }
                            ],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "imagen"
                    },
                    {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict",
                                "version": 2
                            },
                            "conditions": [
                                {
                                    "id": "61145ec7-2b0a-48ab-ac54-ea4caff7268c",
                                    "leftValue": "={{ $json.messages[0].document.mime_type }}",
                                    "rightValue": "application/pdf",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals",
                                        "name": "filter.operator.equals"
                                    }
                                }
                            ],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "pdf"
                    },
                    {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict",
                                "version": 2
                            },
                            "conditions": [
                                {
                                    "id": "a3ef6e91-4e23-4459-b791-72a434b1beff",
                                    "leftValue": "={{ $json.messages[0].type }}",
                                    "rightValue": "text",
                                    "operator": {
                                        "type": "string",
                                        "operation": "equals",
                                        "name": "filter.operator.equals"
                                    }
                                }
                            ],
                            "combinator": "and"
                        },
                        "renameOutput": True,
                        "outputKey": "texto"
                    }
                ]
            },
            "options": {
                "allMatchingOutputs": True
            }
        },
        "type": "n8n-nodes-base.switch",
        "typeVersion": 3.3,
        "position": [trigger_x + 320, trigger_y - 32],
        "id": "00e86c15-6e9d-4798-834e-e86e8d7bbed6",
        "name": "Switch"
    }

    # 2. WhatsApp Business Cloud nodes (get media URL)
    wa_video_node = {
        "parameters": {
            "resource": "media",
            "operation": "mediaUrlGet",
            "mediaGetId": "={{ $('WhatsApp Trigger1').item.json.messages[0].video.id }}"
        },
        "type": "n8n-nodes-base.whatsApp",
        "typeVersion": 1,
        "position": [trigger_x + 640, trigger_y - 192],
        "id": "2015d9ec-1d31-4a6b-8da0-e96df8f6e032",
        "name": "WhatsApp Business Cloud",
        "webhookId": "01a564ba-00b1-407c-9b0b-cd143851bd39",
        "credentials": {
            "whatsAppApi": {
                "id": "0duhem9Atjb1fCMb",
                "name": "WhatsApp send UTQ-BOT-V1"
            }
        }
    }

    wa_image_node = {
        "parameters": {
            "resource": "media",
            "operation": "mediaUrlGet",
            "mediaGetId": "={{ $('WhatsApp Trigger1').item.json.messages[0].image.id }}"
        },
        "type": "n8n-nodes-base.whatsApp",
        "typeVersion": 1,
        "position": [trigger_x + 656, trigger_y - 16],
        "id": "10697ee6-c0a0-4247-adc3-a93f7e3bd0c1",
        "name": "WhatsApp Business Cloud1",
        "webhookId": "01a564ba-00b1-407c-9b0b-cd143851bd39",
        "credentials": {
            "whatsAppApi": {
                "id": "0duhem9Atjb1fCMb",
                "name": "WhatsApp send UTQ-BOT-V1"
            }
        }
    }

    wa_pdf_node = {
        "parameters": {
            "resource": "media",
            "operation": "mediaUrlGet",
            "mediaGetId": "={{ $json.messages[0].document.id }}"
        },
        "type": "n8n-nodes-base.whatsApp",
        "typeVersion": 1,
        "position": [trigger_x + 656, trigger_y + 176],
        "id": "dee5e98a-bac7-47f6-b472-f299c29404e4",
        "name": "WhatsApp Business Cloud2",
        "webhookId": "233f4695-37b7-4716-85cf-42e28369962c",
        "credentials": {
            "whatsAppApi": {
                "id": "0duhem9Atjb1fCMb",
                "name": "WhatsApp send UTQ-BOT-V1"
            }
        }
    }

    # 3. HTTP Request nodes (download media)
    http_video_node = {
        "parameters": {
            "url": "={{ $json.url }}",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "whatsAppApi",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [trigger_x + 880, trigger_y - 192],
        "id": "5b534d85-e85c-47a2-9f26-3cc9507add68",
        "name": "HTTP Request1",
        "credentials": {
            "whatsAppApi": {
                "id": "0duhem9Atjb1fCMb",
                "name": "WhatsApp send UTQ-BOT-V1"
            }
        }
    }

    http_image_node = {
        "parameters": {
            "url": "={{ $json.url }}",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "whatsAppApi",
            "options": {}
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [trigger_x + 880, trigger_y - 16],
        "id": "97e3452d-47f2-48f5-83e1-6f6c57097802",
        "name": "HTTP Request",
        "credentials": {
            "whatsAppApi": {
                "id": "0duhem9Atjb1fCMb",
                "name": "WhatsApp send UTQ-BOT-V1"
            }
        }
    }

    http_pdf_node = {
        "parameters": {
            "url": "={{ $json.url }}",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "whatsAppApi",
            "options": {
                "response": {
                    "response": {
                        "responseFormat": "file"
                    }
                }
            }
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [trigger_x + 880, trigger_y + 176],
        "id": "1b0b1d87-9fc4-41ac-85be-b4e35f8055cc",
        "name": "HTTP Request2",
        "credentials": {
            "whatsAppApi": {
                "id": "0duhem9Atjb1fCMb",
                "name": "WhatsApp send UTQ-BOT-V1"
            }
        }
    }

    # 4. Gemini Analyze nodes (EXACT structure from user)
    analyze_video_node = {
        "parameters": {
            "resource": "video",
            "operation": "analyze",
            "modelId": {
                "__rl": True,
                "value": "models/gemini-2.5-flash",
                "mode": "list",
                "cachedResultName": "models/gemini-2.5-flash"
            },
            "text": "Describe the key points of the video content. The answer must be in Spanish.",
            "inputType": "binary",
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [trigger_x + 1088, trigger_y - 192],
        "id": "45570130-700d-47db-ae2c-cde5f19c1928",
        "name": "Analyze video",
        "credentials": {
            "googlePalmApi": {
                "id": "fzxSzUoNmiHkN56C",
                "name": "Google Gemini(PaLM) Api account"
            }
        }
    }

    analyze_image_node = {
        "parameters": {
            "resource": "image",
            "operation": "analyze",
            "modelId": {
                "__rl": True,
                "value": "models/gemini-2.5-flash",
                "mode": "list",
                "cachedResultName": "models/gemini-2.5-flash"
            },
            "text": "Describe the relevant points of the image content. Use a maximum of 100 words. The answer must be in Spanish.",
            "inputType": "binary",
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [trigger_x + 1088, trigger_y - 16],
        "id": "f9d7ec00-a8bd-4991-b024-43a4364c8930",
        "name": "Analyze an image",
        "credentials": {
            "googlePalmApi": {
                "id": "fzxSzUoNmiHkN56C",
                "name": "Google Gemini(PaLM) Api account"
            }
        }
    }

    analyze_pdf_node = {
        "parameters": {
            "resource": "document",
            "modelId": {
                "__rl": True,
                "value": "models/gemini-2.5-flash",
                "mode": "list",
                "cachedResultName": "models/gemini-2.5-flash"
            },
            "text": "Give me a brief description of the document's contents. The answer must be in Spanish.",
            "inputType": "binary",
            "options": {}
        },
        "type": "@n8n/n8n-nodes-langchain.googleGemini",
        "typeVersion": 1,
        "position": [trigger_x + 1088, trigger_y + 176],
        "id": "1ff9db36-59c4-4ef1-8a0e-17f20f9d6937",
        "name": "Analyze document",
        "credentials": {
            "googlePalmApi": {
                "id": "fzxSzUoNmiHkN56C",
                "name": "Google Gemini(PaLM) Api account"
            }
        }
    }

    # 5. Preparar Texto node (for text messages to match Gemini output format)
    preparar_texto_node = {
        "parameters": {
            "assignments": {
                "assignments": [
                    {
                        "id": "prep-text-001",
                        "name": "content",
                        "value": "={{ { parts: [{ text: $json.messages[0].text.body }] } }}",
                        "type": "object"
                    }
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [trigger_x + 1088, trigger_y + 80],
        "id": "prep-texto-utq-001",
        "name": "Preparar Texto"
    }

    # 6. Edit Fields1 node (single node that receives all outputs)
    edit_fields_node = {
        "parameters": {
            "assignments": {
                "assignments": [
                    {
                        "id": "f00e1278-32dd-4638-9be7-fbe65263dd39",
                        "name": "text",
                        "value": "={{ $json.content.parts[0].text }}",
                        "type": "string"
                    }
                ]
            },
            "options": {}
        },
        "type": "n8n-nodes-base.set",
        "typeVersion": 3.4,
        "position": [trigger_x + 1376, trigger_y + 48],
        "id": "cca8b873-15f1-4f3b-87f4-87873594f490",
        "name": "Edit Fields1"
    }

    # Add all new nodes
    new_nodes = [
        switch_node,
        wa_video_node,
        wa_image_node,
        wa_pdf_node,
        http_video_node,
        http_image_node,
        http_pdf_node,
        analyze_video_node,
        analyze_image_node,
        analyze_pdf_node,
        preparar_texto_node,
        edit_fields_node
    ]

    workflow['nodes'].extend(new_nodes)
    print(f"\n✓ Added {len(new_nodes)} new multimedia nodes")

    # Update connections
    # Remove old connections related to multimedia nodes
    if 'connections' not in workflow:
        workflow['connections'] = {}

    # Clean up old connections
    for node_name in old_multimedia_node_names:
        if node_name in workflow['connections']:
            del workflow['connections'][node_name]

    # Add new connections based on user's exact structure
    workflow['connections'][whatsapp_trigger['name']] = {
        "main": [[{"node": "Switch", "type": "main", "index": 0}]]
    }

    workflow['connections']['Switch'] = {
        "main": [
            [{"node": "WhatsApp Business Cloud", "type": "main", "index": 0}],   # video
            [{"node": "WhatsApp Business Cloud1", "type": "main", "index": 0}],  # imagen
            [{"node": "WhatsApp Business Cloud2", "type": "main", "index": 0}],  # pdf
            [{"node": "Preparar Texto", "type": "main", "index": 0}]             # texto
        ]
    }

    workflow['connections']['WhatsApp Business Cloud'] = {
        "main": [[{"node": "HTTP Request1", "type": "main", "index": 0}]]
    }

    workflow['connections']['WhatsApp Business Cloud1'] = {
        "main": [[{"node": "HTTP Request", "type": "main", "index": 0}]]
    }

    workflow['connections']['WhatsApp Business Cloud2'] = {
        "main": [[{"node": "HTTP Request2", "type": "main", "index": 0}]]
    }

    workflow['connections']['HTTP Request1'] = {
        "main": [[{"node": "Analyze video", "type": "main", "index": 0}]]
    }

    workflow['connections']['HTTP Request'] = {
        "main": [[{"node": "Analyze an image", "type": "main", "index": 0}]]
    }

    workflow['connections']['HTTP Request2'] = {
        "main": [[{"node": "Analyze document", "type": "main", "index": 0}]]
    }

    workflow['connections']['Analyze video'] = {
        "main": [[{"node": "Edit Fields1", "type": "main", "index": 0}]]
    }

    workflow['connections']['Analyze an image'] = {
        "main": [[{"node": "Edit Fields1", "type": "main", "index": 0}]]
    }

    workflow['connections']['Analyze document'] = {
        "main": [[{"node": "Edit Fields1", "type": "main", "index": 0}]]
    }

    workflow['connections']['Preparar Texto'] = {
        "main": [[{"node": "Edit Fields1", "type": "main", "index": 0}]]
    }

    # Connect Edit Fields1 to Extraer datos del user
    workflow['connections']['Edit Fields1'] = {
        "main": [[{"node": "Extraer datos del user", "type": "main", "index": 0}]]
    }

    print("✓ Updated all connections")

    # Update Extraer datos del user to use the text field from Edit Fields1
    for assignment in extraer_datos_node['parameters']['assignments']['assignments']:
        if assignment['name'] == 'message':
            assignment['value'] = "={{ $json.text }}"
            print(f"✓ Updated 'Extraer datos del user' message field to use: $json.text")
            break

    # Save updated workflow
    with open('utq_bot.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print("\n✅ Successfully implemented exact multimedia logic!")
    print(f"\n📊 Workflow structure:")
    print(f"   WhatsApp Trigger → Switch →")
    print(f"      ├─ video  → WA Cloud → HTTP → Analyze video → Edit Fields1")
    print(f"      ├─ imagen → WA Cloud1 → HTTP → Analyze image → Edit Fields1")
    print(f"      ├─ pdf    → WA Cloud2 → HTTP2 → Analyze document → Edit Fields1")
    print(f"      └─ texto  → Preparar Texto → Edit Fields1")
    print(f"   Edit Fields1 → Extraer datos del user")
    print(f"\n   All paths converge at Edit Fields1 with uniform format:")
    print(f"   {{ content: {{ parts: [{{ text: '...' }}] }} }}")

if __name__ == '__main__':
    implement_exact_multimedia_logic()
