/**
 * Organigrama IGSS — Diciembre 2024
 * Estructura jerárquica: Subgerencia → Dirección → Departamento → Sección
 */

const ORGANIGRAMA = {
  'Subgerencia Administrativa': {
    direcciones: [],
    departamentos: {
      'Comunicación Social y Relaciones Públicas': [],
      'Legal': ['Sección de Correspondencia y Archivo', 'Sección de Recopilación de Leyes'],
      'Abastecimientos': [],
      'Servicios de Apoyo': ['Sección de Biblioteca'],
      'Servicios Contratados': [],
    },
  },
  'Subgerencia Financiera': {
    direcciones: ['Dirección de Análisis de Riesgos Financieros', 'Dirección de Recaudación'],
    departamentos: {
      'Departamento de Presupuesto': [],
      'Departamento de Contabilidad': [],
      'Departamento de Tesorería': [],
      'Departamento de Inversiones': [],
      'Departamento de Cobro Administrativo': [],
      'Departamento de Cobro Judicial': [],
      'Departamento de Inspección Patronal': ['Sección Metropolitana', 'Sección de Coordinación Departamental', 'Sección Departamental', 'Sección de Fiscalización Electrónica'],
      'Departamento de Registro de Patronos y Trabajadores': [],
    },
  },
  'Subgerencia de Prestaciones en Salud': {
    direcciones: ['Dirección Terapéutica Central', 'Dirección Técnica de Logística de Insumos, Medicamentos y Equipo Médico'],
    departamentos: {
      'Departamento de Farmacoterapia': [],
      'Departamento de Farmacovigilancia': [],
      'Departamento de Farmacoeconomía': [],
      'Departamento de Dispositivos Médicos': [],
      'Departamento Médico de Servicios Centrales': [],
      'Departamento Médico de Servicios Técnicos': ['Sección de Enfermería', 'Sección de Registros Médicos y Bioestadística', 'Sección de Nutrición', 'Sección de Laboratorios y Patología', 'Sección de Bancos de Sangre', 'Sección de Radiología', 'Sección de Asistencia Farmacéutica'],
      'Departamento de Medicina Preventiva': ['Sección de Epidemiología', 'Sección de Higiene Materno Infantil', 'Sección de Seguridad e Higiene'],
    },
  },
  'Subgerencia de Prestaciones Pecuniarias': {
    direcciones: [],
    departamentos: {
      'Departamento de Prestaciones en Dinero': [],
      'Departamento de Invalidez, Vejez y Sobrevivencia': [],
      'Departamento de Medicina Legal y Evaluación de Incapacidades': [],
      'Departamento de Trabajo Social': [],
      'Centro de Atención al Afiliado (CATAFI)': [],
    },
  },
  'Subgerencia de Recursos Humanos': {
    direcciones: [],
    departamentos: {
      'Departamento de Gestión y Planeación del Recurso Humano': [],
      'Departamento de Compensaciones y Beneficios': [],
      'Departamento Jurídico-Laboral': [],
      'Departamento de Capacitación y Desarrollo': [],
    },
  },
  'Subgerencia de Planificación y Desarrollo': {
    direcciones: ['Dirección de Cooperación y Relaciones Internacionales (DICORI)'],
    departamentos: {
      'Departamento de Planificación': [],
      'Departamento Actuarial y Estadístico': [],
      'Departamento de Organización y Métodos': [],
      'Departamento de Infraestructura Institucional': [],
    },
  },
  'Subgerencia de Tecnología': {
    direcciones: ['Dirección de Investigación y Proyectos Tecnológicos', 'Dirección de Desarrollo y Gestión de Sistemas', 'Dirección de Tecnología y Servicio'],
    departamentos: {
      'Departamento de Gestión de Proyectos Tecnológicos': [],
      'Departamento de Riesgo, Investigación y Gestión del Cambio Tecnológico': [],
      'Departamento de Análisis y Desarrollo de Sistemas': [],
      'Departamento de Control de Calidad': [],
      'Departamento de Infraestructura Tecnológica': [],
      'Departamento de Telecomunicaciones, Conectividad y Seguridad': [],
      'Departamento de Soporte Técnico': [],
    },
  },
  'Subgerencia de Integridad y Transparencia Administrativa': {
    direcciones: [],
    departamentos: {
      'Departamento de Investigaciones Especiales': [],
      'Departamento de Cambio Institucional': [],
      'Departamento de Supervisión': [],
    },
  },
  'Gerencia': {
    direcciones: [],
    departamentos: {
      'Departamento de Auditoría Interna': [],
      'Departamento de Auditoría de Servicios de Salud': [],
      'Secretaría de Gerencia': [],
      'Unidad de Información Pública': [],
    },
  },
}

export function getSubgerencias() {
  return [...Object.keys(ORGANIGRAMA), 'OTRA']
}

export function getDirecciones(subgerencia) {
  if (!subgerencia || subgerencia === 'OTRA') return ['NO APLICA', 'OTRA']
  const sg = ORGANIGRAMA[subgerencia]
  if (!sg) return ['NO APLICA', 'OTRA']
  const dirs = sg.direcciones || []
  return dirs.length > 0 ? [...dirs, 'NO APLICA', 'OTRA'] : ['NO APLICA', 'OTRA']
}

export function getDepartamentosIGSS(subgerencia) {
  if (!subgerencia || subgerencia === 'OTRA') return ['OTRO']
  const sg = ORGANIGRAMA[subgerencia]
  if (!sg) return ['OTRO']
  return [...Object.keys(sg.departamentos || {}), 'OTRO']
}

export function getSecciones(subgerencia, departamento) {
  if (!subgerencia || !departamento || subgerencia === 'OTRA' || departamento === 'OTRO') return ['OTRA']
  const sg = ORGANIGRAMA[subgerencia]
  if (!sg) return ['OTRA']
  const secciones = (sg.departamentos || {})[departamento] || []
  return secciones.length > 0 ? [...secciones, 'NO APLICA', 'OTRA'] : ['NO APLICA', 'OTRA']
}

export default ORGANIGRAMA
