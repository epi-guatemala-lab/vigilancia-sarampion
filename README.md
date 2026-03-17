# Vigilancia Epidemiológica — Brote de Sarampión 2026

**IGSS** — Instituto Guatemalteco de Seguridad Social
Departamento de Medicina Preventiva — Sección de Epidemiología
Subgerencia de Prestaciones en Servicios de Salud

Formulario web multi-página para la recolección de datos de vigilancia epidemiológica del brote de sarampión 2026. Los datos se envían directamente a Google Sheets.

## Instalación Local

```bash
# Clonar el repositorio
git clone https://github.com/TU_USUARIO/vigilancia-sarampion.git
cd vigilancia-sarampion

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar servidor de desarrollo
npm run dev
```

## Configuración

1. **Google Sheets**: Ver [docs/SETUP_GOOGLE_SHEETS.md](docs/SETUP_GOOGLE_SHEETS.md)
2. **Deploy**: Ver [docs/DEPLOY_GITHUB_PAGES.md](docs/DEPLOY_GITHUB_PAGES.md)

## Stack Tecnológico

- **Frontend**: React 18 + Vite
- **Estilos**: Tailwind CSS (mobile-first)
- **Backend**: Google Apps Script / Google Sheets API v4
- **Hosting**: GitHub Pages

## Estructura del Formulario

El formulario tiene 8 secciones basadas en la ficha epidemiológica:

1. **Datos Administrativos** — Diagnóstico, unidad médica, fechas
2. **Datos del Paciente** — Afiliación, nombre, edad, residencia
3. **Embarazo** — Condicional si el paciente es femenino
4. **Consulta y Sintomatología** — Motivo de consulta, signos clínicos
5. **Vacunación** — Historial de SPR/SR
6. **Complicaciones** — Hospitalización, condición de egreso
7. **Laboratorio** — Muestras, IgG, IgM, RT-PCR
8. **Contactos y Clasificación** — Clasificación final del caso

## Personalización

Los campos se definen en `src/config/formSchema.js`. Cada campo tiene:
- `id`: Identificador único (nombre de columna en Sheets)
- `label`: Etiqueta visible
- `type`: Tipo de campo (text, select, date, radio, etc.)
- `page`: Página del formulario
- `required`: Si es obligatorio
- `conditional`: Reglas de visibilidad condicional
- `validation`: Reglas de validación

## Licencia

Uso interno IGSS Guatemala.
