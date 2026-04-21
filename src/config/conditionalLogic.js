/**
 * Lógica condicional para campos dinámicos del formulario.
 * Evalúa si un campo debe mostrarse según el estado actual del formulario.
 */

/**
 * Determina si un campo es visible según las reglas condicionales
 */
export function isFieldVisible(field, formData) {
  if (!field.conditional) return true

  const { dependsOn, showWhen, showWhenNot, additionalCheck } = field.conditional
  const dependValue = formData[dependsOn]

  if (dependValue === undefined || dependValue === null || dependValue === '') {
    return false
  }

  // dependValue puede ser array (checkbox multi-select) o string
  const depValues = Array.isArray(dependValue) ? dependValue : [String(dependValue).trim()]
  if (depValues.length === 0) return false

  let matchesShowWhen = true
  if (showWhen !== undefined) {
    if (Array.isArray(showWhen)) {
      matchesShowWhen = depValues.some(v => showWhen.includes(v))
    } else {
      matchesShowWhen = depValues.includes(String(showWhen).trim())
    }
  }

  // showWhenNot: muestra el campo cuando el valor NO coincide con estos.
  // Útil para "cualquier cosa excepto X" (ej. cualquier país != GUATEMALA).
  let matchesShowWhenNot = true
  if (showWhenNot !== undefined) {
    const excl = Array.isArray(showWhenNot) ? showWhenNot : [String(showWhenNot).trim()]
    matchesShowWhenNot = !depValues.some(v => excl.includes(v))
  }

  if (!matchesShowWhen || !matchesShowWhenNot) return false

  if (typeof additionalCheck === 'function') {
    try {
      return !!additionalCheck(formData)
    } catch {
      return true
    }
  }

  return true
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
