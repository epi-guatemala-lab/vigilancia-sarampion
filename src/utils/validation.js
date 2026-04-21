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

export function validateField(field, value, formData = {}) {
  const errors = []

  // Campo requerido (estático) o condicionalmente requerido
  const isEmpty = (value === undefined || value === null || String(value).trim() === '')
  let dynamicallyRequired = false
  let requiredMessage = messages.required
  if (typeof field.requiredIf === 'function') {
    try {
      if (field.requiredIf(formData)) {
        dynamicallyRequired = true
        if (field.requiredIfMessage) requiredMessage = field.requiredIfMessage
      }
    } catch {
      /* ignore */
    }
  }
  if ((field.required || dynamicallyRequired) && isEmpty) {
    return [requiredMessage]
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

  // Validación por tipo (documento de identificación)
  if (rules.byType === 'identificacion') {
    const tipo = formData.tipo_identificacion
    if (tipo === 'DPI') {
      if (!/^\d{13}$/.test(strValue)) {
        errors.push('El DPI debe tener exactamente 13 dígitos numéricos')
      }
    } else if (tipo === 'PASAPORTE') {
      if (!/^[A-Za-z0-9]{9,12}$/.test(strValue)) {
        errors.push('El pasaporte debe tener entre 9 y 12 caracteres alfanuméricos')
      }
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
    const fieldErrors = validateField(field, formData[field.id], formData)
    if (fieldErrors.length > 0) {
      errors[field.id] = fieldErrors
      isValid = false
    }
  }

  return { isValid, errors }
}

/**
 * Validación cruzada de fechas — retorna advertencias (no bloquean el envío)
 */
export function validateCrossFieldDates(formData) {
  const warnings = []

  const parse = (key) => {
    const v = formData[key]
    if (!v) return null
    const d = new Date(v + 'T00:00:00')
    return isNaN(d.getTime()) ? null : d
  }

  const fechaSintomas = parse('fecha_inicio_sintomas')
  const fechaNotificacion = parse('fecha_notificacion')
  const fechaFiebre = parse('fecha_inicio_fiebre')
  const fechaErupcion = parse('fecha_inicio_erupcion')
  const fechaHosp = parse('hosp_fecha')
  const fechaEgreso = parse('fecha_egreso')
  const fechaDefuncion = parse('fecha_defuncion')
  const fechaNacimiento = parse('fecha_nacimiento')
  const fechaSalida = parse('viaje_fecha_salida')
  const fechaEntrada = parse('viaje_fecha_entrada')

  // Hoy (zona local; suficiente para no-future)
  const hoy = new Date()
  hoy.setHours(23, 59, 59, 999)

  if (fechaSintomas && fechaNotificacion && fechaSintomas > fechaNotificacion) {
    warnings.push('La fecha de inicio de síntomas es posterior a la fecha de notificación.')
  }
  if (fechaFiebre && fechaNotificacion && fechaFiebre > fechaNotificacion) {
    warnings.push('La fecha de inicio de fiebre es posterior a la fecha de notificación.')
  }
  if (fechaErupcion && fechaNotificacion && fechaErupcion > fechaNotificacion) {
    warnings.push('La fecha de inicio de erupción es posterior a la fecha de notificación.')
  }
  // Erupción y fiebre deben ser ≥ fecha inicio síntomas
  if (fechaErupcion && fechaSintomas && fechaErupcion < fechaSintomas) {
    warnings.push('La fecha de inicio de erupción es anterior a la fecha de inicio de síntomas.')
  }
  if (fechaFiebre && fechaSintomas && fechaFiebre < fechaSintomas) {
    warnings.push('La fecha de inicio de fiebre es anterior a la fecha de inicio de síntomas.')
  }
  // No pueden ser futuras
  if (fechaErupcion && fechaErupcion > hoy) {
    warnings.push('La fecha de inicio de erupción no puede ser posterior al día de hoy.')
  }
  if (fechaFiebre && fechaFiebre > hoy) {
    warnings.push('La fecha de inicio de fiebre no puede ser posterior al día de hoy.')
  }
  if (fechaSintomas && fechaSintomas > hoy) {
    warnings.push('La fecha de inicio de síntomas no puede ser posterior al día de hoy.')
  }
  if (fechaHosp && fechaSintomas && fechaHosp < fechaSintomas) {
    warnings.push('La fecha de hospitalización es anterior a la fecha de inicio de síntomas.')
  }
  if (fechaEgreso && fechaHosp && fechaEgreso < fechaHosp) {
    warnings.push('La fecha de egreso es anterior a la fecha de hospitalización.')
  }
  if (fechaDefuncion && fechaSintomas && fechaDefuncion < fechaSintomas) {
    warnings.push('La fecha de defunción es anterior a la fecha de inicio de síntomas.')
  }
  if (fechaNacimiento && fechaNotificacion && fechaNacimiento >= fechaNotificacion) {
    warnings.push('La fecha de nacimiento no es anterior a la fecha de notificación.')
  }
  if (fechaSalida && fechaEntrada && fechaSalida > fechaEntrada) {
    warnings.push('La fecha de salida del viaje es posterior a la fecha de entrada/retorno.')
  }

  return warnings
}

/**
 * Subset de validateCrossFieldDates que solo ejecuta las reglas
 * cuyos dos campos involucrados están presentes en `pageFieldIds`.
 * Útil para mostrar advertencias al navegar entre pestañas.
 */
export function validateCrossFieldDatesForPage(formData, pageFieldIds) {
  const all = validateCrossFieldDates(formData)
  // Como mapa simple: warnings que mencionen un campo de esta pagina
  // Usamos regex de keywords por warning.
  const ids = new Set(pageFieldIds)
  const keywords = {
    'fecha_inicio_sintomas': ['síntomas'],
    'fecha_notificacion': ['notificación'],
    'fecha_inicio_fiebre': ['fiebre'],
    'fecha_inicio_erupcion': ['erupción'],
    'hosp_fecha': ['hospitalización'],
    'fecha_egreso': ['egreso'],
    'fecha_defuncion': ['defunción'],
    'fecha_nacimiento': ['nacimiento'],
    'viaje_fecha_salida': ['salida del viaje'],
    'viaje_fecha_entrada': ['entrada/retorno'],
  }
  return all.filter((w) => {
    for (const id of ids) {
      const kws = keywords[id] || []
      if (kws.some((kw) => w.toLowerCase().includes(kw.toLowerCase()))) return true
    }
    return false
  })
}
