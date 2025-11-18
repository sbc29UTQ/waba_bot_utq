# Solución Optimizada: IF + Basic LLM para División de Mensajes

## Concepto

**Flujo eficiente que solo usa Basic LLM cuando es necesario:**

1. ✅ Validar longitud del mensaje (IF)
2. ✅ Si ≤130 caracteres → enviar directo (sin costo LLM)
3. ✅ Si >130 caracteres → usar Basic LLM para dividir en 2 partes
4. ✅ Enviar cada parte con delay de 5 segundos

---

## Arquitectura por Agente

```
Agente (Explore/Learn/Apply/Review/Optimize)
  ↓
IF (¿mensaje > 130 caracteres?)
  ├─ NO (≤130) → Send WhatsApp → Call Actualizar_memoria
  │
  └─ SÍ (>130) → Basic LLM Chain (divide en 2)
                    ↓
                 Code (parse JSON)
                    ↓
                 Split Out (convierte a items)
                    ↓
                 Loop Over Items (procesa cada parte)
                    ↓
                 Code (add index)
                    ↓
                 IF (¿es la primera parte?)
                    ├─ SÍ → Send WhatsApp
                    └─ NO → Wait 5 Seconds → Send WhatsApp
                              ↓
                   Call Actualizar_memoria
```

---

## Ventajas de esta Solución

✅ **Económica**: Solo usa LLM cuando el mensaje es >130 caracteres
✅ **Rápida**: Mensajes cortos se envían inmediatamente sin procesamiento
✅ **Inteligente**: División semántica cuando es necesario
✅ **Limpia**: Siempre divide en 2 partes (no 3+)
✅ **Profesional**: Mejor UX para el usuario final

---

## Implementación Paso a Paso

### Para cada agente (ejemplo con "Learn")

---

### 1️⃣ Agregar Nodo "IF" (Validar Longitud)

**Después del agente "Learn":**

1. Hacer clic en "+" después de "Learn"
2. Buscar "IF"
3. Nombrar: "Message Length Check (Learn)"

**Configuración del IF:**

- **Conditions:**
  - **Condition 1:**
    - **Value 1:** `{{ $('Learn').item.json.output.length }}`
    - **Operation:** `larger`
    - **Value 2:** `130`

**Outputs:**
- **True** (mensaje largo) → Ir a "Basic LLM Chain"
- **False** (mensaje corto) → Ir a "Send WhatsApp Message (Short)"

---

### 2️⃣ Branch FALSE: Envío Directo (≤130 caracteres)

**Nodo "Send WhatsApp Message (Short)"**

Tipo: WhatsApp

**Configuración:**
- **Operation:** Send
- **Phone Number ID:** `730111076863264`
- **Recipient Phone Number:** `{{ $('Extraer datos del user').item.json.phone_number }}`
- **Text Body:** `{{ $('Learn').item.json.output }}`

**Conectar a:** `Call 'Actualizar_memoria_utq_bot'1`

---

### 3️⃣ Branch TRUE: División con LLM (>130 caracteres)

#### A. Nodo "Basic LLM Chain" (Split in 2)

1. Hacer clic en el output TRUE del IF
2. Buscar "Basic LLM Chain"
3. Nombrar: "Split in 2 Parts (Learn)"

**Configuración:**

**Prompt:** (Copiar de `prompt_llm_split_2_parts.txt` y adaptar)

```
You are a message splitter for WhatsApp. Your ONLY task is to split a long message into exactly 2 coherent parts.

STRICT RULES:
1. Split the message into EXACTLY 2 parts
2. Each part must be MAXIMUM 130 characters
3. Split at a natural point (end of sentence, paragraph, or logical break)
4. Maintain context and readability in each part
5. Both parts together must contain the complete original message
6. Return ONLY a JSON array with exactly 2 strings

INPUT MESSAGE (more than 130 characters):
{{ $('Learn').item.json.output }}

OUTPUT FORMAT (exactly like this, no other text):
["First part of the message here", "Second part of the message here"]

IMPORTANT:
- Return ONLY the JSON array
- EXACTLY 2 strings in the array, no more, no less
- No explanations, no markdown, no code blocks
- Each string must be ≤130 characters
- Find the best natural split point around the middle of the message
```

**Model:** Conectar a "OpenAI Chat Model" o "OpenAI Chat Model2"

---

#### B. Nodo "Code" (Parse JSON)

**Nombre:** `Parse JSON (Learn)`

**Código:**

```javascript
// Obtener la respuesta del LLM
const llmOutput = $input.item.json.output || $input.item.json.text || '';

// Parsear el JSON
let messageParts = [];
try {
  // Limpiar y parsear
  const cleaned = llmOutput.trim().replace(/```json\n?/g, '').replace(/```\n?/g, '');
  messageParts = JSON.parse(cleaned);

  // Validar que sea un array con 2 elementos
  if (!Array.isArray(messageParts) || messageParts.length !== 2) {
    throw new Error('Expected exactly 2 parts');
  }
} catch (error) {
  // Si falla el parsing, dividir manualmente en 2 partes
  console.error('Error parsing JSON:', error);
  const original = $('Learn').item.json.output;
  const midPoint = Math.floor(original.length / 2);

  // Buscar espacio más cercano al punto medio
  let cutPoint = original.lastIndexOf(' ', midPoint);
  if (cutPoint === -1) cutPoint = midPoint;

  messageParts = [
    original.substring(0, cutPoint).trim(),
    original.substring(cutPoint).trim()
  ];
}

// Obtener datos adicionales
const phoneNumber = $('Extraer datos del user').item.json.phone_number;

return [{
  json: {
    message_parts: messageParts,
    phone_number: phoneNumber,
    total_parts: 2
  }
}];
```

---

#### C. Nodo "Split Out" (Convert to Items)

**Nombre:** `Split Into Items (Learn)`

**Configuración:**
- **Field to Split Out:** `message_parts`
- **Include Other Fields:** ✅ Yes
- **Destination Field Name:** `message_part`

Este nodo convierte el array `[part1, part2]` en 2 items separados.

---

#### D. Nodo "Loop Over Items"

**Nombre:** `Loop Messages (Learn)`

**Configuración:**
- Mode: Run Once for Each Item

Este nodo procesa cada parte secuencialmente (importante para el delay).

---

#### E. Nodo "Code" (Add Index)

**Dentro del Loop, nombrar:** `Add Index (Learn)`

**Código:**

```javascript
// Obtener el índice del loop
const loopNode = $input.context.getNodeParameter('Loop Messages (Learn)');
const currentIndex = $input.itemIndex;

return [{
  json: {
    ...$input.item.json,
    part_number: currentIndex + 1,
    is_first_message: currentIndex === 0
  }
}];
```

---

#### F. Nodo "IF" (Is First Message?)

**Nombre:** `Is First Message? (Learn)`

**Configuración:**
- **Condition:** `{{ $json.is_first_message }}` equals `true`

**Outputs:**
- **True** → Send WhatsApp Message (Long)
- **False** → Wait 5 Seconds

---

#### G. Nodo "Wait" (Solo para segunda parte)

**Nombre:** `Wait 5 Seconds (Learn)`

**Configuración:**
- **Wait Amount:** 5
- **Wait Unit:** Seconds

**Conectar a:** Send WhatsApp Message (Long)

---

#### H. Nodo "Send WhatsApp Message (Long)"

**Nombre:** `Send WhatsApp Message (Long)`

**Configuración:**
- **Operation:** Send
- **Phone Number ID:** `730111076863264`
- **Recipient Phone Number:** `{{ $json.phone_number }}`
- **Text Body:** `{{ $json.message_part }}`

**Conectar a:** `Call 'Actualizar_memoria_utq_bot'1`

---

## Diagrama Visual Completo

```
Learn
  ↓
Message Length Check (Learn) [IF length > 130?]
  │
  ├─ FALSE (≤130) ────────────────────────┐
  │                                       │
  │  Send WhatsApp Message (Short)       │
  │    ↓                                  │
  │                                       │
  └─ TRUE (>130)                          │
       ↓                                  │
     Split in 2 Parts (Learn) [LLM]      │
       ↓                                  │
     Parse JSON (Learn)                   │
       ↓                                  │
     Split Into Items (Learn)             │
       ↓                                  │
     Loop Messages (Learn)                │
       ↓                                  │
     Add Index (Learn)                    │
       ↓                                  │
     Is First Message? (Learn) [IF]       │
       ├─ TRUE → Send WhatsApp (Long) ───┤
       └─ FALSE → Wait 5s → Send (Long) ─┤
                                          ↓
                          Call 'Actualizar_memoria_utq_bot'1
```

---

## Casos de Uso

### Caso 1: Mensaje Corto (≤130 caracteres)

**Input:** "Hola, ¿cómo estás hoy?"

**Flujo:**
```
Learn → IF (25 chars ≤130) → FALSE → Send WhatsApp (Short) → Call Actualizar
```

**Resultado:**
- ✅ 1 mensaje enviado
- ✅ Sin delay
- ✅ Sin costo de LLM
- ⚡ Latencia mínima

---

### Caso 2: Mensaje Largo (>130 caracteres)

**Input:** "Hola, te cuento que el Business Model Canvas es una herramienta estratégica que permite visualizar y diseñar modelos de negocio de forma clara. Se compone de 9 bloques fundamentales que cubren las áreas clave." (199 caracteres)

**Flujo:**
```
Learn → IF (199 chars >130) → TRUE → LLM → Parse → Split → Loop
  → Parte 1: Send directo
  → Parte 2: Wait 5s → Send
  → Call Actualizar
```

**LLM Output:**
```json
[
  "Hola, te cuento que el Business Model Canvas es una herramienta estratégica que permite visualizar y diseñar modelos de negocio.",
  "Se compone de 9 bloques fundamentales que cubren las áreas clave."
]
```

**Resultado:**
- ✅ 2 mensajes enviados
- ✅ 5 segundos de delay entre ellos
- ✅ División inteligente (frases completas)
- 💰 Costo: ~$0.00001-$0.0001

---

## Replicar para los 5 Agentes

Repetir la estructura completa para cada agente:

| Agente | Nodo Actualizar Memoria |
|--------|-------------------------|
| **Explore** | Call 'Actualizar_memoria_utq_bot' |
| **Learn** | Call 'Actualizar_memoria_utq_bot'1 |
| **Apply** | Call 'Actualizar_memoria_utq_bot'2 |
| **Review** | Call 'Actualizar_memoria_utq_bot'3 |
| **Optimize** | Call 'Actualizar_memoria_utq_bot'4 |

**Importante:** En cada Basic LLM, adaptar:
```
{{ $('Learn').item.json.output }} → {{ $('Explore').item.json.output }}
{{ $('Learn').item.json.output }} → {{ $('Apply').item.json.output }}
... etc
```

---

## Optimizaciones Adicionales

### 1. Cache del LLM (Reducir Costos)

Si el mismo mensaje largo se repite, considera agregar cache:

```javascript
// En el nodo Parse JSON, agregar antes del try:
const cacheKey = `split_${hash($('Learn').item.json.output)}`;
const cached = $getWorkflowStaticData(cacheKey);

if (cached) {
  return [{ json: cached }];
}

// ... resto del código ...

// Después del parsing exitoso:
$setWorkflowStaticData(cacheKey, result);
```

### 2. Modelo Económico para División

Usar GPT-3.5-turbo en lugar de GPT-4 solo para la división:

- **GPT-4:** ~$0.0001 por división
- **GPT-3.5-turbo:** ~$0.00001 por división (10x más barato)

Crear un "OpenAI Chat Model" adicional solo para división con modelo `gpt-3.5-turbo`.

---

## Métricas y Monitoreo

### Agregar Nodo de Logging (Opcional)

Antes de "Call Actualizar_memoria", agregar nodo Code:

```javascript
const messageLength = $('Learn').item.json.output.length;
const usedLLM = messageLength > 130;
const parts = usedLLM ? 2 : 1;

console.log({
  agent: 'Learn',
  message_length: messageLength,
  used_llm: usedLLM,
  parts_sent: parts,
  timestamp: new Date().toISOString()
});

return [$input.item];
```

Esto te permite ver en los logs:
- Cuántos mensajes requirieron LLM
- Longitudes promedio
- Costos estimados

---

## Testing Completo

### Test 1: Mensaje Muy Corto
```
Input: "Hola"
Esperado: 1 mensaje, sin delay, sin LLM
```

### Test 2: Mensaje Justo en el Límite
```
Input: "x" * 130
Esperado: 1 mensaje, sin delay, sin LLM
```

### Test 3: Mensaje Ligeramente Largo
```
Input: "x" * 131
Esperado: 2 mensajes, 5s delay, usa LLM
```

### Test 4: Mensaje Muy Largo
```
Input: "x" * 250
Esperado: 2 mensajes, 5s delay, usa LLM
```

### Test 5: Mensaje con Saltos de Línea
```
Input: "Párrafo 1\n\nPárrafo 2\n\nPárrafo 3..." (>130)
Esperado: División inteligente en párrafos
```

---

## Comparación de Soluciones

| Característica | Solución Optimizada (IF + LLM) | Solo Código | Solo LLM |
|----------------|-------------------------------|-------------|----------|
| **Costo** | Bajo (solo cuando >130) | $0 | Alto (siempre) |
| **Velocidad (≤130)** | ⚡ Inmediata | ⚡ Inmediata | 🐌 +1-2s |
| **Velocidad (>130)** | +1-2s (LLM) | ⚡ Inmediata | +1-2s (LLM) |
| **Calidad División** | ⭐⭐⭐⭐⭐ Semántica | ⭐⭐⭐ Mecánica | ⭐⭐⭐⭐⭐ Semántica |
| **Eficiencia** | ⭐⭐⭐⭐⭐ Óptima | ⭐⭐⭐⭐ Buena | ⭐⭐ Baja |
| **Complejidad n8n** | Media (7-8 nodos) | Baja (1 nodo) | Media (5-6 nodos) |

**🏆 Ganador: Solución Optimizada IF + LLM**

---

## Costos Estimados

### Escenario: 1000 mensajes/mes

Suponiendo que **30% de mensajes >130 caracteres:**

**Solución Optimizada:**
- 700 mensajes cortos: $0 (sin LLM)
- 300 mensajes largos: 300 × $0.00001 = **$0.003/mes**
- Total: **~$0.003/mes** (insignificante)

**Solo LLM (sin IF):**
- 1000 mensajes: 1000 × $0.00001 = **$0.01/mes**

**Ahorro: ~70%** 💰

---

## Solución de Problemas

### Error: "Expected exactly 2 parts"
**Causa:** El LLM no retornó exactamente 2 partes
**Solución:** El código tiene fallback que divide manualmente

### Delay no funciona entre partes
**Causa:** Loop no está en modo secuencial
**Solución:** Verificar Loop Over Items está en "Run Once for Each Item"

### Primera parte tiene delay
**Causa:** Lógica del IF "Is First Message?" invertida
**Solución:** Verificar que `is_first_message === true` va directo a Send

### Mensaje no se divide
**Causa:** IF de longitud mal configurado
**Solución:** Verificar `{{ $('Learn').item.json.output.length }} > 130`

---

## Resumen de Nodos por Agente

### Branch Corto (≤130):
1. IF (Message Length Check)
2. Send WhatsApp Message (Short)
3. Call Actualizar_memoria

### Branch Largo (>130):
1. IF (Message Length Check)
2. Basic LLM Chain (Split in 2)
3. Code (Parse JSON)
4. Split Out
5. Loop Over Items
6. Code (Add Index)
7. IF (Is First Message?)
8. Wait 5 Seconds (solo para segunda parte)
9. Send WhatsApp Message (Long)
10. Call Actualizar_memoria

**Total: ~10 nodos por agente** (pero solo se usan 3 si el mensaje es corto)

---

## Archivos de Referencia

1. `prompt_llm_split_2_parts.txt` - Prompt optimizado para dividir en 2
2. `SOLUCION_OPTIMIZADA_IF_LLM.md` - Esta guía completa

---

## Conclusión

Esta solución optimizada ofrece **lo mejor de ambos mundos:**

✅ **Eficiencia**: Solo procesa con LLM cuando es necesario
✅ **Velocidad**: Mensajes cortos son instantáneos
✅ **Calidad**: División inteligente cuando se requiere
✅ **Economía**: Ahorra ~70% en costos vs siempre usar LLM
✅ **UX**: Mejor experiencia de usuario

**Recomendación: Implementar esta solución en los 5 agentes** 🚀
