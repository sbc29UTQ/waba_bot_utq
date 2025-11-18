# Análisis: Continuidad del TextClassifier con Agentes

## Estado Actual del Sistema

### 1. Flujo de Clasificación

```
Usuario envía mensaje
    ↓
Extraer datos del user
    ↓
Buscar Memorias1 (Zep - memoria larga)
    ↓
code2 (formatea facts de Zep)
    ↓
Conseguir Memorias (Supabase - memoria corta)
    ↓
code3 (formatea últimas 5 conversaciones)
    ↓
Clasificacion de intencion (TextClassifier)
    ├─ EXPLORE → Agente Explore
    ├─ LEARN → Agente Learn
    ├─ APPLY → Agente Apply
    ├─ REVIEW → Agente Review
    └─ OPTIMIZE → Agente Optimize
```

---

## 2. Datos Disponibles para el TextClassifier

### A. LONG-TERM MEMORY (Zep - code2)
**Fuente:** `Buscar Memorias1` → Zep Graph Search

**Qué busca:**
```json
{
  "query": "mensaje del usuario",
  "user_id": "phone_number",
  "limit": 3,
  "scopes": "edges",
  "search_filters": {
    "min_relevance": 0.7
  }
}
```

**Qué retorna:**
```
fact1: [información relevante del grafo de conocimiento]
fact2: [información relevante del grafo de conocimiento]
fact3: [información relevante del grafo de conocimiento]
```

**Formato (code2):**
```javascript
facts_text: "fact1: contenido fact2: contenido fact3: contenido"
```

### B. SHORT-TERM MEMORY (Supabase - code3)
**Fuente:** `Conseguir Memorias` → tabla `conversations_utq_bot`

**Qué trae:**
- Últimas 5 conversaciones ordenadas por `created_at DESC`
- Campos: `message_user`, `message_ai`, `created_at`

**Formato (code3):**
```
registro1:
- message_user: [mensaje del usuario]
- message_ai: [respuesta del agente]
- created_at: [fecha]

registro2:
- message_user: [mensaje del usuario]
- message_ai: [respuesta del agente]
- created_at: [fecha]
...
```

### C. CURRENT MESSAGE
```
message: "mensaje actual del usuario"
```

---

## 3. ❌ PROBLEMAS IDENTIFICADOS

### Problema 1: Falta Identificación del Agente Activo

**Situación actual:**
```javascript
// En Supabase solo se guarda:
{
  conversation_id: "phone_number",
  phone_number: "phone_number",
  message_user: "mensaje del usuario",
  message_ai: "respuesta del agente",  // ❌ NO dice QUÉ agente
  created_at: "timestamp"
}
```

**Impacto:**
- ❌ El TextClassifier no sabe qué agente respondió previamente
- ❌ No puede mantener continuidad con el mismo agente
- ❌ Puede cambiar de agente inadecuadamente

**Ejemplo del problema:**
```
Usuario: "Ayúdame a crear mi Business Model Canvas"
→ Clasificado como APPLY → Agente Apply
Agente Apply: "Perfecto, empecemos con el primer bloque..."

Usuario: "Ok, continúa"
→ Clasificado como EXPLORE (porque no tiene contexto) ❌ INCORRECTO
→ Debería seguir con APPLY
```

---

### Problema 2: Falta Contexto del Framework en Uso

**Situación actual:**
- ✅ Se guarda la respuesta del agente
- ❌ NO se guarda qué framework se está usando
- ❌ NO se guarda en qué paso/bloque está el usuario

**Impacto:**
- ❌ Si el usuario está en medio de completar un BMC, el sistema no lo sabe
- ❌ El TextClassifier puede interrumpir el flujo
- ❌ Se pierde el progreso del framework

**Ejemplo del problema:**
```
Usuario: "Ayúdame con el Business Model Canvas"
→ APPLY → Agente Apply
Apply: "Empecemos con Value Proposition..."

Usuario: "Dame un ejemplo"
→ Clasificado como LEARN (pide ejemplo) ❌ INCORRECTO
→ Debería mantenerse en APPLY (ejemplo del bloque actual)
```

---

### Problema 3: Falta Estado de la Conversación

**Situación actual:**
- ❌ NO hay tracking del estado (iniciando, en progreso, completado)
- ❌ NO hay metadata sobre el contexto de la conversación

**Impacto:**
- ❌ No se sabe si el usuario está en una tarea específica
- ❌ No se puede distinguir entre preguntas tangenciales y flujo principal

**Ejemplo del problema:**
```
Usuario: "Ayúdame a aplicar SWOT"
→ APPLY → Agente Apply
Apply: "Empecemos con Strengths (Fortalezas)..."

Usuario: "¿Qué es SWOT?"
→ Clasificado como LEARN ❌ Interrumpe el flujo
→ Ideal: APPLY responde brevemente y continúa
```

---

### Problema 4: Memoria de Zep No Incluye Respuestas del Asistente

**Situación actual:**
```javascript
// En actualizar_memoria_utq_bot.json:
{
  "messages": [
    {
      "content": "mensaje del usuario",
      "role_type": "user"  // ✓ OK
    }
    // ❌ Falta el mensaje del asistente
  ]
}
```

**Impacto:**
- ❌ Zep no construye el grafo con las respuestas del asistente
- ❌ Se pierde información valiosa del contexto
- ❌ La memoria larga está incompleta

---

### Problema 5: Formato de Memoria Corta Limitado

**Situación actual:**
```
registro1:
- message_user: texto
- message_ai: texto
- created_at: fecha
```

**Limitaciones:**
- ❌ No dice qué agente respondió
- ❌ No dice qué categoría fue clasificada
- ❌ No tiene metadata (framework, paso, estado)

---

## 4. ✅ SOLUCIONES PROPUESTAS

### Solución 1: Agregar Campo `agent_name` a la Base de Datos

**Cambio en tabla Supabase `conversations_utq_bot`:**

```sql
ALTER TABLE conversations_utq_bot
ADD COLUMN agent_name VARCHAR(50);  -- 'Explore', 'Learn', 'Apply', 'Review', 'Optimize'

ADD COLUMN classification VARCHAR(50);  -- Categoría clasificada

CREATE INDEX idx_agent_name ON conversations_utq_bot(agent_name);
CREATE INDEX idx_classification ON conversations_utq_bot(classification);
```

**Modificar nodos "Create a row" (5 nodos, uno por agente):**

**Antes:**
```javascript
{
  "conversation_id": "{{ phone_number }}",
  "phone_number": "{{ phone_number }}",
  "message_user": "{{ humanMessage }}",
  "message_ai": "{{ aiMessage }}",
  "created_at": "timestamp"
}
```

**Después (ejemplo para agente Learn):**
```javascript
{
  "conversation_id": "{{ phone_number }}",
  "phone_number": "{{ phone_number }}",
  "message_user": "{{ humanMessage }}",
  "message_ai": "{{ aiMessage }}",
  "agent_name": "Learn",                    // ← NUEVO
  "classification": "LEARN",                 // ← NUEVO
  "created_at": "timestamp"
}
```

---

### Solución 2: Agregar Campo `framework_context` (Metadata)

**Cambio en tabla Supabase:**

```sql
ALTER TABLE conversations_utq_bot
ADD COLUMN framework_context JSONB;  -- Metadata flexible
```

**Ejemplo de uso:**
```json
{
  "framework_context": {
    "framework": "Business Model Canvas",
    "step": "Value Proposition",
    "step_number": 1,
    "total_steps": 9,
    "status": "in_progress"
  }
}
```

**Cómo capturarlo:**
Agregar un nodo "Code" después de cada agente que extraiga el contexto del output del agente usando un LLM o expresiones regulares.

---

### Solución 3: Mejorar Formato de code3 (Memoria Corta)

**Código actual de code3:**
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
- classification: ${row.classification || 'Unknown'}
- message_user: ${row.message_user}
- message_ai: ${row.message_ai}
- framework: ${row.framework_context?.framework || 'None'}
- status: ${row.framework_context?.status || 'N/A'}
- created_at: ${row.created_at}

`;
```

**Beneficio:**
```
registro1:
- agent: Apply
- classification: APPLY
- message_user: ¿Qué va en Value Proposition?
- message_ai: En Value Proposition defines qué problema resuelves...
- framework: Business Model Canvas
- status: in_progress
- created_at: 2024-11-18T10:30:00
```

---

### Solución 4: Guardar Respuesta del Asistente en Zep

**Modificar `actualizar_memoria_utq_bot.json`:**

**Antes:**
```json
{
  "messages": [
    {
      "content": "{{ query }}",
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
      "content": "{{ user_message }}",
      "role_type": "user"
    },
    {
      "content": "{{ ai_response }}",
      "role_type": "assistant"
    }
  ]
}
```

**Cambio en flujo:**
```
Agente → Code (extrae user + ai response) → Call Actualizar_memoria (con ambos)
```

---

### Solución 5: Mejorar Prompt del TextClassifier

**Agregar al systemPromptTemplate:**

```markdown
## CONTINUITY RULES

When analyzing the conversation:

1. **Check Last Agent**: Look at SHORT-TERM MEMORY for the last agent that responded
   - If last agent was APPLY and user continues → likely stay in APPLY
   - Only switch agents if intent clearly changes

2. **Check Active Framework**: Look for framework in progress
   - If user is working on a specific framework → maintain APPLY until complete
   - If user asks conceptual question mid-framework → stay in APPLY (explain briefly)

3. **Detect Progression Keywords**:
   - "next", "continue", "ok", "siguiente" → maintain current agent
   - "what is", "explain" during APPLY → stay in APPLY (contextual explanation)
   - "help me identify" → switch to EXPLORE only if no active framework

4. **Framework Completion**:
   - If user says "finished", "completed", "listo" → route to REVIEW
   - If framework is complete → suggest next steps via OPTIMIZE

## EXAMPLES OF CONTINUITY

**Good Continuity:**
```
Last: APPLY (Business Model Canvas, step 2/9)
User: "What should I put here?"
→ APPLY (continues in context)
```

**Good Switch:**
```
Last: APPLY (Business Model Canvas, completed)
User: "What do I do now?"
→ OPTIMIZE (next steps after completion)
```

**Bad Switch (avoid):**
```
Last: APPLY (SWOT, in progress)
User: "Give me an example"
→ LEARN ❌ WRONG
→ APPLY ✓ CORRECT (example in context of current framework)
```
```

---

### Solución 6: Agregar Nodo de "Context Extractor" (LLM Ligero)

**Nuevo nodo entre Agente y Create a row:**

```
Agente (output)
    ↓
Context Extractor (Basic LLM)
    ↓
Code (parse context)
    ↓
Create a row (con metadata enriquecida)
```

**Prompt del Context Extractor:**
```markdown
Extract structured context from this AI assistant response.

ASSISTANT RESPONSE:
{{ $('Learn').item.json.output }}

Return ONLY a JSON object:
{
  "framework": "name of framework mentioned or null",
  "status": "starting|in_progress|completed|none",
  "step": "current step/block/phase or null",
  "topic": "main topic discussed"
}

Examples:
- "Let's start with the Business Model Canvas..." → {"framework": "Business Model Canvas", "status": "starting", "step": null, "topic": "BMC"}
- "Now for the Value Proposition block..." → {"framework": "Business Model Canvas", "status": "in_progress", "step": "Value Proposition", "topic": "BMC Value Proposition"}
```

---

## 5. IMPLEMENTACIÓN PRIORITARIA

### 🔥 Cambios Críticos (Implementar PRIMERO):

**1. Agregar `agent_name` a Supabase** ⭐⭐⭐⭐⭐
   - Impacto: Alto
   - Esfuerzo: Bajo
   - Permite tracking básico de continuidad

**2. Modificar code3 para mostrar agent** ⭐⭐⭐⭐⭐
   - Impacto: Alto
   - Esfuerzo: Muy Bajo
   - Mejor input para TextClassifier

**3. Mejorar prompt del TextClassifier** ⭐⭐⭐⭐
   - Impacto: Medio-Alto
   - Esfuerzo: Bajo
   - Mejor lógica de continuidad

**4. Guardar AI response en Zep** ⭐⭐⭐⭐
   - Impacto: Medio-Alto
   - Esfuerzo: Medio
   - Mejor memoria larga

### 📊 Cambios Avanzados (Implementar DESPUÉS):

**5. Agregar `framework_context` JSONB** ⭐⭐⭐
   - Impacto: Alto (largo plazo)
   - Esfuerzo: Alto
   - Requiere Context Extractor LLM

**6. Context Extractor LLM** ⭐⭐⭐
   - Impacto: Alto (largo plazo)
   - Esfuerzo: Alto
   - Costo adicional de LLM

---

## 6. FLUJO MEJORADO PROPUESTO

```
Usuario envía mensaje
    ↓
Extraer datos del user
    ↓
Buscar Memorias1 (Zep - con AI responses) ✓ Mejorado
    ↓
code2 (formatea facts de Zep)
    ↓
Conseguir Memorias (Supabase - con agent_name) ✓ Mejorado
    ↓
code3 (muestra agent + framework context) ✓ Mejorado
    ↓
Clasificacion de intencion (con mejor prompt) ✓ Mejorado
    ├─ Detecta último agente activo
    ├─ Detecta framework en progreso
    ├─ Mantiene continuidad inteligentemente
    └─ Clasifica correctamente
    ↓
Agente correspondiente
    ↓
Context Extractor (opcional) ⭐ Nuevo
    ↓
Create a row (con agent_name + metadata) ✓ Mejorado
    ↓
Call Actualizar_memoria (con user + AI) ✓ Mejorado
```

---

## 7. COMPARACIÓN ANTES/DESPUÉS

### ANTES (Actual):

**Memoria Corta:**
```
registro1:
- message_user: ¿Qué va en Value Proposition?
- message_ai: En Value Proposition defines...
- created_at: 2024-11-18
```

**Problema:** No sabe qué agente, qué framework, qué estado

---

### DESPUÉS (Mejorado):

**Memoria Corta:**
```
registro1:
- agent: Apply
- classification: APPLY
- message_user: ¿Qué va en Value Proposition?
- message_ai: En Value Proposition defines...
- framework: Business Model Canvas
- status: in_progress
- created_at: 2024-11-18
```

**Ventaja:** Contexto completo para continuidad

---

## 8. EJEMPLO DE CASO DE USO MEJORADO

### Conversación:

**Turno 1:**
```
Usuario: "Ayúdame a crear mi Business Model Canvas"
→ TextClassifier: APPLY (nuevo framework)
→ Agente Apply: "Perfecto, empecemos con Value Proposition..."
→ Guarda: agent=Apply, framework=BMC, status=starting
```

**Turno 2:**
```
Usuario: "Ok, continúa"
→ TextClassifier ve memoria:
  - Last agent: Apply
  - Framework: Business Model Canvas
  - Status: starting
→ APPLY (mantiene continuidad) ✓
→ Agente Apply: "Para Value Proposition, define..."
→ Guarda: agent=Apply, framework=BMC, status=in_progress
```

**Turno 3:**
```
Usuario: "Dame un ejemplo"
→ TextClassifier ve memoria:
  - Last agent: Apply
  - Framework: Business Model Canvas
  - Status: in_progress
→ APPLY (ejemplo en contexto) ✓
→ Agente Apply: "Por ejemplo, si tu negocio es..."
→ Guarda: agent=Apply, framework=BMC, status=in_progress
```

**Turno 4:**
```
Usuario: "Ya terminé todos los bloques"
→ TextClassifier ve memoria:
  - Last agent: Apply
  - Framework: Business Model Canvas
  - Status: in_progress
→ REVIEW (pide revisión de trabajo completo) ✓
→ Agente Review: "Excelente, déjame revisar..."
→ Guarda: agent=Review, framework=BMC, status=completed
```

---

## 9. MÉTRICAS DE ÉXITO

Para validar las mejoras, medir:

1. **Tasa de Continuidad**
   - % de veces que mantiene el mismo agente cuando debería
   - Meta: >90%

2. **Cambios Correctos**
   - % de veces que cambia de agente apropiadamente
   - Meta: >95%

3. **Satisfacción del Usuario**
   - Feedback sobre fluidez de conversación
   - Meta: "Conversation feels natural"

4. **Completitud de Frameworks**
   - % de frameworks iniciados que se completan
   - Meta: >70%

---

## 10. RESUMEN DE RECOMENDACIONES

### Prioridad ALTA (Implementar YA):
1. ✅ Agregar columna `agent_name` a Supabase
2. ✅ Modificar los 5 nodos "Create a row" para guardar agent_name
3. ✅ Modificar code3 para incluir agent_name en formatted_memories
4. ✅ Mejorar prompt del TextClassifier con reglas de continuidad

### Prioridad MEDIA (Próxima iteración):
5. ✅ Guardar respuesta del asistente en Zep
6. ✅ Agregar columna `classification` a Supabase

### Prioridad BAJA (Futuro):
7. ⭐ Agregar columna `framework_context` JSONB
8. ⭐ Implementar Context Extractor LLM

---

## Conclusión

El sistema actual **NO tiene continuidad robusta** porque:
- ❌ No sabe qué agente respondió previamente
- ❌ No sabe si hay un framework activo
- ❌ No guarda el estado de la conversación

Las mejoras propuestas **permiten mantener continuidad** mediante:
- ✅ Tracking del agente activo
- ✅ Contexto del framework en uso
- ✅ Memoria completa (user + assistant)
- ✅ Prompt mejorado con lógica de continuidad

**Impacto esperado:** UX 10x mejor, conversaciones más naturales, mayor completitud de tareas.
