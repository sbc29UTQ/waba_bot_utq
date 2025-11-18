// ============================================
// CÓDIGO PARA DIVIDIR Y ENVIAR MENSAJES LARGOS
// ============================================
// Este código debe agregarse como un nodo "Code" después de cada agente
// y ANTES del nodo "Send message"

// Obtener el output del agente anterior
const agentOutput = $input.item.json.output || '';
const phoneNumber = $('Extraer datos del user').item.json.phone_number;
const MAX_LENGTH = 130;

// Si el mensaje es <= 130 caracteres, retornar como está
if (agentOutput.length <= MAX_LENGTH) {
  return [{
    json: {
      message: agentOutput,
      phone_number: phoneNumber,
      total_parts: 1,
      part_number: 1
    }
  }];
}

// ============================================
// FUNCIÓN PARA DIVIDIR EL MENSAJE
// ============================================
function splitMessage(text, maxLength) {
  const chunks = [];
  let remaining = text;

  while (remaining.length > 0) {
    if (remaining.length <= maxLength) {
      chunks.push(remaining);
      break;
    }

    // Buscar punto de corte natural (70% del max length)
    let cutPoint = maxLength;
    const searchText = remaining.substring(0, maxLength);
    const minCutPoint = Math.floor(maxLength * 0.7);

    // Buscar último: salto de línea, punto, coma o espacio
    const lastNewline = searchText.lastIndexOf('\n');
    const lastPeriod = searchText.lastIndexOf('. ');
    const lastComma = searchText.lastIndexOf(', ');
    const lastSpace = searchText.lastIndexOf(' ');

    // Elegir el mejor punto de corte
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

  // Limitar a máximo 3 partes
  if (chunks.length > 3) {
    const extraChunks = chunks.slice(2);
    chunks[2] = extraChunks.join(' ');
    chunks.length = 3;
  }

  return chunks;
}

// ============================================
// DIVIDIR EL MENSAJE EN CHUNKS
// ============================================
const messageParts = splitMessage(agentOutput, MAX_LENGTH);
const totalParts = messageParts.length;

// ============================================
// RETORNAR MÚLTIPLES ITEMS (uno por cada parte)
// ============================================
// n8n procesará cada item secuencialmente
return messageParts.map((part, index) => ({
  json: {
    message: part,
    phone_number: phoneNumber,
    total_parts: totalParts,
    part_number: index + 1,
    needs_delay: index > 0  // true si no es el primer mensaje
  }
}));
