/**
 * Lógica condicional para campos dinámicos del formulario.
 * Evalúa si un campo debe mostrarse según el estado actual del formulario.
 */

/**
 * Determina si un campo es visible según las reglas condicionales
 */
export function isFieldVisible(field, formData) {
  if (!field.conditional) return true

  const { dependsOn, showWhen } = field.conditional
  const dependValue = formData[dependsOn]

  if (dependValue === undefined || dependValue === null || dependValue === '') {
    return false
  }

  // showWhen puede ser un valor único o un array de valores
  if (Array.isArray(showWhen)) {
    return showWhen.includes(dependValue)
  }

  return String(dependValue).trim() === String(showWhen).trim()
}

/**
 * Determina si una página completa debe mostrarse.
 * Una página se salta si TODOS sus campos son condicionales y NINGUNO es visible.
 */
export function isPageVisible(pageFields, formData) {
  if (pageFields.length === 0) return false

  const conditionalFields = pageFields.filter(f => f.conditional)

  // Si hay campos no condicionales, la página siempre se muestra
  if (conditionalFields.length < pageFields.length) return true

  // Si todos son condicionales, mostrar solo si al menos uno es visible
  return conditionalFields.some(f => isFieldVisible(f, formData))
}

/**
 * Obtiene las páginas visibles en orden
 */
export function getVisiblePages(allPages, formData) {
  return Object.entries(allPages)
    .filter(([_, fields]) => isPageVisible(fields, formData))
    .map(([pageNum]) => parseInt(pageNum))
    .sort((a, b) => a - b)
}

/**
 * Limpia datos de campos que ya no son visibles
 */
export function cleanHiddenFieldData(formData, allFields) {
  const cleaned = { ...formData }
  for (const field of allFields) {
    if (field.conditional && !isFieldVisible(field, formData)) {
      delete cleaned[field.id]
    }
  }
  return cleaned
}
