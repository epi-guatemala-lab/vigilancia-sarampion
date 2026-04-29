/**
 * Validaciones por tipo de campo — mensajes en español
 *
 * Reglas de fecha (deben coincidir con vigilancia_activa/validacion_fechas.py):
 *   AÑO_MIN_CASO = 2024 (Guatemala libre de sarampión hasta 2026, +margen importados)
 *   DIAS_NOTIF_SINTOMAS_HARD = 180 (rechazo)
 *   DIAS_NOTIF_SINTOMAS_SOFT = 90 (advertencia)
 */

export const AÑO_MIN_CASO = 2024
export const DIAS_NOTIF_SINTOMAS_HARD = 180
export const DIAS_NOTIF_SINTOMAS_SOFT = 90

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
  yearMin: (y) => `El año no puede ser anterior a ${y} (probable error de captura)`,
  yearMax: (y) => `El año no puede ser posterior a ${y}`,
  dateFormat: 'El formato de fecha no es válido. Use el selector o YYYY-MM-DD',
  dateThreeDigitYear: 'Año con 3 dígitos detectado. Asegúrese de escribir 4 dígitos (ej. 2026)',
}

/**
 * Parser flexible de fechas. Acepta:
 *   YYYY-MM-DD (ISO, default de input[type=date])
 *   DD/MM/YYYY, DD-MM-YYYY
 *   YYYY/MM/DD
 *   DD/MM/YY → 2000+YY si YY<50, 1900+YY si no
 * RECHAZA año de 3 dígitos ("09/04/226" típico typo) → retorna null
 *
 * @returns {Date|null}
 */
export function parsearFechaFlexible(valor) {
  if (valor === null || valor === undefined) return null
  if (valor instanceof Date && !isNaN(valor.getTime())) return valor
  const s = String(valor).trim()
  if (!s) return null
  // Detectar typo "09/04/226" (año de 3 dígitos)
  const m3 = s.match(/^(\d{1,2})[/\-](\d{1,2})[/\-](\d{1,4})$/)
  if (m3 && m3[3].length === 3) return null

  const formats = [
    /^(\d{4})-(\d{2})-(\d{2})$/,                    // YYYY-MM-DD
    /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/,              // DD/MM/YYYY
    /^(\d{1,2})-(\d{1,2})-(\d{4})$/,                // DD-MM-YYYY
    /^(\d{4})\/(\d{1,2})\/(\d{1,2})$/,              // YYYY/MM/DD
    /^(\d{1,2})\/(\d{1,2})\/(\d{2})$/,              // DD/MM/YY
  ]
  for (let i = 0; i < formats.length; i++) {
    const m = s.match(formats[i])
    if (!m) continue
    let y, mo, d
    if (i === 0 || i === 3) { // YYYY-MM-DD o YYYY/MM/DD
      y = parseInt(m[1], 10); mo = parseInt(m[2], 10); d = parseInt(m[3], 10)
    } else if (i === 4) { // DD/MM/YY
      d = parseInt(m[1], 10); mo = parseInt(m[2], 10)
      const yy = parseInt(m[3], 10)
      y = yy < 50 ? 2000 + yy : 1900 + yy
    } else { // DD/MM/YYYY o DD-MM-YYYY
      d = parseInt(m[1], 10); mo = parseInt(m[2], 10); y = parseInt(m[3], 10)
    }
    if (mo < 1 || mo > 12 || d < 1 || d > 31) return null
    const dt = new Date(y, mo - 1, d, 0, 0, 0, 0)
    // Verificar que la conversión no rolló (ej: 31/02 → 03/03)
    if (dt.getFullYear() !== y || dt.getMonth() !== mo - 1 || dt.getDate() !== d) return null
    return dt
  }
  return null
}

/**
 * Valida una fecha individual contra reglas hard/soft.
 *
 * @param {string|Date} valor
 * @param {string} campo - id del campo (para mensaje)
 * @param {{añoMin?: number, añoMax?: number, permiteFutura?: boolean, esNacimiento?: boolean}} opts
 * @returns {{fecha: Date|null, hard: string[], soft: string[]}}
 */
export function validarFechaCaso(valor, campo, opts = {}) {
  const año_min = opts.añoMin ?? AÑO_MIN_CASO
  const año_max = opts.añoMax ?? (new Date().getFullYear() + 1)
  const hard = []
  const soft = []

  if (valor === null || valor === undefined || String(valor).trim() === '') {
    return { fecha: null, hard, soft }
  }

  // Detectar typo de 3 dígitos antes del parse general
  const s = String(valor).trim()
  const m3 = s.match(/^(\d{1,2})[/\-](\d{1,2})[/\-](\d{1,4})$/)
  if (m3 && m3[3].length === 3) {
    hard.push(messages.dateThreeDigitYear)
    return { fecha: null, hard, soft }
  }

  const fecha = parsearFechaFlexible(valor)
  if (!fecha) {
    hard.push(messages.dateFormat)
    return { fecha: null, hard, soft }
  }

  const hoy = new Date(); hoy.setHours(23, 59, 59, 999)

  if (opts.esNacimiento) {
    if (fecha > hoy) hard.push('La fecha de nacimiento no puede ser futura')
    if (fecha.getFullYear() < 1900) hard.push('La fecha de nacimiento no puede ser anterior a 1900')
    return { fecha, hard, soft }
  }

  if (fecha.getFullYear() < año_min) hard.push(messages.yearMin(año_min))
  if (fecha.getFullYear() > año_max) hard.push(messages.yearMax(año_max))
  if (!opts.permiteFutura && fecha > hoy) hard.push(messages.noFuture)

  return { fecha, hard, soft }
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
    const dt = parsearFechaFlexible(value)
    if (dt && dt > today) {
      errors.push(messages.noFuture)
    }
  }

  // Año mínimo (rechaza typos como "2023" o "1991")
  if (rules.yearMin && field.type === 'date') {
    const dt = parsearFechaFlexible(value)
    if (dt && dt.getFullYear() < rules.yearMin) {
      errors.push(messages.yearMin(rules.yearMin))
    }
  }

  // Año máximo
  if (rules.yearMax && field.type === 'date') {
    const dt = parsearFechaFlexible(value)
    if (dt && dt.getFullYear() > rules.yearMax) {
      errors.push(messages.yearMax(rules.yearMax))
    }
  }

  // Parser flexible: rechaza formatos inválidos como "09/04/226" (año 3 dígitos)
  if (rules.flexibleParse && field.type === 'date') {
    const m3 = strValue.match(/^(\d{1,2})[/\-](\d{1,2})[/\-](\d{1,4})$/)
    if (m3 && m3[3].length === 3) {
      errors.push(messages.dateThreeDigitYear)
    } else if (parsearFechaFlexible(strValue) === null) {
      errors.push(messages.dateFormat)
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
 * Validación de coherencia entre fechas con separación HARD vs SOFT.
 * HARD = bloquea el envío. SOFT = warning con confirm() (no bloquea).
 *
 * @returns {{hard: string[], soft: string[]}}
 */
export function validarCoherenciaFechas(formData) {
  const hard = []
  const soft = []

  const fis = parsearFechaFlexible(formData.fecha_inicio_sintomas)
  const fnotif = parsearFechaFlexible(formData.fecha_notificacion)
  const fnac = parsearFechaFlexible(formData.fecha_nacimiento)

  // HARD: notificación anterior a síntomas (inversión cronológica)
  if (fis && fnotif && fnotif < fis) {
    hard.push(
      'La fecha de notificación es anterior a la fecha de inicio de síntomas. ' +
      'La notificación no puede ocurrir antes de los síntomas.'
    )
  }

  // HARD: diferencia notif - síntomas mayor a 180 días (probable typo)
  if (fis && fnotif) {
    const diff = Math.round((fnotif - fis) / 86400000)
    if (diff > DIAS_NOTIF_SINTOMAS_HARD) {
      hard.push(
        `Diferencia entre notificación y síntomas = ${diff} días ` +
        `(>${DIAS_NOTIF_SINTOMAS_HARD}, probable error de captura)`
      )
    } else if (diff > DIAS_NOTIF_SINTOMAS_SOFT) {
      soft.push(
        `Diferencia entre notificación y síntomas = ${diff} días ` +
        `(>${DIAS_NOTIF_SINTOMAS_SOFT}, verificar)`
      )
    }
  }

  // HARD: fecha de nacimiento posterior a fecha del caso (paciente "no nacido")
  if (fnac && fis && fnac > fis) {
    hard.push('La fecha de nacimiento es posterior a la fecha de inicio de síntomas')
  }
  if (fnac && fnotif && fnac > fnotif) {
    hard.push('La fecha de nacimiento es posterior a la fecha de notificación')
  }

  // Coherencia edad declarada vs calculada (SOFT)
  const edadDeclarada = parseInt(String(formData.edad_anios || '').trim(), 10)
  if (fnac && Number.isFinite(edadDeclarada) && edadDeclarada >= 0 && edadDeclarada <= 130) {
    const ref = fis || fnotif || new Date()
    const edadCalc = Math.floor((ref - fnac) / (365.25 * 86400000))
    if (Math.abs(edadCalc - edadDeclarada) > 2) {
      soft.push(
        `Edad declarada (${edadDeclarada}) difiere de la calculada (${edadCalc}) ` +
        `desde la fecha de nacimiento`
      )
    }
  }

  // El resto de las reglas existentes (warnings) se mantienen como SOFT
  const todasWarnings = validateCrossFieldDates(formData)
  for (const w of todasWarnings) {
    // Las que ya capturamos como HARD no se duplican
    const yaHard = hard.some(h => h.toLowerCase().includes(w.toLowerCase().slice(0, 30)))
    if (yaHard) continue
    if (!soft.includes(w)) soft.push(w)
  }

  return { hard, soft }
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
