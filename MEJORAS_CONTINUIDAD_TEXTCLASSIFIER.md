# 🔍 Análisis de Continuidad: Mejoras para TextClassifier y Agentes

## 📊 RESUMEN EJECUTIVO

Se analizaron TODOS los casos posibles de continuidad en la conversación para identificar mejoras que mantengan la coherencia del flujo mientras permiten transiciones naturales entre agentes.

### Casos Analizados:
1. **Usuario envía framework (imagen/video/PDF)** - 4 subcasos
2. **Usuario pide recomendaciones/próximos pasos** - 4 subcasos
3. **Patrones de transición entre agentes**
4. **Palabras clave de cambio de fase**

---

## 🎯 CASO 1: Usuario Envía Framework con Datos de su Negocio

### Subcaso 1.1: Primera vez (sin agente previo)
```
Usuario: [envía imagen de Business Model Canvas]
→ REVIEW ✅ (correcto)

Continuación:
Review: "Veo tu BMC. Te doy feedback: X es fuerte, Y necesita mejora..."
Review: "¿Quieres profundizar en algo?"

Usuario puede decir:
a) "Explícame más sobre Y" → REVIEW ✅ (continuidad correcta)
b) "Ayúdame a mejorar Y" → ¿REVIEW o APPLY? 🤔
c) [envía versión actualizada] → REVIEW ✅ (re-evaluación)
d) "¿Qué sigue?" → ¿REVIEW o OPTIMIZE? 🤔
```

**Evaluación:** Funciona bien ✅

---

### Subcaso 1.2: Usuario con Apply activo
```
Apply: "¿Ya completaste todos los bloques?"
Usuario: "Sí" [envía canvas completo]

ACTUAL: → APPLY ❌ (por continuidad estricta)
IDEAL: → REVIEW ✅ (especializado en evaluación)

Problema:
- Apply NO especializado en dar feedback detallado
- Usuario completa framework = quiere evaluación profesional

Continuación IDEAL:
Review: "Tu BMC tiene fortalezas en X, Y. Áreas de mejora: Z, W..."
Usuario: "¿Cómo mejoro Z?" → ¿REVIEW o APPLY?
```

**Evaluación:** Necesita mejora ❌

---

### Subcaso 1.3: Usuario con Explore activo
```
Explore: "¿Qué herramientas has usado?"
Usuario: [envía canvas que hizo antes]

ACTUAL: → EXPLORE ❌ (continuidad)
ALTERNATIVA: → REVIEW ✅

Análisis:
- Si Explore PIDIÓ ver herramientas → EXPLORE ✅ (contexto)
- Si usuario envía sin solicitud → REVIEW ✅ (evaluación)

Depende del CONTEXTO de la pregunta del agente
```

**Evaluación:** Depende del contexto 🤔

---

### Subcaso 1.4: Usuario con Review activo
```
Review: "Mejora X, Y. ¿Trabajas en ello?"
Usuario: [envía canvas actualizado]

ACTUAL: → REVIEW ✅ (correcto)

Continuación:
Review: "Mejoraste X significativamente. Y ahora está más claro..."
Review: "¿Quieres seguir refinando o pasamos a siguiente fase?"

Usuario:
a) "Ayúdame a mejorar Z" → ¿REVIEW o APPLY? 🤔
b) "¿Qué sigue?" → ¿REVIEW o OPTIMIZE? 🤔
c) [envía otra versión] → REVIEW ✅ (ciclo continúa)
```

**Evaluación:** Funciona bien ✅

---

## 🎯 CASO 2: Usuario Pide Recomendaciones/Próximos Pasos

### Subcaso 2.1: "¿Qué sigue?" después de completar framework
```
Apply: "Ya completamos tu Business Model Canvas"
Usuario: "¿Qué sigue?" / "¿Qué debo hacer ahora?"

ACTUAL: Ambiguo 🤔 (podría mantener APPLY o cambiar)
IDEAL: → OPTIMIZE ✅

Razones:
- Apply cumplió su función (crear/aplicar)
- "¿Qué sigue?" = solicitud de siguiente fase estratégica
- OPTIMIZE especializado en orientación futura

Continuación:
Optimize: "Excelente, completaste BMC. Próximos pasos:"
Optimize: "1) Valida con clientes, 2) Complementa con VPC, 3) Define OKRs"
```

**Evaluación:** Necesita mejora ❌

---

### Subcaso 2.2: "¿Qué framework uso ahora?"
```
Review: "Tu canvas está bien, áreas de mejora: X, Y"
Usuario: "¿Qué pasos me recomiendas?" / "¿Qué framework uso ahora?"

ACTUAL: Ambiguo 🤔 (continuidad vs cambio)
IDEAL: → OPTIMIZE ✅

Razones:
- Usuario cambió de "evaluar" a "planificar siguiente fase"
- "Próximos pasos/frameworks" = dominio de OPTIMIZE
- Review ya completó su evaluación

Continuación:
Optimize: "Basado en tu BMC, recomiendo:"
Optimize: "1) Value Proposition Canvas para profundizar propuesta"
Optimize: "2) Customer Journey para entender experiencia"
```

**Evaluación:** Necesita mejora ❌

---

### Subcaso 2.3: Solicitud de framework adicional
```
Apply: "Ya terminamos BMC"
Usuario: "¿Qué otros frameworks puedo usar?"

ACTUAL: Mantiene agente actual (APPLY)
IDEAL: → OPTIMIZE ✅ (si terminó framework)
      → EXPLORE ✅ (si está diagnosticando)

Razones:
- Solicitud de herramientas complementarias
- OPTIMIZE mejor para recomendar frameworks estratégicos
- EXPLORE mejor si aún está diagnosticando problemas

Continuación:
Optimize: "Complementa BMC con:"
Optimize: "- Value Proposition Canvas (propuesta valor)"
Optimize: "- SWOT (análisis situación)"
Optimize: "- Customer Journey (experiencia cliente)"
```

**Evaluación:** Necesita mejora ❌

---

### Subcaso 2.4: Solicitud de conclusiones
```
Review: [dio feedback sobre canvas]
Usuario: "Dame un resumen" / "¿Cuáles son las conclusiones?"

ACTUAL: Mantiene agente actual (REVIEW) ✅
¿Es correcto? Depende...

Review puede resumir: ✅
Pero luego... ¿qué?

Usuario: "Ok, ¿y ahora qué hago?"
→ Aquí DEBE pasar a OPTIMIZE
```

**Evaluación:** Funciona bien, pero necesita transición ⚠️

---

## 🔄 PATRONES DE TRANSICIÓN IDENTIFICADOS

### Flujo Lineal (Usuario nuevo):
```
EXPLORE → LEARN → APPLY → REVIEW → OPTIMIZE
```

### Ciclo Iterativo (Mejora continua):
```
APPLY ⟷ REVIEW
(crear/actualizar → evaluar → mejorar → re-evaluar)
```

### Transiciones Especiales:
```
Review → Apply: "Ayúdame a implementar/actualizar"
Apply → Review: "Revísalo" / [envía framework]
Cualquiera → Optimize: "¿Qué sigue?" / "Próximos pasos"
Review → Optimize: Después de iteraciones satisfactorias
```

---

## 🔑 PALABRAS CLAVE DE CAMBIO DE FASE

### → EXPLORE (Diagnóstico)
- "No sé qué hacer"
- "Tengo problemas con..."
- "¿Qué herramienta necesito?"

### → LEARN (Aprendizaje)
- "¿Qué es [framework]?"
- "Explícame cómo funciona"
- "Quiero entender"

### → APPLY (Aplicación/Implementación) ⭐
- "Ayúdame a crear/hacer/completar"
- "Guíame paso a paso"
- "Cómo lleno [bloque]"
- **"Ayúdame a actualizar/implementar/mejorar"** ← Desde Review

### → REVIEW (Evaluación) ⭐
- **"Revísalo" / "Evalúa esto"**
- "¿Qué te parece?"
- "Dame feedback"
- **[Envía framework completo]** ← Visual

### → OPTIMIZE (Siguiente Fase) ⭐
- **"¿Qué sigue?" / "Próximos pasos"**
- "¿Qué framework uso ahora?"
- "Dame conclusiones finales"
- "¿Cómo escalo/optimizo?"

⭐ = Más importantes para detectar cambio de fase

---

## ❌ PROBLEMAS IDENTIFICADOS

### Problema 1: Framework completo + Apply activo
**Situación:** Apply ayuda → Usuario completa → Envía imagen
**Actual:** Mantiene APPLY (continuidad)
**Problema:** Apply NO especializado en evaluación
**Impacto:** Feedback superficial, pierde especialización de Review

### Problema 2: "¿Qué sigue?" + Apply/Review activo
**Situación:** Usuario termina fase → Pregunta próximos pasos
**Actual:** Mantiene agente actual
**Problema:** "Qué sigue" es dominio de OPTIMIZE
**Impacto:** Respuesta limitada, pierde orientación estratégica

### Problema 3: "Ayúdame a actualizar" + Review activo
**Situación:** Review da feedback → Usuario quiere implementar
**Actual:** Mantiene REVIEW
**Problema:** APPLY mejor para guiar implementación
**Impacto:** Review no guía paso a paso eficientemente

### Problema 4: Solicitud de frameworks + Cualquier agente
**Situación:** "¿Qué otros frameworks uso?"
**Actual:** Mantiene agente actual
**Problema:** Respuesta genérica sin orientación estratégica
**Impacto:** Pierde oportunidad de OPTIMIZE para recomendar

---

## ✅ MEJORAS PROPUESTAS

### MEJORA 1: Refinar CONTINUITY RULE 1

**Agregar EXCEPCIONES para cambio de fase explícito**

```markdown
### RULE 1: ANSWERING ASSISTANT'S QUESTIONS = SAME AGENT (MANDATORY)

**IF** user is answering assistant's questions:
→ **MUST** route to SAME agent

**⚠️ EXCEPTION - Explicit Phase Change Keywords:**

**IF** user's answer contains phase change keywords:
→ **ALLOW AGENT SWITCH** (phase change > continuity)

**Detection:**

Review → Apply (implementation request):
- Spanish: "ayúdame a actualizar", "ayúdame a implementar", "guíame para hacer",
          "cómo aplico", "paso a paso", "ayúdame a mejorar [específico]"
- English: "help me update", "help me implement", "guide me to do",
          "how do I apply", "step by step"

Apply → Review (evaluation request):
- Spanish: "revísalo", "evalúa esto", "¿qué te parece?", "dame feedback",
          "¿está bien?", "analízalo"
- English: "review this", "evaluate", "what do you think", "give me feedback",
          "is this good?"

Any → Optimize (next steps request):
- Spanish: "¿qué sigue?", "próximos pasos", "¿ahora qué?", "¿qué debo hacer ahora?",
          "¿qué framework uso ahora?", "¿cómo continúo?"
- English: "what's next?", "next steps", "now what?", "what should I do now?",
          "what framework should I use?", "how do I continue?"

**Priority:** Phase change keywords > Simple continuity
```

**Beneficio:** Permite transiciones naturales cuando usuario cambia de intención

---

### MEJORA 2: Refinar MULTIMEDIA RULE 3

**Agregar detección de CONTEXTO en pregunta del agente**

```markdown
### MULTIMEDIA RULE 3: Multimedia in mid-conversation → CONTINUITY RULES FIRST

**Standard behavior:**
IF user in active conversation AND sends multimedia:
→ APPLY CONTINUITY RULES FIRST

**⚠️ EXCEPTION 1 - Framework Completion:**

IF assistant asked about completion/review AND user sends framework (image/doc):
→ **ROUTE TO REVIEW** (natural progression, not data provision)

**Detection:**
- Assistant message contains: "completaste", "terminaste", "listo", "finished", "completed"
- OR assistant message contains review keywords: "revisar", "evaluar", "review", "evaluate"
- AND user sends: image/document of framework/canvas/matrix

**⚠️ EXCEPTION 2 - Requested Information:**

IF assistant specifically asked to SEE/SHOW something:
→ **MAINTAIN AGENT** (user providing requested information)

**Detection:**
- Assistant message contains: "muéstrame", "envía", "comparte", "show me", "send", "share"
- User responds with multimedia
→ This is data provision, not evaluation request
```

**Beneficio:** Distingue entre "proveer información" vs "solicitar evaluación"

---

### MEJORA 3: Nueva Regla de Alta Prioridad para "Próximos Pasos"

**Insertar ANTES de CONTINUITY RULES**

```markdown
## 🎯 NEXT STEPS DETECTION (VERY HIGH PRIORITY)

**This rule applies BEFORE continuity rules for strategic progression**

### RULE: Next Steps Request = OPTIMIZE

**IF** user message contains next steps keywords:
→ **ROUTE TO OPTIMIZE** (regardless of current agent)

**Keywords:**
- Spanish: "qué sigue", "próximos pasos", "ahora qué", "qué debo hacer ahora",
          "qué framework uso ahora", "qué herramienta sigue", "cómo continúo"
- English: "what's next", "next steps", "now what", "what should I do now",
          "what framework now", "what tool next", "how do I continue"

**Exception:** IF current agent is already OPTIMIZE → maintain

**Rationale:**
- "Next steps" is OPTIMIZE's domain (strategic planning)
- User signaling phase completion and seeking future direction
- Other agents (Apply, Review) should not handle strategic next steps
```

**Beneficio:** Captura solicitudes de orientación estratégica de forma consistente

---

### MEJORA 4: Mejorar Agentes para Facilitar Transiciones

**Actualizar systemMessage de cada agente:**

#### Apply Agent
```markdown
## When to suggest transition to REVIEW:

If user completes framework or asks about evaluation:
- Suggest: "I see you've completed the framework. Would you like me to pass
           you to the Review specialist for professional feedback?"
- User can say "yes" or "review it" → Triggers Review transition
```

#### Review Agent
```markdown
## When to suggest transition to APPLY:

If user asks how to implement improvements:
- Suggest: "Would you like step-by-step guidance to implement these changes?
           I can connect you with the Apply specialist."
- User can say "yes" or "help me update" → Triggers Apply transition

## When to suggest transition to OPTIMIZE:

After multiple review iterations when user seems satisfied:
- Suggest: "Your framework looks solid now. Want to discuss next steps and
           complementary frameworks?"
- User can say "yes" or "what's next" → Triggers Optimize transition
```

**Beneficio:** Agentes sugieren transiciones proactivamente

---

## 📋 TABLA COMPARATIVA: ANTES vs DESPUÉS

| Situación | Comportamiento Actual | Con Mejoras | Mejor? |
|-----------|----------------------|-------------|--------|
| Apply + Usuario envía framework completo | APPLY | REVIEW | ✅ Sí |
| Review + "Ayúdame a actualizar" | REVIEW | APPLY | ✅ Sí |
| Apply + "¿Qué sigue?" | APPLY | OPTIMIZE | ✅ Sí |
| Review + "Próximos pasos" | REVIEW | OPTIMIZE | ✅ Sí |
| Explore + "Muéstrame herramientas" + imagen | EXPLORE | EXPLORE | ✅ Igual (correcto) |
| Review + [envía nueva versión] | REVIEW | REVIEW | ✅ Igual (correcto) |
| Apply + "¿Cuáles son tus clientes?" + respuesta texto | APPLY | APPLY | ✅ Igual (correcto) |

---

## 🎯 PRIORIDAD REFINADA DE REGLAS

Nueva jerarquía propuesta:

```
1. NEXT STEPS DETECTION (Muy alta prioridad)
   - "¿Qué sigue?" → OPTIMIZE

2. CONTINUITY RULES (Alta prioridad)
   - EXCEPTION: Phase change keywords detected
   - Mantener agente si solo provisión de datos

3. MULTIMEDIA RULES (Alta prioridad)
   - EXCEPTION: Framework completion → REVIEW
   - EXCEPTION: Requested information → Maintain agent

4. CLASSIFICATION CATEGORIES (Prioridad normal)
```

---

## ✅ BENEFICIOS DE LAS MEJORAS

1. ✅ **Especialización preservada:** Cada agente trabaja en lo que hace mejor
2. ✅ **Transiciones naturales:** Usuario no dice "cambia a [agente]"
3. ✅ **Continuidad inteligente:** Mantiene cuando apropiado, cambia cuando necesario
4. ✅ **Ciclo iterativo:** Apply ⟷ Review funciona fluidamente
5. ✅ **Orientación estratégica:** "Qué sigue" siempre va a OPTIMIZE
6. ✅ **Contexto respetado:** Distingue "proveer datos" vs "cambiar fase"
7. ✅ **Sugerencias proactivas:** Agentes facilitan transiciones
8. ✅ **Flujo completo:** EXPLORE → LEARN → APPLY ⟷ REVIEW → OPTIMIZE

---

## 🚀 IMPLEMENTACIÓN RECOMENDADA

### Fase 1: Alta Prioridad (Implementar primero)
1. ✅ MEJORA 3: Regla de "Próximos pasos" → OPTIMIZE
2. ✅ MEJORA 1: Excepciones a CONTINUITY RULE 1 (keywords de fase)

### Fase 2: Media Prioridad
3. ✅ MEJORA 2: Excepciones a MULTIMEDIA RULE 3 (contexto)

### Fase 3: Optimización
4. ✅ MEJORA 4: Actualizar agentes con sugerencias de transición

**Razón del orden:** Mejoras 1 y 3 resuelven los problemas más críticos y frecuentes.
