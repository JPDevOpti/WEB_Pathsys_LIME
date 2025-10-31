// Sanitiza HTML básico para mostrar contenido en notificaciones
export function sanitizeHtml(input: string): string {
  if (!input || typeof input !== 'string') return ''

  // Eliminar etiquetas <script>
  const withoutScripts = input.replace(/<\s*script[^>]*>[\s\S]*?<\s*\/\s*script\s*>/gi, '')

  // Eliminar atributos de eventos (onclick, onerror, etc.)
  const withoutEvents = withoutScripts.replace(/\son[a-z]+\s*=\s*(['"]).*?\1/gi, '')

  // Neutralizar URLs javascript: en href/src
  const withoutJsUrls = withoutEvents.replace(/(href|src)\s*=\s*(['"])\s*javascript:[^'"\s]*\2/gi, '$1="#"')

  // Eliminar expresiones peligrosas en estilos
  const withoutExpression = withoutJsUrls.replace(/style\s*=\s*(['"])[\s\S]*?expression\([^'"]*\)\1/gi, '')

  // Eliminar iframes/objects/embeds potencialmente peligrosos
  const withoutEmbeds = withoutExpression.replace(/<\s*(iframe|object|embed)[^>]*>[\s\S]*?<\s*\/\s*\1\s*>/gi, '')

  return withoutEmbeds
}