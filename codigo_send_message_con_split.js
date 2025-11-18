// ============================================
// CÓDIGO AUTO-CONTENIDO: DIVIDIR Y ENVIAR MENSAJES
// ============================================
// Este código REEMPLAZA el nodo "Send message"
// Divide mensajes largos y los envía con delay de 5 segundos

// ============================================
// CONFIGURACIÓN
// ============================================
const PHONE_NUMBER_ID = '730111076863264';  // Tu WhatsApp Business Phone Number ID
const ACCESS_TOKEN = '{{ $credentials.whatsAppTriggerApi.accessToken }}';  // Token de WhatsApp
const MAX_LENGTH = 130;
const DELAY_MS = 5000;  // 5 segundos

// Obtener datos del flujo
const agentOutput = $input.item.json.output || '';
const recipientPhone = $('Extraer datos del user').item.json.phone_number;

// ============================================
// FUNCIÓN: DIVIDIR MENSAJE
// ============================================
function splitMessage(text, maxLength) {
  if (text.length <= maxLength) {
    return [text];
  }

  const chunks = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (remaining.length <= maxLength) {
      chunks.push(remaining);
      break;
    }

    let cutPoint = maxLength;
    const searchText = remaining.substring(0, maxLength);
    const minCutPoint = Math.floor(maxLength * 0.7);

    // Buscar puntos de corte naturales
    const lastNewline = searchText.lastIndexOf('\\n');
    const lastPeriod = searchText.lastIndexOf('. ');
    const lastComma = searchText.lastIndexOf(', ');
    const lastSpace = searchText.lastIndexOf(' ');

    if (lastNewline > minCutPoint) {
      cutPoint = lastNewline + 1;
    } else if (lastPeriod > minCutPoint) {
      cutPoint = lastPeriod + 2;
    } else if (lastComma > minCutPoint) {
      cutPoint = lastComma + 2;
    } else if (lastSpace > minCutPoint) {
      cutPoint = lastSpace + 1;
    }

    chunks.push(remaining.substring(0, cutPoint).trim());
    remaining = remaining.substring(cutPoint).trim();
  }

  // Limitar a 3 partes
  if (chunks.length > 3) {
    const extraChunks = chunks.slice(2);
    chunks[2] = extraChunks.join(' ');
    chunks.length = 3;
  }

  return chunks;
}

// ============================================
// FUNCIÓN: ENVIAR MENSAJE A WHATSAPP
// ============================================
async function sendWhatsAppMessage(phoneNumber, message) {
  const url = `https://graph.facebook.com/v21.0/${PHONE_NUMBER_ID}/messages`;

  const response = await $http.request({
    method: 'POST',
    url: url,
    headers: {
      'Authorization': `Bearer ${ACCESS_TOKEN}`,
      'Content-Type': 'application/json'
    },
    body: {
      messaging_product: 'whatsapp',
      to: phoneNumber,
      type: 'text',
      text: {
        body: message
      }
    },
    json: true
  });

  return response;
}

// ============================================
// FUNCIÓN: ESPERAR (DELAY)
// ============================================
function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================
// PROCESO PRINCIPAL
// ============================================
const messageParts = splitMessage(agentOutput, MAX_LENGTH);
const results = [];

// Enviar cada parte con delay
for (let i = 0; i < messageParts.length; i++) {
  const part = messageParts[i];

  // Si no es el primer mensaje, esperar 5 segundos
  if (i > 0) {
    await wait(DELAY_MS);
  }

  // Enviar mensaje
  try {
    const response = await sendWhatsAppMessage(recipientPhone, part);
    results.push({
      part_number: i + 1,
      total_parts: messageParts.length,
      message: part,
      success: true,
      response: response
    });
  } catch (error) {
    results.push({
      part_number: i + 1,
      total_parts: messageParts.length,
      message: part,
      success: false,
      error: error.message
    });
  }
}

// ============================================
// RETORNAR RESULTADO
// ============================================
return [{
  json: {
    phone_number: recipientPhone,
    original_message: agentOutput,
    total_parts: messageParts.length,
    messages_sent: results,
    all_sent: results.every(r => r.success)
  }
}];
