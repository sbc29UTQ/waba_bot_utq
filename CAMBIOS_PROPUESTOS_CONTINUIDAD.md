# Cambios Propuestos para Mejorar Continuidad

## Problema Principal

**El TextClassifier NO puede mantener continuidad porque falta información clave:**
- ❌ No sabe qué agente respondió previamente
- ❌ No sabe si el usuario está en medio de un framework
- ❌ Solo guarda mensajes, sin contexto

---

## Cambios Necesarios (Prioridad ALTA)

### 1. Modificar Tabla Supabase `conversations_utq_bot`

**Agregar columnas:**

```sql
ALTER TABLE conversations_utq_bot
ADD COLUMN agent_name VARCHAR(50),      -- 'Explore', 'Learn', 'Apply', 'Review', 'Optimize'
ADD COLUMN classification VARCHAR(50);  -- 'EXPLORE', 'LEARN', 'APPLY', 'REVIEW', 'OPTIMIZE'

CREATE INDEX idx_agent_name ON conversations_utq_bot(agent_name);
CREATE INDEX idx_classification ON conversations_utq_bot(classification);
```

---

### 2. Modificar Nodos "Create a row" (5 nodos)

**En `utq_bot.json`, buscar nodos:**
- Create a row (Explore)
- Create a row1 (Learn)
- Create a row2 (Apply)
- Create a row3 (Review)
- Create a row4 (Optimize)

**Agregar campos:**

```javascript
// Ejemplo para "Create a row" (Explore):
{
  "fieldId": "agent_name",
  "fieldValue": "Explore"
},
{
  "fieldId": "classification",
  "fieldValue": "EXPLORE"
}

// Para "Create a row1" (Learn):
{
  "fieldId": "agent_name",
  "fieldValue": "Learn"
},
{
  "fieldId": "classification",
  "fieldValue": "LEARN"
}

// ... y así para Apply, Review, Optimize
```

---

### 3. Modificar Nodo "code3" (Formatear Memoria Corta)

**Ubicación:** `utq_bot.json` → nodo "code3"

**Código actual:**
```javascript
formattedText += `registro${index + 1}:
- message_user: ${row.message_user}
- message_ai: ${row.message_ai}
- created_at: ${row.created_at}

`;
```

**Código mejorado:**
```javascript
formattedText += `registro${index + 1}:
- agent: ${row.agent_name || 'Unknown'}
- category: ${row.classification || 'Unknown'}
- user: ${row.message_user}
- assistant: ${row.message_ai}
- date: ${row.created_at}

`;
```

**Resultado visible para TextClassifier:**
```
registro1:
- agent: Apply
- category: APPLY
- user: ¿Qué va en Value Proposition?
- assistant: En Value Proposition defines el valor...
- date: 2024-11-18T10:30:00
```

---

### 4. Mejorar Prompt del TextClassifier

**Ubicación:** `utq_bot.json` → nodo "Clasificacion de intencion" → `systemPromptTemplate`

**Agregar esta sección ANTES de "## CLASSIFICATION CATEGORIES":**

```markdown
---

## CONTINUITY & CONTEXT RULES

**CRITICAL**: Always check SHORT-TERM MEMORY for conversation context.

### Rule 1: Maintain Agent Continuity
- If the last interaction used a specific agent (e.g., "agent: Apply")
- AND the current message suggests continuation ("ok", "continue", "next", "siguiente")
- → Route to the SAME agent to maintain flow

### Rule 2: Respect Active Frameworks
- If SHORT-TERM MEMORY shows agent: Apply with an active framework
- AND user asks questions related to that framework
- → Route to APPLY (even if question seems like LEARN)
- The agent will provide context-specific answers

### Rule 3: Detect True Intent Changes
ONLY switch agents if:
- User explicitly asks for a different service ("explain what is...", "help me identify...")
- User indicates completion ("finished", "done", "completed")
- User changes topic completely

### Rule 4: Progression Keywords
These suggest continuation with current agent:
- "ok", "yes", "sí", "continue", "next", "siguiente"
- "what else", "and then", "después"
- "give me an example" (when in APPLY)

### Rule 5: Completion Detection
If user says:
- "finished", "done", "completed", "listo", "terminé"
- AND last agent was APPLY
- → Route to REVIEW (for feedback)

### Examples:

**Good Continuity:**
```
SHORT-TERM MEMORY shows:
  agent: Apply
  user: Help me with BMC
  assistant: Let's start with Value Proposition...

CURRENT MESSAGE: "ok, continue"
→ Classification: APPLY ✓ (maintains continuity)
```

**Good Switch:**
```
SHORT-TERM MEMORY shows:
  agent: Apply
  user: Help me with BMC
  assistant: We've completed all 9 blocks...

CURRENT MESSAGE: "what should I do now?"
→ Classification: OPTIMIZE ✓ (completed, asking for next steps)
```

**Avoid Bad Switches:**
```
SHORT-TERM MEMORY shows:
  agent: Apply
  category: APPLY
  user: What goes in Value Proposition?
  assistant: In Value Proposition you define...

CURRENT MESSAGE: "give me an example"
→ WRONG: LEARN ❌ (breaks flow)
→ CORRECT: APPLY ✓ (example in context)
```

---
```

---

### 5. Guardar Respuesta del Asistente en Zep

**Ubicación:** `actualizar_memoria_utq_bot.json` → nodo "actualiza la memoria"

**Modificar el workflow para pasar AMBOS mensajes:**

#### 5.1. Modificar nodos "Call Actualizar_memoria" (5 nodos)

**Agregar parámetro `ai_response`:**

```javascript
// En cada nodo "Call 'Actualizar_memoria_utq_bot'":
{
  "workflowInputs": {
    "value": {
      "session_id": "{{ phone_number }}",
      "query": "{{ user_message }}",
      "ai_response": "{{ $('Agente').item.json.output }}"  // ← NUEVO
    }
  }
}
```

**Ejemplo para cada agente:**
- Explore: `"ai_response": "{{ $('Explore').item.json.output }}"`
- Learn: `"ai_response": "{{ $('Learn').item.json.output }}"`
- Apply: `"ai_response": "{{ $('Apply').item.json.output }}"`
- Review: `"ai_response": "{{ $('Review').item.json.output }}"`
- Optimize: `"ai_response": "{{ $('Optimize').item.json.output }}"`

#### 5.2. Modificar `actualizar_memoria_utq_bot.json`

**Nodo "actualiza la memoria" - jsonBody:**

**Antes:**
```json
{
  "messages": [
    {
      "content": "{{ user_query }}",
      "role_type": "user"
    }
  ]
}
```

**Después:**
```json
{
  "messages": [
    {
      "content": "{{ user_query }}",
      "role_type": "user"
    },
    {
      "content": "{{ ai_response }}",
      "role_type": "assistant"
    }
  ]
}
```

---

## Resumen de Archivos a Modificar

| Archivo | Nodos a Modificar | Cambios |
|---------|------------------|---------|
| **Supabase DB** | conversations_utq_bot | Agregar columnas `agent_name`, `classification` |
| **utq_bot.json** | Create a row (x5) | Agregar campos agent_name, classification |
| **utq_bot.json** | code3 | Incluir agent_name en formato output |
| **utq_bot.json** | Clasificacion de intencion | Agregar reglas de continuidad al prompt |
| **utq_bot.json** | Call Actualizar_memoria (x5) | Pasar parámetro ai_response |
| **actualizar_memoria_utq_bot.json** | actualiza la memoria | Guardar mensaje del asistente en Zep |

---

## Impacto Esperado

### Antes (Sin cambios):
```
Usuario: "Ayúdame con el BMC"
→ APPLY
Apply: "Empecemos con Value Proposition..."

Usuario: "Dame un ejemplo"
→ LEARN ❌ (pierde contexto)
Learn: "El BMC es una herramienta..." (respuesta genérica)
```

### Después (Con cambios):
```
Usuario: "Ayúdame con el BMC"
→ APPLY
Apply: "Empecemos con Value Proposition..."

Usuario: "Dame un ejemplo"
→ APPLY ✓ (mantiene contexto)
Apply: "Por ejemplo, si tu producto es una app..." (ejemplo específico del bloque)
```

---

## Orden de Implementación

### Fase 1 (Básica - 30 min):
1. ✅ Agregar columnas a Supabase
2. ✅ Modificar 5 nodos "Create a row"
3. ✅ Modificar nodo "code3"

**Resultado:** TextClassifier puede ver qué agente respondió

---

### Fase 2 (Mejorada - 15 min):
4. ✅ Mejorar prompt del TextClassifier

**Resultado:** Lógica de continuidad implementada

---

### Fase 3 (Completa - 30 min):
5. ✅ Modificar 5 nodos "Call Actualizar_memoria"
6. ✅ Modificar "actualizar_memoria_utq_bot.json"

**Resultado:** Memoria completa en Zep (user + assistant)

---

## Testing

### Test 1: Continuidad Simple
```
1. Usuario: "Ayúdame a crear mi BMC"
   Esperado: APPLY

2. Usuario: "Ok, continúa"
   Esperado: APPLY (mismo agente)
```

### Test 2: Ejemplo en Contexto
```
1. Usuario: "Apliquemos SWOT"
   Esperado: APPLY

2. Usuario: "Dame un ejemplo"
   Esperado: APPLY (no LEARN)
```

### Test 3: Cambio Legítimo
```
1. Usuario: "Ayúdame con BMC"
   Esperado: APPLY

2. Usuario: "Ya terminé, ¿qué sigue?"
   Esperado: OPTIMIZE (cambio apropiado)
```

### Test 4: Nueva Pregunta
```
1. Usuario: "Apliquemos BMC"
   Esperado: APPLY

2. Usuario: "¿Qué es el Lean Canvas?"
   Esperado: LEARN (nueva pregunta, diferente framework)
```

---

## Métricas de Éxito

- **Continuidad:** >90% de mensajes que deberían mantener agente, lo hacen
- **Cambios Correctos:** >95% de cambios de agente son apropiados
- **UX:** Conversaciones se sienten naturales y fluidas

---

## Costo de Implementación

- **Tiempo:** ~1.5 horas total
- **Riesgo:** Bajo (no afecta lógica existente)
- **Reversible:** Sí (solo agregar columnas, no se elimina nada)
- **Impacto:** Alto (mejora significativa en UX)

---

## Conclusión

Estos cambios son **críticos** para que el sistema funcione como se espera:

✅ **Simple de implementar** (principalmente agregar campos)
✅ **Alto impacto** (continuidad natural de conversación)
✅ **Bajo riesgo** (cambios aditivos, no destructivos)
✅ **Escalable** (permite mejoras futuras con framework_context)

**Recomendación:** Implementar Fase 1 y 2 inmediatamente (45 min de trabajo).
