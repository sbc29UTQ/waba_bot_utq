# 🔍 Análisis: Continuidad vs Multimedia en TextClassifier

## ❌ PROBLEMA IDENTIFICADO

### Escenario:
1. Usuario está con agente **Apply** (aplicando framework)
2. Apply pregunta: **"¿Deseas revisar algo o actualizar?"**
3. Usuario envía **IMAGEN de framework completo**

### Conflicto de Reglas:

**🔴 CONTINUITY RULES (Prioridad más alta):**
- "ANSWERING ASSISTANT'S QUESTIONS = SAME AGENT"
- Usuario está respondiendo → Mantener **APPLY**

**🟡 MULTIMEDIA RULE 1:**
- "Image/PDF of completed frameworks → REVIEW"
- Imagen de framework → Clasificar como **REVIEW**

**🟡 MULTIMEDIA RULE 3:**
- "Multimedia in mid-conversation → CONTINUITY RULES FIRST"
- En conversación activa → Aplicar CONTINUITY primero

### Resultado Actual:
```
Apply pregunta: "¿Deseas revisar algo?"
Usuario envía: [imagen de BMC completo]
→ TextClassifier: Mantiene APPLY ✓ (por continuidad)
→ Apply recibe imagen y debe dar feedback
→ PROBLEMA: Apply NO especializado en evaluación detallada
```

---

## 📊 CASOS DE USO ANALIZADOS

### ✅ CASO 1: Solicitud de datos (Continuidad CORRECTA)
```
Apply: "¿Cuáles son tus segmentos de clientes?"
User: [imagen con lista de segmentos]
→ Mantener APPLY ✓
→ Usuario proporciona información solicitada visualmente
```

### ✅ CASO 2: Solicitud de contexto (Continuidad CORRECTA)
```
Apply: "¿Puedes describir tu proceso actual?"
User: [imagen de diagrama de flujo]
→ Mantener APPLY ✓
→ Usuario muestra contexto solicitado visualmente
```

### ❌ CASO 3: Pregunta sobre revisión + Framework completo (Continuidad INCORRECTA)
```
Apply: "¿Deseas revisar algo o actualizar?"
User: [imagen de Business Model Canvas completo]
→ Actualmente: Mantiene APPLY ❌
→ Debería: Cambiar a REVIEW ✓
→ Razón: Usuario cambió intención → Quiere feedback especializado
```

### ✅ CASO 4: Progresión natural (Cambio CORRECTO)
```
Apply: "Ya terminaste, ¿qué sigue?"
User: "Revisa esto" [imagen de canvas]
→ Cambiar a REVIEW ✓
→ Cambio explícito de intención
```

---

## 🎯 ANÁLISIS DE INTENCIÓN

### Cuando Apply pregunta sobre revisión:
- **"¿Deseas revisar algo?"**
- **"¿Quieres que evalúe tu trabajo?"**
- **"¿Necesitas feedback?"**

### Y usuario envía framework completo:
La intención REAL es:
1. ✅ **"Sí, REVISA ESTO"** → Cambio a Review (natural)
2. ❌ **"Sí, sigamos aplicando"** → Mantener Apply (no tiene sentido)

### Diferencia clave:
```
Proporcionar datos solicitados:
  Apply: "¿Cuál es tu propuesta de valor?"
  User: [texto/imagen descriptiva]
  → Mantener APPLY (continuar aplicación)

Compartir trabajo para evaluación:
  Apply: "¿Quieres que revise algo?"
  User: [imagen de framework completo]
  → Cambiar a REVIEW (nueva fase)
```

---

## 💡 SOLUCIÓN PROPUESTA

### Refinar MULTIMEDIA RULE 3 con una EXCEPCIÓN:

```markdown
### MULTIMEDIA RULE 3: Multimedia in mid-conversation → CONTINUITY RULES FIRST

**IF** user is in active conversation (RECENT CONVERSATION HISTORY shows recent agent)
AND sends image/video/document:
→ **APPLY CONTINUITY RULES FIRST** (Rules 1-3 above)
→ User is likely providing requested information visually

**⚠️ EXCEPTION - Natural Progression to Review:**

**IF** assistant asked about review/feedback/evaluation
AND user sends completed framework (image/document):
→ **ROUTE TO REVIEW** (natural stage progression, not simple continuity)
→ User is initiating review phase, not just answering

**How to detect:**
- Assistant's question contains: "review", "revisar", "feedback", "evaluar", "¿qué te parece?"
- AND MEDIA TYPE is 'image' or 'document'
- AND MESSAGE describes completed or partial framework/canvas/analysis
- → This is STAGE PROGRESSION, not data provision

**Examples:**

✅ **EXCEPTION APPLIES (Route to Review):**
```
Last agent: Apply
Assistant: "¿Deseas revisar algo o actualizar?"
User sends: MEDIA TYPE: image, MESSAGE: "Image showing completed Business Model Canvas with all 9 blocks filled..."
→ **REVIEW** (user initiating review phase - natural progression)
```

```
Last agent: Apply
Assistant: "Do you want me to evaluate your work?"
User sends: MEDIA TYPE: document, MESSAGE: "PDF with completed SWOT analysis..."
→ **REVIEW** (user requesting evaluation - stage change)
```

❌ **EXCEPTION DOES NOT APPLY (Maintain continuity):**
```
Last agent: Apply
Assistant: "What are your customer segments?"
User sends: MEDIA TYPE: image, MESSAGE: "Image showing list of 5 customer types..."
→ **APPLY** (user providing requested data - continuity)
```

```
Last agent: Apply
Assistant: "Can you describe your current process?"
User sends: MEDIA TYPE: image, MESSAGE: "Diagram showing workflow steps..."
→ **APPLY** (user providing context - continuity)
```
```

---

## 🔧 IMPLEMENTACIÓN

### Cambios necesarios en TextClassifier:

**Ubicación:** `systemPromptTemplate` → MULTIMEDIA RULE 3

**Agregar después del ejemplo existente:**
```markdown
**⚠️ EXCEPTION - Natural Progression to Review:**

**IF** assistant asked about review/feedback/evaluation AND user sends completed framework:
→ **ROUTE TO REVIEW** (natural stage progression)

**Detection criteria:**
1. Recent assistant message contains review keywords:
   - Spanish: "revisar", "evaluar", "feedback", "¿qué te parece?", "¿está bien?"
   - English: "review", "evaluate", "feedback", "check", "assess"
2. MEDIA TYPE is 'image' or 'document'
3. MESSAGE describes completed/partial framework, canvas, matrix, or analysis

**Examples:**
- Apply asks: "¿Deseas revisar algo?" + User sends completed canvas image → **REVIEW**
- Apply asks: "Want me to check your work?" + User sends framework PDF → **REVIEW**
- Apply asks: "What's next?" + User sends completed analysis → **REVIEW**
```

---

## ✅ BENEFICIOS DE LA SOLUCIÓN

1. **Especialización:** Review recibe frameworks para evaluación (su especialidad)
2. **Continuidad inteligente:** Mantiene continuidad cuando es apropiado
3. **Progresión natural:** Permite transición Apply → Review cuando el usuario lo indica
4. **Mejor UX:** Usuario no necesita decir explícitamente "cambia a review"
5. **Intención clara:** Distingue entre "proporcionar datos" vs "solicitar evaluación"

---

## 📋 RESUMEN

| Situación | Regla Actual | Regla Propuesta | Mejor? |
|-----------|--------------|-----------------|--------|
| Apply pide datos + Usuario envía imagen | Mantener Apply | Mantener Apply | ✓ Igual |
| Apply pide contexto + Usuario envía diagrama | Mantener Apply | Mantener Apply | ✓ Igual |
| **Apply pregunta sobre revisión + Usuario envía framework** | **Mantener Apply** | **Cambiar a Review** | **✓ Mejor** |
| Usuario envía framework sin contexto previo | Cambiar a Review | Cambiar a Review | ✓ Igual |

**Conclusión:** La excepción mejora el caso específico sin afectar negativamente otros casos.

---

## 🔄 ACTUALIZACIÓN: CICLOS ITERATIVOS (Review ↔ Apply)

### Observación del Usuario:
"El usuario puede enviar imagen de canvas completo → va a Review → Review da recomendaciones → Usuario quiere ACTUALIZAR el canvas con las recomendaciones"

### Flujo Iterativo Completo:

```
1. Usuario envía canvas completo (primera vez)
   → REVIEW (evaluación inicial) ✓

2. Review: "Tu canvas está bien, pero podrías mejorar X, Y, Z"
   
3. Usuario: "Ayúdame a actualizar mi canvas con esas recomendaciones"
   → ¿REVIEW o APPLY?
   → Debería: APPLY ✓ (ayudar a implementar cambios)

4. Apply ayuda a actualizar los bloques X, Y, Z

5. Usuario: [envía imagen de canvas ACTUALIZADO]
   → ¿APPLY o REVIEW?
   → Debería: REVIEW ✓ (evaluar nueva versión)

6. [Ciclo se repite hasta satisfacción]

7. Usuario: "¿Qué hago ahora?"
   → OPTIMIZE ✓ (próximos pasos)
```

---

## ⚠️ NUEVOS CONFLICTOS IDENTIFICADOS

### CONFLICTO #2: Review → Apply (solicitud de ayuda)

```
Review: "Podrías mejorar tu propuesta de valor y tus canales"
Usuario: "Ayúdame a actualizar esas secciones"

Regla actual: CONTINUITY RULE 1
  - Usuario está respondiendo (implícitamente acepta hacer cambios)
  - → Mantener REVIEW ❌

Debería ser: RULE 3 - Explicit Intent Change
  - "Ayúdame a actualizar" = solicitud de ayuda para APLICAR
  - → Cambiar a APPLY ✓
```

**Problema:** CONTINUITY RULE 1 dice "OVERRIDE ALL OTHER RULES", pero RULE 3 dice "Explicit intent change" debería permitir cambio.

### CONFLICTO #3: Apply → Review (re-evaluación)

```
Apply: "Ya actualizamos los bloques de propuesta de valor y canales"
Usuario: "Revísalo ahora" + [envía canvas actualizado]

Regla actual: CONTINUITY RULE 1
  - Usuario respondiendo solicitud implícita
  - → Mantener APPLY ❌

Debería ser: Cambio explícito + Multimedia
  - "Revísalo" = solicitud explícita de evaluación
  - + Framework completo = MULTIMEDIA RULE 1
  - → Cambiar a REVIEW ✓
```

---

## 💡 SOLUCIÓN EXTENDIDA

### Refinar CONTINUITY RULE 1 con detección de cambio de fase:

```markdown
### RULE 1: ANSWERING ASSISTANT'S QUESTIONS = SAME AGENT (MANDATORY)

**IF** the most recent assistant message contains questions AND the current user message is answering those questions:
→ **MUST** route to the SAME agent that asked the questions

**⚠️ EXCEPTION - Explicit Phase Change in Response:**

**IF** user's answer contains EXPLICIT INTENT to change workflow phase:
→ **ALLOW AGENT SWITCH** (phase change overrides continuity)

**Phase change keywords:**

**Review → Apply** (request help to implement):
- Spanish: "ayúdame a actualizar", "cómo aplico", "guíame para hacer", "paso a paso", "implementar"
- English: "help me update", "how do I apply", "guide me to", "step by step", "implement"

**Apply → Review** (request evaluation):
- Spanish: "revísalo", "evalúa esto", "¿qué te parece?", "dame feedback"
- English: "review this", "evaluate", "what do you think", "give me feedback"

**Any → Optimize** (request next steps):
- Spanish: "¿qué sigue?", "próximos pasos", "¿ahora qué?"
- English: "what's next?", "next steps", "now what?"

**Examples:**

✅ **EXCEPTION APPLIES (Allow switch despite continuity):**
```
Last agent: Review
Review: "Your canvas needs improvements. Want to work on it?"
User: "Yes, help me update those sections step by step"
→ **APPLY** (explicit request for guided implementation - phase change)
```

```
Last agent: Apply
Apply: "We've updated the value proposition. Ready to continue?"
User: "Review it now please" + [sends updated canvas image]
→ **REVIEW** (explicit request for evaluation - phase change)
```

❌ **EXCEPTION DOES NOT APPLY (Maintain continuity):**
```
Last agent: Apply
Apply: "What customer segments do you have?"
User: "SMEs and startups"
→ **APPLY** (simple data provision - no phase change)
```
```

---

## 🎯 CASOS DE USO EXTENDIDOS

### Tabla de Transiciones:

| Desde | Hacia | Trigger | Permitir? | Razón |
|-------|-------|---------|-----------|-------|
| **EXPLORE** | LEARN | "Explícame el BMC" | ✅ | Cambio explícito |
| **LEARN** | APPLY | "Ayúdame a crearlo" | ✅ | Cambio explícito |
| **APPLY** | REVIEW | "Revísalo" + [imagen] | ✅ | Cambio explícito + multimedia |
| **REVIEW** | APPLY | "Ayúdame a actualizar" | ✅ | **NUEVO: Cambio de fase** |
| **APPLY** | REVIEW | [envía canvas actualizado] | ✅ | **NUEVO: Re-evaluación** |
| **REVIEW** | REVIEW | [envía nueva versión] | ✅ | Continuidad correcta |
| **APPLY** | APPLY | "Mis segmentos son..." | ✅ | Continuidad correcta |
| **REVIEW** | OPTIMIZE | "¿Qué sigue?" | ✅ | Cambio explícito |

---

## 📋 RESUMEN DE SOLUCIÓN COMPLETA

### Cambios necesarios en TextClassifier:

1. **MULTIMEDIA RULE 3 - Agregar excepción:**
   - Detectar: Pregunta sobre revisión/evaluación + Framework completo
   - Acción: Apply → Review (progresión natural)

2. **CONTINUITY RULE 1 - Agregar excepción:**
   - Detectar: Palabras clave de cambio de fase en respuesta
   - Acción: Permitir cambio de agente (fase > continuidad)
   - Keywords:
     - Review → Apply: "ayúdame a actualizar", "cómo aplico", "paso a paso"
     - Apply → Review: "revísalo", "evalúa", "dame feedback"
     - Any → Optimize: "¿qué sigue?", "próximos pasos"

3. **Prioridad refinada:**
   ```
   1. Cambio de fase explícito (palabras clave) → PERMITIR CAMBIO
   2. Multimedia + Framework completo en pregunta de revisión → PERMITIR CAMBIO
   3. Continuidad normal → MANTENER AGENTE
   ```

### Ciclo de vida completo:
```
EXPLORE → LEARN → APPLY ⟷ REVIEW → OPTIMIZE
                    ↑       ↓
                    └───────┘
                 (ciclo iterativo)
```

---

## ✅ BENEFICIOS DE LA SOLUCIÓN EXTENDIDA

1. ✅ Soporta ciclo iterativo natural (Apply ⟷ Review)
2. ✅ Permite "Review → Apply" para implementar recomendaciones
3. ✅ Permite "Apply → Review" para re-evaluar cambios
4. ✅ Mantiene continuidad cuando es apropiado (provisión de datos)
5. ✅ Detecta cambio de fase incluso dentro de respuestas
6. ✅ Usuario no necesita decir explícitamente "cambia de agente"
7. ✅ Flujo natural de trabajo: evaluar → mejorar → re-evaluar → repetir
8. ✅ Transición final a Optimize cuando usuario pregunta "¿qué sigue?"

