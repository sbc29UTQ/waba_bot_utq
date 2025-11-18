# Instrucciones: Implementar División de Mensajes Largos

## Objetivo
Dividir automáticamente mensajes de más de 130 caracteres en 2-3 partes y enviarlos con un delay de 5 segundos entre cada uno.

## Implementación Requerida
Esta modificación debe aplicarse a los **5 agentes**: Explore, Learn, Apply, Review, Optimize

---

## Opción 1: Solución Completa Autocontenida (RECOMENDADA)

Esta opción reemplaza el nodo "Send message" con un nodo de código que:
- Divide el mensaje automáticamente
- Envía cada parte directamente a WhatsApp API
- Maneja el delay de 5 segundos entre mensajes

### Pasos para cada agente:

#### 1. Abrir el workflow en n8n

#### 2. Para cada agente (ejemplo con "Learn"):

**2.1. Agregar nuevo nodo "Code"**
   - Hacer clic en el botón "+" después del nodo "Learn"
   - Seleccionar "Code"
   - Nombrar: "Split and Send (Learn)"

**2.2. Pegar el código**
   - Copiar el contenido de `codigo_send_message_con_split.js`
   - Pegarlo en el nodo de código
   - **IMPORTANTE**: Actualizar la línea del ACCESS_TOKEN según tu método de autenticación:
     ```javascript
     // Opción A: Si usas credenciales de n8n
     const ACCESS_TOKEN = '{{ $credentials.whatsAppTriggerApi.accessToken }}';

     // Opción B: Si el token está en una variable de entorno
     const ACCESS_TOKEN = '{{ $env.WHATSAPP_ACCESS_TOKEN }}';

     // Opción C: Si tienes el token hardcodeado (NO RECOMENDADO para producción)
     const ACCESS_TOKEN = 'TU_TOKEN_AQUI';
     ```

**2.3. Conectar el flujo**
   - **Desconectar** el nodo "Learn" del nodo "Send message" existente
   - **Conectar** el nodo "Learn" al nuevo nodo "Split and Send (Learn)"
   - **Mantener** la conexión a "Call 'Actualizar_memoria_utq_bot'1"

**2.4. Eliminar nodo antiguo (opcional)**
   - Una vez validado que funciona, puedes eliminar el nodo "Send message" antiguo

#### 3. Repetir para los otros 4 agentes:
   - **Explore** → Crear "Split and Send (Explore)"
   - **Apply** → Crear "Split and Send (Apply)"
   - **Review** → Crear "Split and Send (Review)"
   - **Optimize** → Crear "Split and Send (Optimize)"

---

## Opción 2: Solución con Nodos Nativos de n8n

Esta opción usa nodos nativos de n8n para mayor visibilidad del flujo.

### Estructura requerida por agente:

```
Agente → Code (Split) → Loop Over Items → IF → Wait → Send Message
                                          ↓
                                     (sin delay)
```

### Pasos para cada agente:

#### 1. Agregar nodo "Code" (Split Message)
   - Nombre: "Split Message (Learn)"
   - Código del archivo: `codigo_division_mensajes.js`

#### 2. Agregar nodo "Loop Over Items"
   - Conectar desde "Split Message (Learn)"
   - Este nodo procesará cada parte del mensaje secuencialmente

#### 3. Agregar nodo "IF"
   - Condición: `{{ $json.needs_delay }} is equal to true`
   - True branch → Wait 5 Seconds
   - False branch → Send WhatsApp Message (sin delay)

#### 4. Agregar nodo "Wait"
   - Duración: 5 segundos
   - Conectar a → Send WhatsApp Message

#### 5. Actualizar nodo "Send message"
   - Cambiar textBody de:
     ```
     {{ $('Learn').item.json.output }}
     ```
   - A:
     ```
     {{ $json.message }}
     ```
   - Cambiar recipientPhoneNumber de:
     ```
     {{ $('Extraer datos del user').item.json.phone_number }}
     ```
   - A:
     ```
     {{ $json.phone_number }}
     ```

#### 6. Repetir para los otros 4 agentes

---

## Configuración del Código

### Parámetros ajustables:

```javascript
const MAX_LENGTH = 130;  // Máximo de caracteres por mensaje
const DELAY_MS = 5000;   // Delay entre mensajes (5 segundos = 5000ms)
```

### Lógica de división:
- El código intenta dividir en puntos naturales (saltos de línea, puntos, comas)
- Si no encuentra punto natural, divide en el último espacio
- Limita a máximo **3 partes** como solicitaste

---

## Testing

### Casos de prueba:

1. **Mensaje corto (≤130 caracteres)**
   - Debe enviar 1 solo mensaje sin delay

2. **Mensaje medio (131-260 caracteres)**
   - Debe enviar 2 mensajes con 5 segundos de delay

3. **Mensaje largo (>260 caracteres)**
   - Debe enviar máximo 3 mensajes con 5 segundos entre cada uno

### Cómo probar:
1. Activar el workflow
2. Enviar un mensaje de prueba que active un agente
3. Verificar en WhatsApp:
   - Número de mensajes recibidos
   - Delay entre mensajes (~5 segundos)
   - Que el contenido esté completo

---

## Notas Importantes

⚠️ **Opción 1 (Autocontenida)**: Requiere configurar correctamente el ACCESS_TOKEN

⚠️ **Opción 2 (Nodos nativos)**: Más visual pero requiere más nodos

✅ **Ventaja Opción 1**: Menos nodos, más fácil de mantener

✅ **Ventaja Opción 2**: Mejor visibilidad del flujo en n8n, más fácil de debuggear

---

## Solución de Problemas

### Error: "ACCESS_TOKEN is not defined"
- Verificar que la credencial de WhatsApp está configurada correctamente
- Revisar la sintaxis del ACCESS_TOKEN en el código

### Mensajes no se dividen
- Verificar que MAX_LENGTH = 130
- Revisar que el código está tomando correctamente el output del agente

### No hay delay entre mensajes
- Verificar que DELAY_MS = 5000
- Asegurar que el código `await wait(DELAY_MS)` se está ejecutando

### Mensajes duplicados
- Asegurar que eliminaste o desconectaste el nodo "Send message" antiguo

---

## Resumen de Cambios por Agente

| Agente | Nodo Original | Nuevo Nodo | Mantener Conexión |
|--------|---------------|------------|-------------------|
| Explore | Send message1 | Split and Send (Explore) | Call 'Actualizar_memoria_utq_bot' |
| Learn | Send message | Split and Send (Learn) | Call 'Actualizar_memoria_utq_bot'1 |
| Apply | Send message2 | Split and Send (Apply) | Call 'Actualizar_memoria_utq_bot'2 |
| Review | Send message3 | Split and Send (Review) | Call 'Actualizar_memoria_utq_bot'3 |
| Optimize | Send message4 | Split and Send (Optimize) | Call 'Actualizar_memoria_utq_bot'4 |

---

## Archivos de Referencia

1. `codigo_send_message_con_split.js` - Código completo autocontenido (Opción 1)
2. `codigo_division_mensajes.js` - Código solo para split (Opción 2)
3. `split_and_send_messages.json` - Subworkflow alternativo

---

¿Necesitas ayuda con la implementación? Los códigos están listos para copiar y pegar.
