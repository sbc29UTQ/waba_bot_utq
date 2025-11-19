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
