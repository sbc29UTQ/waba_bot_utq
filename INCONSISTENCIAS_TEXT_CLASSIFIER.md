# 🔍 Análisis de Inconsistencias: Nodo "Clasificacion de intencion"

## ❌ INCONSISTENCIA PRINCIPAL

El nodo **"Clasificacion de intencion"** (TextClassifier) hace referencia al campo `media_type`, pero este campo **NO EXISTE** en el nodo "Extraer datos del user".

---

## 📋 Campos Disponibles en "Extraer datos del user"

| Campo | Valor | Fuente |
|-------|-------|--------|
| `id_session` | `$('WhatsApp Trigger').first().json.messages[0].id` | WhatsApp Trigger |
| `phone_number` | `$('WhatsApp Trigger').first().json.messages[0].from` | WhatsApp Trigger |
| `user_name` | `$('WhatsApp Trigger').first().json.contacts[0].profile.name` | WhatsApp Trigger |
| `type_message` | `$('WhatsApp Trigger').first().json.messages[0].type` | WhatsApp Trigger |
| `message` | `$json.text` | Edit Fields1 |
| `attachments` | `$('WhatsApp Trigger').first().json.messages[0]` | WhatsApp Trigger |

### ✅ Campo Disponible para Tipo de Mensaje:
- **`type_message`** contiene: `text`, `image`, `video`, `document`

### ❌ Campo NO Disponible:
- **`media_type`** - NO EXISTE

---

## 🚨 Referencias Incorrectas Encontradas

### 1. En `inputText`:
```javascript
MEDIA TYPE: {{$('Extraer datos del user').first().json.media_type || 'text'}}
//                                                      ^^^^^^^^^^
//                                                      ❌ NO EXISTE
```

**Debería ser:**
```javascript
MEDIA TYPE: {{$('Extraer datos del user').first().json.type_message || 'text'}}
//                                                      ^^^^^^^^^^^^^
//                                                      ✅ EXISTE
```

### 2. En `systemPromptTemplate`:

El prompt contiene una sección completa sobre reglas multimedia:

```
## 🎬 MULTIMEDIA MESSAGE CLASSIFICATION RULES (HIGH PRIORITY)

The MEDIA TYPE field indicates what the user sent:
- **text**: User typed this message directly
- **image**: User sent an image (MESSAGE is AI-generated description of the image)
- **video**: User sent a video (MESSAGE is AI-generated description of the video)
- **document**: User sent a PDF/document (MESSAGE is AI-generated summary)
```

Esta sección hace referencia a "MEDIA TYPE field" que proviene del `inputText`, el cual está usando `media_type` (campo inexistente).

---

## 📊 Impacto de las Inconsistencias

### ⚠️ Comportamiento Actual:

1. **inputText siempre muestra "text"**:
   - `{{$('Extraer datos del user').first().json.media_type || 'text'}}`
   - Como `media_type` es `undefined`, siempre usa el fallback `'text'`
   - **Resultado**: El clasificador NUNCA detecta imágenes, videos o PDFs

2. **Reglas multimedia no se aplican**:
   - Las 4 reglas multimedia en el prompt dependen de MEDIA TYPE
   - Como siempre es 'text', estas reglas NUNCA se activan
   - **Resultado**: Imágenes de frameworks NO se clasifican como REVIEW automáticamente

3. **Pérdida de contexto multimedia**:
   - El agente no sabe si el mensaje viene de imagen/video/documento
   - No puede aplicar lógica especial para multimedia
   - **Resultado**: Experiencia degradada para mensajes multimedia

---

## ✅ Solución Recomendada

### Opción 1: Usar campo existente (RÁPIDA Y SIMPLE)

Cambiar `media_type` → `type_message` en ambos lugares:

**1. En `inputText`:**
```javascript
// ANTES (❌):
MEDIA TYPE: {{$('Extraer datos del user').first().json.media_type || 'text'}}

// DESPUÉS (✅):
MEDIA TYPE: {{$('Extraer datos del user').first().json.type_message || 'text'}}
```

**2. No requiere cambios en `systemPromptTemplate`** porque el prompt solo LEE el valor, no lo referencia directamente.

### Opción 2: Agregar campo `media_type` (MÁS SEMÁNTICA)

Si prefieres mantener el nombre `media_type` por claridad semántica, agregar el campo en "Extraer datos del user":

```json
{
  "id": "nuevo-campo-media-type",
  "name": "media_type",
  "value": "={{ $('WhatsApp Trigger').first().json.messages[0].type }}",
  "type": "string"
}
```

Pero esto es redundante con `type_message` que ya existe.

---

## 🎯 Valores Esperados

Los valores que retorna WhatsApp Trigger y que están disponibles en ambos campos son:

| Tipo WhatsApp | Valor en JSON | Descripción |
|---------------|---------------|-------------|
| Texto | `text` | Mensaje de texto plano |
| Imagen | `image` | Imagen (con o sin caption) |
| Video | `video` | Video |
| Documento/PDF | `document` | Archivo PDF u otro documento |

**Nota**: El Switch node ya clasifica correctamente estos valores, por lo que usar `type_message` es consistente con toda la arquitectura.

---

## ⚡ Implementación Recomendada

**Usar Opción 1** (cambiar referencia a `type_message`):

1. ✅ Usa campo que YA EXISTE
2. ✅ No requiere modificar "Extraer datos del user"
3. ✅ Consistente con estructura WhatsApp
4. ✅ Los valores son idénticos (text, image, video, document)
5. ✅ Cambio mínimo de código

---

## 📝 Resumen

| Aspecto | Estado Actual | Estado Correcto |
|---------|---------------|-----------------|
| **Campo referenciado** | `media_type` ❌ | `type_message` ✅ |
| **Campo existe** | NO ❌ | SÍ ✅ |
| **Reglas multimedia funcionan** | NO ❌ | SÍ ✅ |
| **Clasificación multimedia** | Deshabilitada ❌ | Habilitada ✅ |
| **Experiencia usuario** | Degradada ❌ | Completa ✅ |

---

## 🔧 Archivos Afectados

- **utq_bot.json**: Nodo "Clasificacion de intencion"
  - Parámetro: `inputText`
  - Línea aproximada: Buscar `media_type`
