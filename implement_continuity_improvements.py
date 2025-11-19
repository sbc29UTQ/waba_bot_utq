#!/usr/bin/env python3
"""
Implement continuity improvements to TextClassifier
Based on MEJORAS_CONTINUIDAD_TEXTCLASSIFIER.md analysis
"""

import json

def implement_improvements():
    with open('utq_bot.json', 'r', encoding='utf-8') as f:
        workflow = json.load(f)

    print("=" * 70)
    print("IMPLEMENTING CONTINUITY IMPROVEMENTS")
    print("=" * 70)

    # Find TextClassifier node
    for node in workflow['nodes']:
        if node.get('name') == 'Clasificacion de intencion':
            system_prompt = node['parameters']['options']['systemPromptTemplate']

            # MEJORA 3: Insert "Next Steps" rule BEFORE CONTINUITY RULES
            print("\n✓ MEJORA 3: Adding Next Steps Detection rule...")

            next_steps_rule = """

## 🎯 NEXT STEPS DETECTION (VERY HIGH PRIORITY)

**This rule applies BEFORE continuity rules for strategic progression**

### RULE: Next Steps Request = OPTIMIZE

**IF** user message contains next steps keywords:
→ **ROUTE TO OPTIMIZE** (regardless of current agent)

**Keywords (Spanish):**
- "qué sigue"
- "próximos pasos"
- "ahora qué"
- "qué debo hacer ahora"
- "qué framework uso ahora"
- "qué herramienta sigue"
- "cómo continúo"
- "qué debo hacer después"

**Keywords (English):**
- "what's next"
- "next steps"
- "now what"
- "what should I do now"
- "what framework now"
- "what tool next"
- "how do I continue"
- "what should I do next"

**Exception:** IF current agent is already OPTIMIZE → maintain OPTIMIZE

**Rationale:**
- "Next steps" is OPTIMIZE's domain (strategic planning and future direction)
- User signaling phase completion and seeking future guidance
- Other agents (Apply, Review, Explore, Learn) should not handle strategic next steps
- This enables natural progression to the final workflow stage

**Examples:**

✅ **ROUTE TO OPTIMIZE:**
```
Last agent: Apply
User: "Ya terminé el canvas, ¿qué sigue?"
→ **OPTIMIZE** (strategic next steps request)
```

```
Last agent: Review
User: "Ok, entendí el feedback. ¿Qué debo hacer ahora?"
→ **OPTIMIZE** (seeking strategic direction)
```

```
Last agent: Learn
User: "Ya entendí el BMC. ¿Qué framework uso ahora?"
→ **OPTIMIZE** (seeking framework recommendations)
```

❌ **DO NOT ROUTE TO OPTIMIZE (different intent):**
```
User: "¿Cuál es el siguiente bloque?" (within Apply process)
→ Context: asking about next BLOCK, not next PHASE
→ Maintain APPLY
```

---

"""

            # Find where to insert (before CONTINUITY RULES)
            lines = system_prompt.split('\n')
            continuity_index = None

            for i, line in enumerate(lines):
                if 'CRITICAL CONTINUITY RULES' in line:
                    continuity_index = i
                    break

            if continuity_index:
                # Insert the new rule before CONTINUITY RULES
                lines.insert(continuity_index, next_steps_rule)
                print(f"  → Inserted at line {continuity_index}")

            # MEJORA 1: Add exceptions to CONTINUITY RULE 1
            print("\n✓ MEJORA 1: Adding exceptions to CONTINUITY RULE 1...")

            continuity_exception = """

**⚠️ EXCEPTION - Explicit Phase Change Keywords:**

**IF** user's answer contains phase change keywords:
→ **ALLOW AGENT SWITCH** (phase change overrides simple continuity)

**Phase change keywords detected in user response:**

**Review → Apply** (request help to implement):
- Spanish: "ayúdame a actualizar", "ayúdame a implementar", "guíame para hacer",
          "cómo aplico", "paso a paso para", "ayúdame a mejorar [específico]",
          "implementar", "actualizar el canvas"
- English: "help me update", "help me implement", "guide me to do",
          "how do I apply", "step by step to", "help me improve [specific]",
          "implement", "update the canvas"

**Apply → Review** (request evaluation):
- Spanish: "revísalo", "evalúa esto", "¿qué te parece?", "dame feedback",
          "¿está bien?", "analízalo", "dame tu opinión", "¿cómo quedó?"
- English: "review this", "evaluate this", "what do you think", "give me feedback",
          "is this good", "analyze this", "give me your opinion", "how does it look"

**Any → Optimize** (request next steps - covered by Next Steps rule above):
- Spanish: "¿qué sigue?", "próximos pasos", "¿ahora qué?"
- English: "what's next?", "next steps", "now what?"

**Priority:** Phase change keywords > Simple continuity

**Examples:**

✅ **EXCEPTION APPLIES (Allow switch despite continuity):**
```
Last agent: Review
Review: "Your canvas needs improvements. Want to work on them?"
User: "Yes, help me update those sections step by step"
→ **APPLY** (explicit request for guided implementation - phase change keyword detected)
```

```
Last agent: Apply
Apply: "We've updated the value proposition block. Ready to continue?"
User: "Review it now please, I want feedback"
→ **REVIEW** (explicit request for evaluation - phase change keyword detected)
```

❌ **EXCEPTION DOES NOT APPLY (Maintain continuity):**
```
Last agent: Apply
Apply: "What customer segments do you have?"
User: "SMEs and startups in tech sector"
→ **APPLY** (simple data provision - no phase change keywords)
```

```
Last agent: Review
Review: "Do you want me to explain this issue further?"
User: "Yes, explain more about the channels block"
→ **REVIEW** (continuation request - no phase change)
```
"""

            # Find RULE 1 section and add exception after it
            rule1_index = None
            for i, line in enumerate(lines):
                if '### RULE 1: ANSWERING ASSISTANT' in line:
                    rule1_index = i
                    # Find end of RULE 1 (before ### RULE 2 or before next ##)
                    for j in range(i+1, len(lines)):
                        if lines[j].strip().startswith('### RULE 2') or \
                           (lines[j].strip().startswith('##') and not lines[j].strip().startswith('###')):
                            # Insert before RULE 2 or next major section
                            lines.insert(j, continuity_exception)
                            print(f"  → Inserted exception at line {j}")
                            break
                    break

            # MEJORA 2: Add exceptions to MULTIMEDIA RULE 3
            print("\n✓ MEJORA 2: Adding exceptions to MULTIMEDIA RULE 3...")

            multimedia_exception = """

**⚠️ EXCEPTION 1 - Framework Completion (Natural Progression):**

**IF** assistant asked about completion/review/evaluation AND user sends framework:
→ **ROUTE TO REVIEW** (natural progression to evaluation phase, not simple data provision)

**Detection criteria:**
- Assistant message contains completion keywords: "completaste", "terminaste", "listo",
  "finished", "completed", "done"
- OR assistant message contains review keywords: "revisar", "evaluar", "ver",
  "review", "evaluate", "check", "assess"
- AND user sends: image/document of framework/canvas/matrix/analysis

**Why this is phase change, not continuity:**
- User completing framework = ready for professional evaluation
- Review is specialized in detailed feedback
- Natural workflow progression: Create (Apply) → Evaluate (Review)

**Examples:**

✅ **EXCEPTION APPLIES (Route to Review):**
```
Last agent: Apply
Apply: "¿Ya completaste todos los bloques del canvas?"
User: [sends image of completed Business Model Canvas]
→ **REVIEW** (framework complete - natural progression to evaluation)
```

```
Last agent: Apply
Apply: "Ready to review your work?"
User: "Yes" + [sends canvas image]
→ **REVIEW** (user ready for evaluation - phase change)
```

**⚠️ EXCEPTION 2 - Requested Information (Maintain Continuity):**

**IF** assistant specifically asked to SEE/SHOW/SEND something:
→ **MAINTAIN AGENT** (user providing specifically requested information)

**Detection criteria:**
- Assistant message contains request keywords: "muéstrame", "envía", "comparte",
  "show me", "send", "share", "can you show"
- User responds with multimedia (image/video/document)
→ This is data provision, not evaluation request

**Examples:**

✅ **EXCEPTION APPLIES (Maintain agent):**
```
Last agent: Explore
Explore: "¿Qué herramientas has usado? Muéstramelas si las tienes"
User: [sends image of old canvas]
→ **EXPLORE** (providing requested context - not seeking evaluation)
```

```
Last agent: Apply
Apply: "Show me your current customer segments"
User: [sends image of segment list]
→ **APPLY** (providing requested data - continuity correct)
```
"""

            # Find MULTIMEDIA RULE 3 and add exceptions
            multimedia_rule3_index = None
            for i, line in enumerate(lines):
                if 'MULTIMEDIA RULE 3' in line:
                    multimedia_rule3_index = i
                    # Find end of RULE 3 (before ### MULTIMEDIA RULE 4 or before next ##)
                    for j in range(i+1, len(lines)):
                        if '### MULTIMEDIA RULE 4' in lines[j] or \
                           (lines[j].strip().startswith('---') and j > i + 10):
                            # Insert before RULE 4 or separator
                            lines.insert(j, multimedia_exception)
                            print(f"  → Inserted exceptions at line {j}")
                            break
                    break

            # Reconstruct the system prompt
            new_system_prompt = '\n'.join(lines)

            # Update the node
            node['parameters']['options']['systemPromptTemplate'] = new_system_prompt

            print("\n✅ All improvements implemented successfully!")
            print("\nSummary:")
            print("  ✓ MEJORA 3: Next Steps Detection rule added (VERY HIGH PRIORITY)")
            print("  ✓ MEJORA 1: Phase change exceptions added to CONTINUITY RULE 1")
            print("  ✓ MEJORA 2: Context exceptions added to MULTIMEDIA RULE 3")

            break

    # Save updated workflow
    with open('utq_bot.json', 'w', encoding='utf-8') as f:
        json.dump(workflow, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("CHANGES SAVED TO utq_bot.json")
    print("=" * 70)

    print("\n📋 NEW RULE HIERARCHY:")
    print("""
1. 🎯 NEXT STEPS DETECTION (Very High Priority)
   - "¿Qué sigue?" → OPTIMIZE

2. 🎬 MULTIMEDIA RULES (High Priority)
   - With exceptions for context detection

3. ⚠️ CONTINUITY RULES (Highest Priority - but with exceptions)
   - With exceptions for phase change keywords

4. 📊 CLASSIFICATION CATEGORIES (Normal Priority)
""")

if __name__ == '__main__':
    implement_improvements()
