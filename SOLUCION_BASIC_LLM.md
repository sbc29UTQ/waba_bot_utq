# Solución: División Inteligente de Mensajes con Basic LLM

## Arquitectura de la Solución

Usar un **Basic LLM de LangChain** para dividir mensajes de forma inteligente en lugar de solo por caracteres.

### Ventajas de usar Basic LLM:
✅ División semántica (por contexto, no solo por caracteres)
✅ Mantiene coherencia en cada parte
✅ Respeta puntos naturales de corte
✅ Puede resumir si es necesario
✅ Más profesional y legible

---

## Flujo por Agente

```
Agente (Explore/Learn/Apply/Review/Optimize)
    ↓
Basic LLM Chain (divide en partes)
    ↓
Code (parse JSON response)
    ↓
Split Out (convierte array en items)
    ↓
Loop Over Items (procesa secuencialmente)
    ↓
IF (¿es el primer mensaje?)
    ├─ NO → Wait 5 seconds → Send WhatsApp
    └─ SÍ → Send WhatsApp (sin delay)
    ↓
Call 'Actualizar_memoria_utq_bot'
```

---

## Implementación Paso a Paso

### 1. Agregar Nodo "Basic LLM Chain"

**Después de cada agente (ejemplo: Learn):**

1. Hacer clic en "+" después del nodo "Learn"
2. Buscar "Basic LLM Chain"
3. Nombrar: "Split Message LLM (Learn)"

**Configuración del nodo:**

- **Prompt:** (Copiar contenido de `prompt_basic_llm_division.txt` y adaptar)

```
You are a message formatter for WhatsApp. Your task is to take a message and split it into parts if it's longer than 130 characters.

RULES:
1. If the message is 130 characters or less: return it as-is in a JSON array with one element
2. If the message is longer than 130 characters: split it into 2-3 coherent parts
3. Each part must be maximum 130 characters
4. Split at natural points (paragraphs, sentences, logical breaks)
5. Maintain context and readability in each part
6. Return ONLY a JSON array of strings, nothing else

INPUT MESSAGE:
{{ $('Learn').item.json.output }}

OUTPUT FORMAT (exactly like this):
["Part 1 text here", "Part 2 text here", "Part 3 text here"]

Or if short:
["Complete message here"]

IMPORTANT:
- Return ONLY the JSON array
- No explanations
- No markdown
- No extra text
- Each string must be ≤130 characters
```

- **Model:** Conectar a "OpenAI Chat Model" o "OpenAI Chat Model2" existente
- **Output Parser:** Text (default)

---

### 2. Agregar Nodo "Code" (Parse JSON)

Después de "Split Message LLM":

**Nombre:** "Parse JSON Response (Learn)"

**Código:**

```javascript
// Obtener la respuesta del LLM
const llmOutput = $input.item.json.output || $input.item.json.text || '';

// Parsear el JSON
let messageParts = [];
try {
  // Intentar parsear como JSON
  messageParts = JSON.parse(llmOutput.trim());

  // Validar que sea un array
  if (!Array.isArray(messageParts)) {
    // Si no es array, usar como un solo mensaje
    messageParts = [llmOutput];
  }
} catch (error) {
  // Si falla el parsing, usar el mensaje completo como una parte
  console.error('Error parsing JSON:', error);
  messageParts = [llmOutput];
}

// Obtener el número de teléfono
const phoneNumber = $('Extraer datos del user').item.json.phone_number;

// Retornar como un solo item con el array
return [{
  json: {
    message_parts: messageParts,
    phone_number: phoneNumber,
    total_parts: messageParts.length
  }
}];
```

---

### 3. Agregar Nodo "Split Out"

Después de "Parse JSON Response":

**Nombre:** "Split Into Items (Learn)"

**Configuración:**
- **Field to Split Out:** `message_parts`
- **Include Other Fields:** ✅ Yes
- **Destination Field Name:** `message_part`

Este nodo convierte el array `message_parts` en items individuales.

---

### 4. Agregar Nodo "Loop Over Items"

Después de "Split Into Items":

**Nombre:** "Loop Messages (Learn)"

Este nodo procesará cada parte del mensaje secuencialmente (importante para el delay).

---

### 5. Agregar Nodo "Code" (Add Index)

Dentro del Loop, primero agregar un nodo Code:

**Nombre:** "Add Message Index (Learn)"

**Código:**

```javascript
// Obtener el índice del item actual en el loop
const currentIndex = $input.context.nodesExecutionData.Loop Messages (Learn).itemIndex;
const totalParts = $input.item.json.total_parts;

return [{
  json: {
    ...$input.item.json,
    part_number: currentIndex + 1,
    is_first_message: currentIndex === 0
  }
}];
```

---

### 6. Agregar Nodo "IF"

Después de "Add Message Index":

**Nombre:** "Is First Message? (Learn)"

**Configuración:**
- **Condición:** `{{ $json.is_first_message }}` equals `true`

**Outputs:**
- **True** → Ir directo a "Send WhatsApp Message"
- **False** → Ir a "Wait 5 Seconds"

---

### 7. Agregar Nodo "Wait"

En el branch False del IF:

**Nombre:** "Wait 5 Seconds (Learn)"

**Configuración:**
- **Wait Amount:** 5
- **Wait Unit:** Seconds
- **Continuar en:** Conectar a "Send WhatsApp Message"

---

### 8. Modificar/Agregar Nodo "Send WhatsApp Message"

**Nombre:** "Send WhatsApp Message (Learn)"

**Configuración:**
- **Operation:** Send
- **Phone Number ID:** 730111076863264
- **Recipient Phone Number:** `{{ $json.phone_number }}`
- **Text Body:** `{{ $json.message_part }}`

---

### 9. Conectar al resto del flujo

Después de "Send WhatsApp Message", conectar a:
- "Call 'Actualizar_memoria_utq_bot'1" (o el que corresponda)

---

## Diagrama Visual

```
Learn
  ↓
Split Message LLM (Learn)  [usa prompt para dividir inteligentemente]
  ↓
Parse JSON Response (Learn)  [parsea JSON del LLM]
  ↓
Split Into Items (Learn)  [convierte array en items]
  ↓
Loop Messages (Learn)  [procesa cada parte secuencialmente]
  ↓
Add Message Index (Learn)  [agrega índice y flag is_first]
  ↓
Is First Message? (Learn)  [IF condition]
  ├─ TRUE  → Send WhatsApp Message (Learn)
  └─ FALSE → Wait 5 Seconds (Learn) → Send WhatsApp Message (Learn)
                                              ↓
                                   Call 'Actualizar_memoria_utq_bot'1
```

---

## Replicar para los 5 Agentes

Repetir el flujo completo para:
- **Explore** (usar OpenAI Chat Model)
- **Learn** (usar OpenAI Chat Model2)
- **Apply** (usar OpenAI Chat Model)
- **Review** (usar OpenAI Chat Model2)
- **Optimize** (usar OpenAI Chat Model)

**Importante:** Adaptar los nombres de nodos en el prompt del Basic LLM:
- `{{ $('Learn').item.json.output }}` → `{{ $('Explore').item.json.output }}`
- `{{ $('Learn').item.json.output }}` → `{{ $('Apply').item.json.output }}`
- etc.

---

## Ventajas de esta Solución

### 1. División Inteligente
- El LLM entiende el contexto
- Divide por frases completas
- Mantiene coherencia semántica

### 2. Visual en n8n
- Fácil de debuggear
- Se ve el flujo completo
- Logs claros de cada paso

### 3. Flexible
- Fácil ajustar el prompt si necesitas cambiar lógica
- Puedes agregar más reglas al LLM
- Puedes cambiar el max length fácilmente

### 4. Profesional
- Mensajes mejor formateados
- División natural
- Mejor experiencia de usuario

---

## Alternativa Simplificada (Sin Loop)

Si prefieres una versión más simple sin el nodo Loop:

```
Agente
  ↓
Basic LLM (divide mensaje)
  ↓
Code (parse + envía directamente cada parte con delay)
  ↓
Call 'Actualizar_memoria_utq_bot'
```

**Código alternativo (auto-contenido con delay):**

```javascript
const llmOutput = $input.item.json.output || $input.item.json.text || '';
const phoneNumber = $('Extraer datos del user').item.json.phone_number;
const PHONE_NUMBER_ID = '730111076863264';
const ACCESS_TOKEN = '{{ $credentials.whatsAppTriggerApi.accessToken }}';

// Parsear partes del mensaje
let messageParts = [];
try {
  messageParts = JSON.parse(llmOutput.trim());
  if (!Array.isArray(messageParts)) messageParts = [llmOutput];
} catch (error) {
  messageParts = [llmOutput];
}

// Función para enviar mensaje
async function sendWhatsApp(phone, text) {
  const url = `https://graph.facebook.com/v21.0/${PHONE_NUMBER_ID}/messages`;
  return await $http.request({
    method: 'POST',
    url: url,
    headers: {
      'Authorization': `Bearer ${ACCESS_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: {
      messaging_product: 'whatsapp',
      to: phone,
      type: 'text',
      text: { body: text }
    },
    json: true
  });
}

// Función delay
const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Enviar cada parte con delay
const results = [];
for (let i = 0; i < messageParts.length; i++) {
  if (i > 0) await wait(5000);  // 5 segundos delay

  try {
    const response = await sendWhatsApp(phoneNumber, messageParts[i]);
    results.push({ part: i + 1, success: true, response });
  } catch (error) {
    results.push({ part: i + 1, success: false, error: error.message });
  }
}

return [{ json: { results, total_parts: messageParts.length } }];
```

---

## Testing

### Caso 1: Mensaje corto
**Input:** "Hola, ¿cómo estás?"
**Esperado:** 1 mensaje, sin delay

### Caso 2: Mensaje medio
**Input:** Texto de 200 caracteres
**Esperado:** 2 mensajes, 5s delay entre ellos

### Caso 3: Mensaje largo
**Input:** Texto de 400 caracteres
**Esperado:** 3 mensajes, 5s delay entre cada uno

---

## Costos

⚠️ **Importante:** Cada división de mensaje usa el Basic LLM, lo que implica:
- ~50-100 tokens por llamada (input + output)
- Si usas GPT-4: ~$0.0001 por división
- Si usas GPT-3.5: ~$0.00001 por división

**Alternativa económica:** Usar modelo más económico solo para división (GPT-3.5-turbo)

---

## Notas Finales

✅ **Más inteligente** que división por caracteres
✅ **Mejor UX** para el usuario final
✅ **Fácil de mantener** visualmente en n8n
⚠️ **Costo adicional** por uso de LLM
⚠️ **Latencia adicional** por procesamiento LLM (~1-2s)

---

¿Prefieres la versión con Loop (más nodos pero más claro) o la versión auto-contenida (menos nodos pero en código)?
