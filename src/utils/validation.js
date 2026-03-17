/**
 * Validaciones por tipo de campo — mensajes en español
 */

const messages = {
  required: 'Este campo es obligatorio',
  minLength: (n) => `Debe tener al menos ${n} caracteres`,
  maxLength: (n) => `No debe exceder ${n} caracteres`,
  min: (n) => `El valor mínimo es ${n}`,
  max: (n) => `El valor máximo es ${n}`,
  email: 'Ingrese un correo electrónico válido',
  phone: 'Ingrese un número de teléfono válido (8 dígitos)',
  noFuture: 'La fecha no puede ser futura',
  pattern: 'El formato no es válido',
  dpi: 'El DPI debe tener 13 dígitos',
}

export function validateField(field, value) {
  const errors = []

  // Campo requerido
  if (field.required) {
    if (value === undefined || value === null || String(value).trim() === '') {
      return [messages.required]
    }
  }

  // Si no es requerido y está vacío, no validar más
  if (value === undefined || value === null || String(value).trim() === '') {
    return []
  }

  const strValue = String(value).trim()
  const rules = field.validation || {}

  // Longitud mínima
  if (rules.minLength && strValue.length < rules.minLength) {
    errors.push(messages.minLength(rules.minLength))
  }

  // Longitud máxima
  if (rules.maxLength && strValue.length > rules.maxLength) {
    errors.push(messages.maxLength(rules.maxLength))
  }

  // Valor mínimo (números)
  if (rules.min !== undefined && Number(value) < rules.min) {
    errors.push(messages.min(rules.min))
  }

  // Valor máximo (números)
  if (rules.max !== undefined && Number(value) > rules.max) {
    errors.push(messages.max(rules.max))
  }

  // No fecha futura
  if (rules.noFuture && field.type === 'date') {
    const today = new Date()
    today.setHours(23, 59, 59, 999)
    if (new Date(value) > today) {
      errors.push(messages.noFuture)
    }
  }

  // Email
  if (field.type === 'email') {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(strValue)) {
      errors.push(messages.email)
    }
  }

  // Teléfono Guatemala
  if (field.type === 'phone') {
    const phoneRegex = /^\d{8}$/
    if (!phoneRegex.test(strValue.replace(/\s/g, ''))) {
      errors.push(messages.phone)
    }
  }

  // Patrón personalizado
  if (rules.pattern) {
    const regex = new RegExp(rules.pattern)
    if (!regex.test(strValue)) {
      errors.push(rules.patternMessage || messages.pattern)
    }
  }

  return errors
}

/**
 * Valida todos los campos visibles de una página
 */
export function validatePage(fields, formData) {
  const errors = {}
  let isValid = true

  for (const field of fields) {
    const fieldErrors = validateField(field, formData[field.id])
    if (fieldErrors.length > 0) {
      errors[field.id] = fieldErrors
      isValid = false
    }
  }

  return { isValid, errors }
}
