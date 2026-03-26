# GoData Guatemala - Referencia Completa del Brote Sarampion

**Generado**: 2026-03-26
**Instancia**: https://godataguatemala.mspas.gob.gt
**Outbreak ID**: `ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19`

## 1. Informacion del Brote

| Campo | Valor |
|-------|-------|
| **Nombre** | Taller Sarampion |
| **Enfermedad** | LNG_REFERENCE_DATA_CATEGORY_DISEASE_MEASLES (Sarampion/Measles) |
| **Fecha inicio** | 2025-12-15T00:00:00.000Z |
| **Fecha fin** | 2027-12-31T00:00:00.000Z |
| **Case ID Mask** | `SR-9999` (SR-0001, SR-0002...) |
| **Contact ID Mask** | `CO-9999` (CO-0001, CO-0002...) |
| **Periodo seguimiento** | 21 dias |
| **Frecuencia seguimiento** | Cada 1 dia(s) |
| **Dias entre contactos** | 7 |
| **Dias en cadenas** | 7 |
| **Dias no vistos** | 3 |
| **Generar seguimientos al crear contactos** | True |
| **Generar seguimientos al crear casos** | False |
| **Total casos actuales** | 5 |

## 2. Autenticacion API

**IMPORTANTE: Esta instancia usa OAuth2 (NO el formato estandar GoData)**

```bash
GODATA="https://godataguatemala.mspas.gob.gt/api"

# Obtener token (formato OAuth2)
TOKEN=$(curl -s -X POST "$GODATA/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{"username":"practica4@gmail.com","password":"sarampion123456"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

# Usar con header Authorization: Bearer
curl -H "Authorization: Bearer $TOKEN" "$GODATA/outbreaks/$OUTBREAK_ID/cases"
```

Respuesta de autenticacion:
```json
{
  "token_type": "bearer",
  "expires_in": 600,
  "access_token": "BFjJbci..."
}
```

**NO usar** `?access_token=TOKEN` como query parameter. Siempre usar header `Authorization: Bearer TOKEN`.

## 3. Plantilla de Investigacion de Caso (Case Investigation Template)

### 3.1 Campos Estandar del Caso (Standard Fields)

Estos campos van en el JSON raiz del caso, NO en `questionnaireAnswers`:

| Campo | Tipo | Obligatorio | Valores posibles |
|-------|------|-------------|------------------|
| `firstName` | string | SI | Nombre(s) |
| `middleName` | string | NO | Segundo nombre |
| `lastName` | string | SI | Apellidos |
| `gender` | ref_data | SI | `LNG_REFERENCE_DATA_CATEGORY_GENDER_FEMALE`, `_MALE` |
| `dob` | date | NO | ISO 8601: `1964-02-26T00:00:00.000Z` |
| `age` | object | NO | `{"years": 62, "months": 0}` |
| `dateOfOnset` | date | SI | Fecha inicio sintomas |
| `dateOfReporting` | date | SI | Fecha de reporte |
| `visualId` | string | SI | Auto-generado: SR-NNNN |
| `pregnancyStatus` | ref_data | visible | Ver seccion Ref Data |
| `classification` | ref_data | NO | Ver seccion Case Classification |
| `outcomeId` | ref_data | NO | Ver seccion Outcomes |
| `riskLevel` | ref_data | NO | Ver seccion Risk Level |
| `addresses` | array | NO | Array de direcciones |
| `documents` | array | NO | Array de documentos |
| `vaccinesReceived` | array | NO | Array de vacunas |
| `dateRanges` | array | NO | Hospitalizacion, aislamiento |

### 3.2 Preguntas del Cuestionario (questionnaireAnswers)

Todas estas preguntas van dentro del objeto `questionnaireAnswers` del caso.
Formato: `"variable_name": [{"value": "respuesta"}]`

#### `diagnostico_de_sospecha_`
- **Texto**: DIAGNOSTICO DE SOSPECHA
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_FICHA_EPIDEMIOLOGICA_DE_VIGILANCIA_DE_SARAMPION_RUBEOLA_DIRECCION_DE_EPIDEMIOLOGIA_Y_GESTION_DE_RIESGO
- **Opciones**:
  - `"SARAMPIÓN"` = SARAMPIÓN
  - `"RUBÉOLA"` = RUBÉOLA
  - `"DENGUE"` = DENGUE
  - `"OTRO ARBOVIROSIS"` = OTRO ARBOVIROSIS
  - `"OTRO FEBRIL EXANTEMÁTICA"` = OTRO FEBRIL EXANTEMÁTICA

> **Sub-pregunta** (aparece cuando respuesta = `"SARAMPIÓN"`)

  ##### `caso_altamente_sospechoso_de_sarampion`
  - **Texto**: CASO ALTAMENTE SOSPECHOSO DE SARAMPIÓN
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO

> **Sub-pregunta** (aparece cuando respuesta = `"OTRO ARBOVIROSIS"`)

  ##### `especifique`
  - **Texto**: ESPECIFIQUE OTRO ARBOVIROSIS
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"OTRO FEBRIL EXANTEMÁTICA"`)

  ##### `especifique_`
  - **Texto**: ESPECIFIQUE OTRO FEBRIL EXANTEMÁTICA
  - **Tipo**: Texto libre

#### `fecha_de_notificacion`
- **Texto**: DATOS DE LA UNIDAD NOTIFICADORA
- **Tipo**: Respuesta unica
- **Obligatorio**: SI
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_DATOS_DE_LA_UNIDAD_NOTIFICADORA
- **Opciones**:
  - `"Fecha de Notificación"` = UNIDAD NOTIFICADORA

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `direccion_de_area_de_salud`
  - **Texto**: DIRECCIÓN DEPARTAMENTAL DE REDES INTEGRADAS DE SERVICIOS DE SALUD (DDRISS)
  - **Tipo**: Respuesta unica
  - **Obligatorio**: SI
  - **Opciones**:
    - `"ALTA VERAPAZ"` = ALTA VERAPAZ
    - `"BAJA VERAPAZ"` = BAJA VERAPAZ
    - `"CHIMALTENANGO"` = CHIMALTENANGO
    - `"CHIQUIMULA"` = CHIQUIMULA
    - `"EL PROGRESO"` = EL PROGRESO
    - `"ESCUINTLA"` = ESCUINTLA
    - `"GUATEMALA CENTRAL"` = GUATEMALA CENTRAL
    - `"GUATEMALA NOR OCCIDENTE"` = GUATEMALA NOR OCCIDENTE
    - `"GUATEMALA NOR ORIENTE"` = GUATEMALA NOR ORIENTE
    - `"GUATEMALA SUR"` = GUATEMALA SUR
    - `"HUEHUETENANGO"` = HUEHUETENANGO
    - `"IXCÁN"` = IXCÁN
    - `"IXIL"` = IXIL
    - `"IZABAL"` = IZABAL
    - `"JALAPA"` = JALAPA
    - `"JUTIAPA"` = JUTIAPA
    - `"PETÉN NORTE"` = PETÉN NORTE
    - `"PETÉN SUR OCCIDENTE"` = PETÉN SUR OCCIDENTE
    - `"PETÉN SUR ORIENTE"` = PETÉN SUR ORIENTE
    - `"QUETZALTENANGO"` = QUETZALTENANGO
    - `"QUICHÉ"` = QUICHÉ
    - `"RETALHULEU"` = RETALHULEU
    - `"SACATEPÉQUEZ"` = SACATEPÉQUEZ
    - `"SAN MARCOS"` = SAN MARCOS
    - `"SANTA ROSA"` = SANTA ROSA
    - `"SOLOLÁ"` = SOLOLÁ
    - `"SUCHITEPÉQUEZ"` = SUCHITEPÉQUEZ
    - `"TOTONICAPAN"` = TOTONICAPAN
    - `"ZACAPA"` = ZACAPA

  > **Sub-pregunta** (aparece cuando respuesta = `"ALTA VERAPAZ"`)

    ###### `distrito_municipal_de_salud_dms`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CAHABON"` = CAHABON
      - `"CAMPUR"` = CAMPUR
      - `"CHAHAL"` = CHAHAL
      - `"CHISEC"` = CHISEC
      - `"COBAN"` = COBAN
      - `"FRAY BARTOLOME DE LAS CASAS"` = FRAY BARTOLOME DE LAS CASAS
      - `"LA TINTA"` = LA TINTA
      - `"LANQUIN"` = LANQUIN
      - `"PANZOS"` = PANZOS
      - `"RAXRUHA"` = RAXRUHA
      - `"SAN CRISTOBAL VERAPAZ"` = SAN CRISTOBAL VERAPAZ
      - `"SAN JUAN CHAMELCO"` = SAN JUAN CHAMELCO
      - `"SAN PEDRO CARCHA"` = SAN PEDRO CARCHA
      - `"SANTA CRUZ VERAPAZ"` = SANTA CRUZ VERAPAZ
      - `"SENAHU"` = SENAHU
      - `"TACTIC"` = TACTIC
      - `"TAMAHU"` = TAMAHU
      - `"TELEMAN"` = TELEMAN
      - `"TUCURU"` = TUCURU

  > **Sub-pregunta** (aparece cuando respuesta = `"ALTA VERAPAZ"`)

    ###### `servicio_de_salud`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"BAJA VERAPAZ"`)

    ###### `distrito_municipal_de_salud_dms_`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CUBULCO"` = CUBULCO
      - `"EL CHOL"` = EL CHOL
      - `"GRANADOS"` = GRANADOS
      - `"PURULHA"` = PURULHA
      - `"RABINAL"` = RABINAL
      - `"SALAMA"` = SALAMA
      - `"SAN JERONIMO"` = SAN JERONIMO
      - `"SAN MIGUEL CHICAJ"` = SAN MIGUEL CHICAJ

  > **Sub-pregunta** (aparece cuando respuesta = `"BAJA VERAPAZ"`)

    ###### `servicio_de_salud_1`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"CHIMALTENANGO"`)

    ###### `distrito_municipal_de_salud_dms_CHI`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"ACATENANGO"` = ACATENANGO
      - `"CHIMALTENANGO"` = CHIMALTENANGO
      - `"EL TEJAR"` = EL TEJAR
      - `"PAQUIP TECPAN GUATEMALA"` = PAQUIP TECPAN GUATEMALA
      - `"PARRAMOS"` = PARRAMOS
      - `"PATZICIA"` = PATZICIA
      - `"PATZUN"` = PATZUN
      - `"SAN ANDRES ITZAPA"` = SAN ANDRES ITZAPA
      - `"SAN JOSE POAQUIL"` = SAN JOSE POAQUIL
      - `"SAN JUAN COMALAPA"` = SAN JUAN COMALAPA
      - `"SAN MARTIN JILOTEPEQUE"` = SAN MARTIN JILOTEPEQUE
      - `"SAN MIGUEL POCHUTA"` = SAN MIGUEL POCHUTA
      - `"SAN PEDRO YEPOCAPA"` = SAN PEDRO YEPOCAPA
      - `"SANTA APOLONIA"` = SANTA APOLONIA
      - `"SANTA CRUZ BALANYA"` = SANTA CRUZ BALANYA
      - `"TECPAN GUATEMALA"` = TECPAN GUATEMALA
      - `"ZARAGOZA"` = ZARAGOZA

  > **Sub-pregunta** (aparece cuando respuesta = `"CHIMALTENANGO"`)

    ###### `servicio_de_salud_2`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"CHIQUIMULA"`)

    ###### `distrito_municipal_de_salud_dms_CH`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CAMOTAN"` = CAMOTAN
      - `"CHIQUIMULA"` = CHIQUIMULA
      - `"CONCEPCION LAS MINAS"` = CONCEPCION LAS MINAS
      - `"ESQUIPULAS"` = ESQUIPULAS
      - `"IPALA"` = IPALA
      - `"JOCOTAN"` = JOCOTAN
      - `"OLOPA"` = OLOPA
      - `"QUETZALTEPEQUE"` = QUETZALTEPEQUE
      - `"SAN JACINTO"` = SAN JACINTO
      - `"SAN JOSE LA ARADA"` = SAN JOSE LA ARADA
      - `"SAN JUAN LA ERMITA"` = SAN JUAN LA ERMITA

  > **Sub-pregunta** (aparece cuando respuesta = `"CHIQUIMULA"`)

    ###### `servicio_de_salud_3`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"EL PROGRESO"`)

    ###### `distrito_municipal_de_salud_dms1`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"EL JICARO"` = EL JICARO
      - `"GUASTATOYA"` = GUASTATOYA
      - `"MORAZAN"` = MORAZAN
      - `"SAN AGUSTIN ACASAGUASTLAN"` = SAN AGUSTIN ACASAGUASTLAN
      - `"SAN ANTONIO LA PAZ"` = SAN ANTONIO LA PAZ
      - `"SAN CRISTOBAL ACASAGUASTLAN"` = SAN CRISTOBAL ACASAGUASTLAN
      - `"SANARATE"` = SANARATE
      - `"SANSARE"` = SANSARE

  > **Sub-pregunta** (aparece cuando respuesta = `"EL PROGRESO"`)

    ###### `servicio_de_salud_4`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"ESCUINTLA"`)

    ###### `distrito_municipal_de_salud_dms3`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"ESCUINTLA"` = ESCUINTLA
      - `"GUANAGAZAPA"` = GUANAGAZAPA
      - `"LA DEMOCRACIA"` = LA DEMOCRACIA
      - `"LA GOMERA"` = LA GOMERA
      - `"MASAGUA"` = MASAGUA
      - `"NUEVA CONCEPCION"` = NUEVA CONCEPCION
      - `"PALIN"` = PALIN
      - `"PUERTO IZTAPA"` = PUERTO IZTAPA
      - `"PUERTO SAN JOSE"` = PUERTO SAN JOSE
      - `"SAN VICENTE PACAYA"` = SAN VICENTE PACAYA
      - `"SANTA LUCIA COTZUMALGUAPA"` = SANTA LUCIA COTZUMALGUAPA
      - `"SIPACATE"` = SIPACATE
      - `"SIQUINALA"` = SIQUINALA
      - `"TIQUISATE"` = TIQUISATE

  > **Sub-pregunta** (aparece cuando respuesta = `"ESCUINTLA"`)

    ###### `servicio_de_salud_`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA CENTRAL"`)

    ###### `distrito_municipal_de_salud_dms4`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"BETHANIA"` = BETHANIA
      - `"CENTRO AMERICA"` = CENTRO AMERICA
      - `"EL AMPARO"` = EL AMPARO
      - `"EL PARAISO"` = EL PARAISO
      - `"JUSTO RUFINO BARRIOS"` = JUSTO RUFINO BARRIOS
      - `"SAN RAFAEL"` = SAN RAFAEL LA LAGUNA II
      - `"SANTA ELENA III"` = SANTA ELENA III
      - `"ZONA 1"` = ZONA 1
      - `"ZONA 11"` = ZONA 11
      - `"ZONA 3"` = ZONA 3
      - `"ZONA 5"` = ZONA 5
      - `"ZONA 6"` = ZONA 6

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA CENTRAL"`)

    ###### `servicio_de_salud_5`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA NOR OCCIDENTE"`)

    ###### `distrito_municipal_de_salud_dms5`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CHUARRANCHO"` = CHUARRANCHO
      - `"CIUDAD QUETZAL"` = CIUDAD QUETZAL
      - `"COMUNIDAD"` = COMUNIDAD
      - `"EL MILAGRO"` = EL MILAGRO
      - `"MIXCO"` = MIXCO
      - `"PRIMERO DE JULIO"` = PRIMERO DE JULIO
      - `"SAN JUAN SACATEPEQUEZ"` = SAN JUAN SACATEPEQUEZ
      - `"SAN PEDRO SACATEPEQUEZ"` = SAN PEDRO SACATEPEQUEZ
      - `"SAN RAYMUNDO"` = SAN RAYMUNDO
      - `"SATELITE"` = SATELITE

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA NOR OCCIDENTE"`)

    ###### `servicio_de_salud_6`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA NOR ORIENTE"`)

    ###### `distrito_municipal_de_salud_dms6`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CHINAUTLA"` = CHINAUTLA
      - `"FRAIJANES"` = FRAIJANES
      - `"PALENCIA"` = PALENCIA
      - `"SAN JOSE DEL GOLFO"` = SAN JOSE DEL GOLFO
      - `"SAN JOSE PINULA"` = SAN JOSE PINULA
      - `"SAN PEDRO AYAMPUC"` = SAN PEDRO AYAMPUC
      - `"SANTA CATARINA PINULA"` = SANTA CATARINA PINULA
      - `"TIERRA NUEVA"` = TIERRA NUEVA

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA NOR ORIENTE"`)

    ###### `servicio_de_salud_7`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA SUR"`)

    ###### `distrito_municipal_de_salud_dms7`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"AMATITLAN"` = AMATITLAN
      - `"BOCA DEL MONTE"` = BOCA DEL MONTE
      - `"CIUDAD REAL"` = CIUDAD REAL
      - `"EL MEZQUITAL"` = EL MEZQUITAL
      - `"PERONIA"` = PERONIA
      - `"SAN MIGUEL PETAPA"` = SAN MIGUEL PETAPA
      - `"VILLA CANALES"` = VILLA CANALES
      - `"VILLA NUEVA"` = VILLA NUEVA

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA SUR"`)

    ###### `servicio_de_salud_8`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"HUEHUETENANGO"`)

    ###### `distrito_municipal_de_salud_dms8`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"AGUACATAN"` = AGUACATAN
      - `"BARILLAS"` = BARILLAS
      - `"CHIANTLA"` = CHIANTLA
      - `"COLOTENANGO"` = COLOTENANGO
      - `"CONCEPCION HUISTA"` = CONCEPCION HUISTA
      - `"CUILCO"` = CUILCO
      - `"HUEHUETENANGO NORTE EL CALVARIO"` = HUEHUETENANGO NORTE EL CALVARIO
      - `"HUEHUETENANGO SUR"` = HUEHUETENANGO SUR
      - `"JACALTENANGO"` = JACALTENANGO
      - `"LA DEMOCRACIA"` = LA DEMOCRACIA
      - `"LA LIBERTAD"` = LA LIBERTAD
      - `"MALACATANCITO"` = MALACATANCITO
      - `"NENTON"` = NENTON
      - `"PETATAN"` = PETATAN
      - `"SAN ANTONIO HUISTA"` = SAN ANTONIO HUISTA
      - `"SAN GASPAR IXCHIL"` = SAN GASPAR IXCHIL
      - `"SAN IDELFONSO IXTAHUACAN"` = SAN IDELFONSO IXTAHUACAN
      - `"SAN JUAN ATITAN"` = SAN JUAN ATITAN
      - `"SAN JUAN IXCOY"` = SAN JUAN IXCOY
      - `"SAN MATEO IXTATAN"` = SAN MATEO IXTATAN
      - `"SAN MIGUEL ACATAN"` = SAN MIGUEL ACATAN
      - `"SAN PEDRO NECTA"` = SAN PEDRO NECTA
      - `"SAN RAFAEL LA INDEPENDENCIA"` = SAN RAFAEL LA INDEPENDENCIA
      - `"SAN RAFAEL PETZAL"` = SAN RAFAEL PETZAL
      - `"SAN SEBASTIAN COATAN"` = SAN SEBASTIAN COATAN
      - `"SAN SEBASTIAN HUEHUETENANGO"` = SAN SEBASTIAN HUEHUETENANGO
      - `"SANTA ANA HUISTA"` = SANTA ANA HUISTA
      - `"SANTA BARBARA"` = SANTA BARBARA
      - `"SANTA EULALIA"` = SANTA EULALIA
      - `"SANTIAGO CHIMALTENANGO"` = SANTIAGO CHIMALTENANGO
      - `"SOLOMA"` = SOLOMA
      - `"TECTITAN"` = TECTITAN
      - `"TODOS SANTOS CUCHUMATÁN"` = TODOS SANTOS CUCHUMATÁN
      - `"UNION CANTINIL"` = UNION CANTINIL

  > **Sub-pregunta** (aparece cuando respuesta = `"HUEHUETENANGO"`)

    ###### `servicio_de_salud_9`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"IXCÁN"`)

    ###### `distrito_municipal_de_salud_dms9`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"INGENIEROS"` = INGENIEROS
      - `"PLAYA GRANDE"` = PLAYA GRANDE
      - `"PUEBLO NUEVO"` = PUEBLO NUEVO
      - `"TZETUN"` = TZETUN

  > **Sub-pregunta** (aparece cuando respuesta = `"IXCÁN"`)

    ###### `servicio_de_salud_10`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"IXIL"`)

    ###### `distrito_municipal_de_salud_dms10`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CHAJUL"` = CHAJUL
      - `"NEBAJ"` = NEBAJ
      - `"SAN JUAN COTZAL"` = SAN JUAN COTZAL

  > **Sub-pregunta** (aparece cuando respuesta = `"IXIL"`)

    ###### `servicio_de_salud_11`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"IZABAL"`)

    ###### `distrito_municipal_de_salud_dms11`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"EL ESTOR"` = EL ESTOR
      - `"FRONTERA RIO DULCE"` = FRONTERA RIO DULCE
      - `"LIVINGSTON"` = LIVINGSTON
      - `"LOS AMATES"` = LOS AMATES
      - `"MORALES"` = MORALES
      - `"NAVAJOA"` = NAVAJOA
      - `"PUERTO BARRIOS"` = PUERTO BARRIOS
      - `"SANTO TOMAS DE CASTILLA"` = SANTO TOMAS DE CASTILLA

  > **Sub-pregunta** (aparece cuando respuesta = `"IZABAL"`)

    ###### `servicio_de_salud_12`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"JALAPA"`)

    ###### `distrito_municipal_de_salud_dms12`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"JALAPA"` = JALAPA
      - `"MATAQUESCUINTLA"` = MATAQUESCUINTLA
      - `"MONJAS"` = MONJAS
      - `"SAN CARLOS ALZATATE"` = SAN CARLOS ALZATATE
      - `"SAN LUIS JILOTEPEQUE"` = SAN LUIS JILOTEPEQUE
      - `"SAN MANUEL CHAPARRON"` = SAN MANUEL CHAPARRON
      - `"SAN PEDRO PINULA"` = SAN PEDRO PINULA
      - `"SANYUYO"` = SANYUYO

  > **Sub-pregunta** (aparece cuando respuesta = `"JALAPA"`)

    ###### `servicio_de_salud_13`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"JUTIAPA"`)

    ###### `distrito_municipal_de_salud_dms13`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"AGUA BLANCA"` = AGUA BLANCA
      - `"ASUNCION MITA"` = ASUNCION MITA
      - `"ATESCATEMPA"` = ATESCATEMPA
      - `"CIUDAD PEDRO DE ALVARADO"` = CIUDAD PEDRO DE ALVARADO
      - `"COMAPA"` = COMAPA
      - `"CONGUACO"` = CONGUACO
      - `"EL ADELANTO"` = EL ADELANTO
      - `"EL PROGRESO"` = EL PROGRESO
      - `"JALPATAGUA"` = JALPATAGUA
      - `"JEREZ"` = JEREZ
      - `"JUTIAPA"` = JUTIAPA
      - `"LOS ANONOS"` = LOS ANONOS
      - `"MOYUTA"` = MOYUTA
      - `"PASACO"` = PASACO
      - `"QUEZADA"` = QUEZADA
      - `"SAN JOSE ACATEMPA"` = SAN JOSE ACATEMPA
      - `"SANTA CATARINA MITA"` = SANTA CATARINA MITA
      - `"YUPILTEPEQUE"` = YUPILTEPEQUE
      - `"ZAPOTITLAN"` = ZAPOTITLAN

  > **Sub-pregunta** (aparece cuando respuesta = `"JUTIAPA"`)

    ###### `servicio_de_salud_14`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN NORTE"`)

    ###### `distrito_municipal_de_salud_dms14`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"FLORES"` = FLORES
      - `"MELCHOR DE MENCOS"` = MELCHOR DE MENCOS
      - `"SAN ANDRES"` = SAN ANDRES
      - `"SAN BENITO"` = SAN BENITO
      - `"SAN FRANCISCO"` = SAN FRANCISCO
      - `"SAN JOSE"` = SAN JOSE

  > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN NORTE"`)

    ###### `servicio_de_salud_15`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN SUR OCCIDENTE"`)

    ###### `distrito_municipal_de_salud_dms15`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"EL NARANJO"` = EL NARANJO
      - `"LA LIBERTAD"` = LA LIBERTAD
      - `"LAS CRUCES"` = LAS CRUCES
      - `"NUEVA ESPERANZA"` = NUEVA ESPERANZA
      - `"SAYAXCHE"` = SAYAXCHE
      - `"TIERRA BLANCA"` = TIERRA BLANCA

  > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN SUR OCCIDENTE"`)

    ###### `servicio_de_salud_18`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN SUR ORIENTE"`)

    ###### `distrito_municipal_de_salud_dms16`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CHACTE"` = CHACTE
      - `"DOLORES"` = DOLORES
      - `"EL CHAL"` = EL CHAL
      - `"POPTUN"` = POPTUN
      - `"SAN LUIS"` = SAN LUIS
      - `"SANTA ANA"` = SANTA ANA

  > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN SUR ORIENTE"`)

    ###### `servicio_de_salud_19`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"QUETZALTENANGO"`)

    ###### `distrito_municipal_de_salud_dms17`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"ALMOLONGA"` = ALMOLONGA
      - `"CABRICAN"` = CABRICAN
      - `"CAJOLA"` = CAJOLA
      - `"CANTEL"` = CANTEL
      - `"COATEPEQUE"` = COATEPEQUE
      - `"COLOMBA"` = COLOMBA
      - `"CONCEPCION CHIQUIRICHAPA"` = CONCEPCION CHIQUIRICHAPA
      - `"EL PALMAR"` = EL PALMAR
      - `"FLORES COSTA CUCA"` = FLORES COSTA CUCA
      - `"GENOVA"` = GENOVA
      - `"HUITAN"` = HUITAN
      - `"LA ESPERANZA"` = LA ESPERANZA
      - `"OLINTEPEQUE"` = OLINTEPEQUE
      - `"PALESTINA DE LOS ALTOS"` = PALESTINA DE LOS ALTOS
      - `"QUETZALTENANGO"` = QUETZALTENANGO
      - `"SALCAJA"` = SALCAJA
      - `"SAN CARLOS SIJA"` = SAN CARLOS SIJA
      - `"SAN FRANCISCO LA UNION"` = SAN FRANCISCO LA UNION
      - `"SAN JUAN OSTUNCALCO"` = SAN JUAN OSTUNCALCO
      - `"SAN MARTIN SACATEPEQUEZ"` = SAN MARTIN SACATEPEQUEZ
      - `"SAN MATEO"` = SAN MATEO
      - `"SAN MIGUEL SIGUILA"` = SAN MIGUEL SIGUILA
      - `"SIBILIA"` = SIBILIA
      - `"ZUNIL"` = ZUNIL

  > **Sub-pregunta** (aparece cuando respuesta = `"QUETZALTENANGO"`)

    ###### `servicio_de_salud_20`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"QUICHÉ"`)

    ###### `distrito_municipal_de_salud_dms18`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CANILLA"` = CANILLA
      - `"CHICAMAN"` = CHICAMAN
      - `"CHICHE"` = CHICHE
      - `"CHICHICASTENANGO"` = CHICHICASTENANGO
      - `"CHINIQUE"` = CHINIQUE
      - `"CHUPOL"` = CHUPOL
      - `"CUNEN"` = CUNEN
      - `"JOYABAJ"` = JOYABAJ
      - `"LA PARROQUIA"` = LA PARROQUIA
      - `"LA TAÑA"` = LA TAÑA
      - `"PACHALUM"` = PACHALUM
      - `"PATZITE"` = PATZITE
      - `"SACAPULAS"` = SACAPULAS
      - `"SAN ANDRES SAJCABAJA"` = SAN ANDRES SAJCABAJA
      - `"SAN ANTONIO ILOTENANGO"` = SAN ANTONIO ILOTENANGO
      - `"SAN BARTOLOME JOCOTENANGO"` = SAN BARTOLOME JOCOTENANGO
      - `"SAN PEDRO JOCOPILAS"` = SAN PEDRO JOCOPILAS
      - `"SANTA CRUZ DEL QUICHE"` = SANTA CRUZ DEL QUICHE
      - `"USPANTAN"` = USPANTAN
      - `"ZACUALPA"` = ZACUALPA

  > **Sub-pregunta** (aparece cuando respuesta = `"QUICHÉ"`)

    ###### `servicio_de_salud_22`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"RETALHULEU"`)

    ###### `distrito_municipal_de_salud_dms19`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CABALLO BLANCO"` = CABALLO BLANCO
      - `"CHAMPERICO"` = CHAMPERICO
      - `"EL ASINTAL"` = EL ASINTAL
      - `"LA MAQUINA"` = LA MAQUINA
      - `"NUEVO SAN CARLOS"` = NUEVO SAN CARLOS
      - `"RETALHULEU"` = RETALHULEU
      - `"SAN ANDRES VILLA SECA"` = SAN ANDRES VILLA SECA
      - `"SAN FELIPE"` = SAN FELIPE
      - `"SAN MARTIN ZAPOTITLAN"` = SAN MARTIN ZAPOTITLAN
      - `"SAN SEBASTIAN"` = SAN SEBASTIAN
      - `"SANTA CRUZ MULUA"` = SANTA CRUZ MULUA

  > **Sub-pregunta** (aparece cuando respuesta = `"RETALHULEU"`)

    ###### `servicio_de_salud_23`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SACATEPÉQUEZ"`)

    ###### `distrito_municipal_de_salud_dms20`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"ANTIGUA GUATEMALA"` = ANTIGUA GUATEMALA
      - `"SAN JUAN ALOTENANGO"` = SAN JUAN ALOTENANGO
      - `"SANTIAGO SACATEPEQUEZ"` = SANTIAGO SACATEPEQUEZ
      - `"SUMPANGO"` = SUMPANGO

  > **Sub-pregunta** (aparece cuando respuesta = `"SACATEPÉQUEZ"`)

    ###### `servicio_de_salud_24`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SAN MARCOS"`)

    ###### `distrito_municipal_de_salud_dms21`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"COMITANCILLO"` = COMITANCILLO
      - `"CONCEPCION TUTUAPA"` = CONCEPCION TUTUAPA
      - `"EL QUETZAL"` = EL QUETZAL
      - `"EL RODEO"` = EL RODEO
      - `"EL TUMBADOR"` = EL TUMBADOR
      - `"IXCHIGUAN"` = IXCHIGUAN
      - `"LA BLANCA"` = LA BLANCA
      - `"LA REFORMA"` = LA REFORMA
      - `"MALACATAN"` = MALACATAN
      - `"SAN JOSE OJETENAM"` = SAN JOSE OJETENAM
      - `"SAN LORENZO"` = SAN LORENZO
      - `"SAN MARCOS"` = SAN MARCOS
      - `"SAN MIGUEL IXTAHUACAN"` = SAN MIGUEL IXTAHUACAN
      - `"SAN PABLO"` = SAN PABLO
      - `"SAN PEDRO SACATEPEQUEZ"` = SAN PEDRO SACATEPEQUEZ
      - `"SAN RAFAEL PIE DE LA CUESTA"` = SAN RAFAEL PIE DE LA CUESTA
      - `"SIBINAL"` = SIBINAL
      - `"SIPACAPA"` = SIPACAPA
      - `"TACANA"` = TACANA
      - `"TAJUMULCO"` = TAJUMULCO
      - `"TECUN UMAN"` = TECUN UMAN
      - `"TEJUTLA"` = TEJUTLA

  > **Sub-pregunta** (aparece cuando respuesta = `"SAN MARCOS"`)

    ###### `servicio_de_salud_25`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SANTA ROSA"`)

    ###### `distrito_municipal_de_salud_dms22`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"BARBERENA"` = BARBERENA
      - `"CASILLAS"` = CASILLAS
      - `"CHIQUIMULILLA"` = CHIQUIMULILLA
      - `"CUILAPA"` = CUILAPA
      - `"GUAZACAPAN"` = GUAZACAPAN
      - `"NUEVA SANTA ROSA"` = NUEVA SANTA ROSA
      - `"ORATORIO"` = ORATORIO
      - `"PUEBLO NUEVO VIÑAS"` = PUEBLO NUEVO VIÑAS
      - `"SAN JUAN TECUACO"` = SAN JUAN TECUACO
      - `"SAN RAFAEL LAS FLORES"` = SAN RAFAEL LAS FLORES
      - `"SANTA CRUZ NARANJO"` = SANTA CRUZ NARANJO
      - `"SANTA MARIA IXHUATAN"` = SANTA MARIA IXHUATAN
      - `"SANTA ROSA DE LIMA"` = SANTA ROSA DE LIMA
      - `"TAXISCO"` = TAXISCO

  > **Sub-pregunta** (aparece cuando respuesta = `"SANTA ROSA"`)

    ###### `servicio_de_salud_26`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SOLOLÁ"`)

    ###### `distrito_municipal_de_salud_dms23`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"GUINEALES"` = GUINEALES
      - `"LA CEIBA"` = LA CEIBA
      - `"NAHUALA"` = NAHUALA
      - `"PANAJACHEL"` = PANAJACHEL
      - `"SAN LUCAS TOLIMAN"` = SAN LUCAS TOLIMAN
      - `"SAN PABLO LA LAGUNA"` = SAN PABLO LA LAGUNA
      - `"SAN PEDRO LA LAGUNA"` = SAN PEDRO LA LAGUNA
      - `"SANTA CATARINA IXTAHUACAN"` = SANTA CATARINA IXTAHUACAN
      - `"SANTA LUCIA UTATLAN"` = SANTA LUCIA UTATLAN
      - `"SANTIAGO ATITLAN"` = SANTIAGO ATITLAN
      - `"SOLOLA"` = SOLOLA
      - `"SAN ANTONIO"` = SAN ANTONIO
      - `"SAN ANDRES"` = SAN ANDRES
      - `"SAN JUAN LA LAGUNA"` = SAN JUAN LA LAGUNA
      - `"SANTA CLARA LA LAGUNA"` = SANTA CLARA LA LAGUNA
      - `"XEJUYUP BOCA COSTA DE NAHUALA"` = XEJUYUP BOCA COSTA DE NAHUALA

  > **Sub-pregunta** (aparece cuando respuesta = `"SOLOLÁ"`)

    ###### `servicio_de_salud_27`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SUCHITEPÉQUEZ"`)

    ###### `distrito_municipal_de_salud_dms24`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CHICACAO"` = CHICACAO
      - `"CUYOTENANGO"` = CUYOTENANGO
      - `"LA MAQUINA"` = LA MAQUINA
      - `"MAZATENANGO"` = MAZATENANGO
      - `"PATULUL"` = PATULUL
      - `"PUEBLO NUEVO"` = PUEBLO NUEVO
      - `"RIO BRAVO"` = RIO BRAVO
      - `"SAN ANTONIO"` = SAN ANTONIO
      - `"SAN JOSE EL IDOLO"` = SAN JOSE EL IDOLO
      - `"SAN FRANCISCO ZAPOTITLAN"` = SAN FRANCISCO ZAPOTITLAN
      - `"ZUNILITO"` = ZUNILITO
      - `"SAN LORENZO"` = SAN LORENZO
      - `"SAN GABRIEL"` = SAN GABRIEL
      - `"SAMAYAC"` = SAMAYAC
      - `"SAN PABLO JOCOPILAS"` = SAN PABLO JOCOPILAS
      - `"SANTA BARBARA"` = SANTA BARBARA
      - `"SAN BERNARDINO"` = SAN BERNARDINO
      - `"SAN JUAN BAUTISTA"` = SAN JUAN BAUTISTA
      - `"SAN MIGUEL PANAN"` = SAN MIGUEL PANAN
      - `"SANTO TOMAS LA UNION"` = SANTO TOMAS LA UNION
      - `"SANTO DOMINGO SUCHITEPEQUEZ"` = SANTO DOMINGO SUCHITEPEQUEZ

  > **Sub-pregunta** (aparece cuando respuesta = `"SUCHITEPÉQUEZ"`)

    ###### `servicio_de_salud_28`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"TOTONICAPAN"`)

    ###### `distrito_municipal_de_salud_dms25`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"MOMOSTENANGO"` = MOMOSTENANGO
      - `"SAN ANDRES XECUL"` = SAN ANDRES XECUL
      - `"SAN BARTOLO AGUAS CALIENTES"` = SAN BARTOLO AGUAS CALIENTES
      - `"SAN CRISTOBAL TOTONICAPAN"` = SAN CRISTOBAL TOTONICAPAN
      - `"SAN FRANCISCO EL ALTO"` = SAN FRANCISCO EL ALTO
      - `"SAN VICENTE BUENABAJ"` = SAN VICENTE BUENABAJ
      - `"SANTA LUCIA LA REFORMA"` = SANTA LUCIA LA REFORMA
      - `"SANTA MARIA CHIQUIMULA"` = SANTA MARIA CHIQUIMULA
      - `"TOTONICAPÁN"` = TOTONICAPÁN

  > **Sub-pregunta** (aparece cuando respuesta = `"TOTONICAPAN"`)

    ###### `servicio_de_salud_30`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"ZACAPA"`)

    ###### `distrito_municipal_de_salud_dms26`
    - **Texto**: DISTRITO MUNICIPAL DE SALUD (DMS)
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"CABAÑAS"` = CABAÑAS
      - `"ESTANZUELA"` = ESTANZUELA
      - `"GUALAN"` = GUALAN
      - `"HUITE"` = HUITE
      - `"LA UNION"` = LA UNION
      - `"RIO HONDO"` = RIO HONDO
      - `"SAN DIEGO"` = SAN DIEGO
      - `"SAN JORGE"` = SAN JORGE
      - `"TECULUTAN"` = TECULUTAN
      - `"USUMATLAN"` = USUMATLAN
      - `"ZACAPA"` = ZACAPA

  > **Sub-pregunta** (aparece cuando respuesta = `"ZACAPA"`)

    ###### `servicio_de_salud_31`
    - **Texto**: SERVICIO DE SALUD
    - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `fecha_de_consulta`
  - **Texto**: FECHA DE CONSULTA
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `fecha_de_investigacion_domiciliaria`
  - **Texto**: FECHA DE INVESTIGACIÓN DOMICILIARIA
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `nombre_de_quien_investiga`
  - **Texto**: NOMBRE DE QUIÉN INVESTIGA
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `cargo_de_quien_investiga`
  - **Texto**: CARGO DE QUIÉN INVESTIGA
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `telefono`
  - **Texto**: TELEFONO
  - **Tipo**: Numerico

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `correo_electronico`
  - **Texto**: CORREO ELECTRÓNICO
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `otro_establecimiento`
  - **Texto**: SEGURO SOCIAL O ESTABLECIMIENTO PRIVADO
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"Seguro Social (IGSS)"` = SEGURO SOCIAL (IGSS)
    - `"ESTABLECIMIENTO PRIVADO"` = ESTABLECIMIENTO PRIVADO

  > **Sub-pregunta** (aparece cuando respuesta = `"Seguro Social (IGSS)"`)

    ###### `especifique_establecimiento`
    - **Texto**: ESPECIFIQUE
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"ESTABLECIMIENTO PRIVADO"`)

    ###### `especifique_privado`
    - **Texto**: ESPECIFIQUE
    - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"Fecha de Notificación"`)

  ##### `fuente_de_notificacion_`
  - **Texto**: FUENTE DE NOTIFICACIÓN
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SERVICIO DE SALUD"` = SERVICIO DE SALUD
    - `"LABORATORIO"` = LABORATORIO
    - `"BÚSQUEDA ACTIVA INSTITUCIONAL"` = BÚSQUEDA ACTIVA INSTITUCIONAL
    - `"BÚSQUEDA ACTIVA COMUNITARIA"` = BÚSQUEDA ACTIVA COMUNITARIA
    - `"BÚSQUEDA ACTIVA LABORATORIAL"` = BÚSQUEDA ACTIVA LABORATORIAL
    - `"INVESTIGACIÓN DE CONTACTOS"` = INVESTIGACIÓN DE CONTACTOS
    - `"CASO REPORTADO POR LA COMUNIDAD"` = CASO REPORTADO POR LA COMUNIDAD
    - `"AUTO NOTIFICACIÓN POR NÚMERO GRATUITO"` = AUTO NOTIFICACIÓN POR NÚMERO GRATUITO
    - `"OTRO"` = OTRO

  > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

    ###### `especifique_fuente`
    - **Texto**: ESPECIFIQUE
    - **Tipo**: Texto libre

#### `informacion_del_paciente`
- **Texto**: INFORMACIÓN DEL PACIENTE
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_INFORMACION_DEL_PACIENTE
- **Opciones**:
  - `"DATOS GENERALES"` = DATOS GENERALES

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `codigo_unico_de_identificacion_dpi_pasaporte_otro`
  - **Texto**: CÓDIGO ÚNICO DE IDENTIFICACIÓN (DPI, PASAPORTE, OTRO)

  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"DPI"` = DPI
    - `"PASAPORTE"` = PASAPORTE
    - `"OTRO"` = OTRO

  > **Sub-pregunta** (aparece cuando respuesta = `"DPI"`)

    ###### `no_de_dpi`
    - **Texto**: NO. DE DPI
    - **Tipo**: Numerico

  > **Sub-pregunta** (aparece cuando respuesta = `"PASAPORTE"`)

    ###### `no_de_pasaporte`
    - **Texto**: NO. DE PASAPORTE
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

    ###### `especifique_cui`
    - **Texto**: ESPECIFIQUE
    - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `nombre_del_tutor_`
  - **Texto**: TIENE TUTOR
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `parentesco_`
    - **Texto**: PARENTESCO DEL TUTOR
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `codigo_unico_de_identificacion_dpi_pasaporte_otro_`
    - **Texto**: CODIGO ÚNICO DE IDENTIFICACIÓN DEL TUTOR (DPI, PASAPORTE, OTRO)
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"DPI"` = DPI
      - `"PASAPORTE"` = PASAPORTE
      - `"OTRO"` = OTRO

    > **Sub-pregunta** (aparece cuando respuesta = `"DPI"`)

      ###### `no_de_dpi_`
      - **Texto**: NO. DE DPI
      - **Tipo**: Numerico

    > **Sub-pregunta** (aparece cuando respuesta = `"PASAPORTE"`)

      ###### `no_de_pasaporte_`
      - **Texto**: NO. DE PASAPORTE
      - **Tipo**: Texto libre

    > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

      ###### `especifique_doc`
      - **Texto**: ESPECIFIQUE
      - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `pueblo`
  - **Texto**: PUEBLO
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"LADINO"` = LADINO
    - `"MAYA"` = MAYA
    - `"GARÍFUNA"` = GARÍFUNA
    - `"XINCA"` = XINCA
    - `"DESCONOCIDO"` = DESCONOCIDO

  > **Sub-pregunta** (aparece cuando respuesta = `"MAYA"`)

    ###### `comunidad_linguistica`
    - **Texto**: COMUNIDAD LINGUÍSTICA
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"Achi´"` = Achi´
      - `"Akateka"` = Akateka
      - `"Awakateka"` = Awakateka
      - `"Ch’orti’"` = Ch’orti’
      - `"Chalchiteka"` = Chalchiteka
      - `"Chuj"` = Chuj
      - `"Itza’"` = Itza’
      - `"Ixil"` = Ixil
      - `"Jakalteka"` = Jakalteka
      - `"Kaqchikel"` = Kaqchikel
      - `"K´iche´"` = K´iche´
      - `"Mam"` = Mam
      - `"Mopan"` = Mopan
      - `"Poqomam"` = Poqomam
      - `"Pocomchi’"` = Pocomchi’
      - `"Q’anjob’al"` = Q’anjob’al
      - `"Q'eqchi'"` = Q'eqchi'
      - `"Sakapulteka"` = Sakapulteka
      - `"Sipakapensa"` = Sipakapensa
      - `"Tektiteka"` = Tektiteka
      - `"Tz’utujil"` = Tz’utujil
      - `"Uspanteka"` = Uspanteka
      - `"No indica"` = No indica

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `extranjero_`
  - **Texto**: EXTRANJERO
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `migrante`
  - **Texto**: MIGRANTE
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `ocupacion_`
  - **Texto**: OCUPACIÓN
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `escolaridad_`
  - **Texto**: ESCOLARIDAD
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"NO APLICA"` = NO APLICA
    - `"PRE PRIMARIA"` = PRE PRIMARIA
    - `"PRIMARIA"` = PRIMARIA
    - `"BÁSICOS"` = BÁSICOS
    - `"DIVERSIFICADO"` = DIVERSIFICADO
    - `"UNIVERSIDAD"` = UNIVERSIDAD
    - `"NINGUNO"` = NINGUNO
    - `"OTRO"` = OTRO
    - `"NO INDICA"` = NO INDICA

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `telefono_`
  - **Texto**: TELÉFONO
  - **Tipo**: Numerico

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `pais_de_residencia_`
  - **Texto**: PAÍS DE RESIDENCIA
  - **Tipo**: Respuesta unica
  - **Obligatorio**: SI
  - **Opciones**:
    - `"GUATEMALA"` = GUATEMALA
    - `"OTRO"` = OTRO

  > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA"`)

    ###### `departamento_de_residencia_`
    - **Texto**: DEPARTAMENTO DE RESIDENCIA
    - **Tipo**: Respuesta unica
    - **Obligatorio**: SI
    - **Opciones**:
      - `"ALTA VERAPAZ"` = ALTA VERAPAZ
      - `"BAJA VERAPAZ"` = BAJA VERAPAZ
      - `"CHIMALTENANGO"` = CHIMALTENANGO
      - `"CHIQUIMULA"` = CHIQUIMULA
      - `"EL PROGRESO"` = EL PROGRESO
      - `"ESCUINTLA"` = ESCUINTLA
      - `"GUATEMALA"` = GUATEMALA
      - `"HUEHUETENANGO"` = HUEHUETENANGO
      - `"IZABAL"` = IZABAL
      - `"JALAPA"` = JALAPA
      - `"JUTIAPA"` = JUTIAPA
      - `"PETÉN"` = PETÉN
      - `"QUETZALTENANGO"` = QUETZALTENANGO
      - `"QUICHÉ"` = QUICHÉ
      - `"RETALHULEU"` = RETALHULEU
      - `"SACATEPÉQUEZ"` = SACATEPÉQUEZ
      - `"SAN MARCOS"` = SAN MARCOS
      - `"SANTA ROSA"` = SANTA ROSA
      - `"SOLOLÁ"` = SOLOLÁ
      - `"SUCHITEPÉQUEZ"` = SUCHITEPÉQUEZ
      - `"TOTONICAPÁN"` = TOTONICAPÁN
      - `"ZACAPA"` = ZACAPA

    > **Sub-pregunta** (aparece cuando respuesta = `"ALTA VERAPAZ"`)

      ###### `municipio_de_residencia_`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CAHABON"` = CAHABON

        - `"CHAHAL"` = CHAHAL

        - `"CHISEC"` = CHISEC

        - `"COBAN"` = COBAN

        - `"FRAY BARTOLOME DE LAS CASAS"` = FRAY BARTOLOME DE LAS CASAS

        - `"LA TINTA"` = LA TINTA

        - `"LANQUIN"` = LANQUIN

        - `"PANZOS"` = PANZOS

        - `"RAXRUHA"` = RAXRUHA

        - `"SAN CRISTOBAL VERAPAZ"` = SAN CRISTOBAL VERAPAZ

        - `"SAN JUAN CHAMELCO"` = SAN JUAN CHAMELCO

        - `"SAN PEDRO CARCHA"` = SAN PEDRO CARCHA

        - `"SANTA CRUZ VERAPAZ"` = SANTA CRUZ VERAPAZ

        - `"SENAHU"` = SENAHU

        - `"TACTIC"` = TACTIC

        - `"TAMAHU"` = TAMAHU

        - `"TUCURU"` = TUCURU


    > **Sub-pregunta** (aparece cuando respuesta = `"BAJA VERAPAZ"`)

      ###### `municipio_de_residencia1`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CUBULCO"` = CUBULCO

        - `"EL CHOL"` = EL CHOL

        - `"GRANADOS"` = GRANADOS

        - `"PURULHA"` = PURULHA

        - `"RABINAL"` = RABINAL

        - `"SALAMA"` = SALAMA

        - `"SAN JERONIMO"` = SAN JERONIMO

        - `"SAN MIGUEL CHICAJ"` = SAN MIGUEL CHICAJ


    > **Sub-pregunta** (aparece cuando respuesta = `"CHIMALTENANGO"`)

      ###### `municipio_de_residencia2`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"ACATENANGO"` = ACATENANGO
        - `"CHIMALTENANGO"` = CHIMALTENANGO
        - `"EL TEJAR"` = EL TEJAR
        - `"PARRAMOS"` = PARRAMOS

        - `"PATZICIA"` = PATZICIA

        - `"PATZUN"` = PATZUN

        - `"POCHUTA"` = POCHUTA

        - `"SAN ANDRES ITZAPA"` = SAN ANDRES ITZAPA

        - `"SAN JOSE POAQUIL"` = SAN JOSE POAQUIL

        - `"SAN JUAN COMALAPA"` = SAN JUAN COMALAPA

        - `"SAN MARTIN JILOTEPEQUE"` = SAN MARTIN JILOTEPEQUE

        - `"SANTA APOLONIA"` = SANTA APOLONIA

        - `"SANTA CRUZ BALANYA"` = SANTA CRUZ BALANYA

        - `"TECPAN GUATEMALA"` = TECPAN GUATEMALA

        - `"YEPOCAPA"` = YEPOCAPA

        - `"ZARAGOZA"` = ZARAGOZA


    > **Sub-pregunta** (aparece cuando respuesta = `"CHIQUIMULA"`)

      ###### `municipio_de_residencia3`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CAMOTAN"` = CAMOTAN

        - `"CHIQUIMULA"` = CHIQUIMULA

        - `"CONCEPCION LAS MINAS"` = CONCEPCION LAS MINAS

        - `"ESQUIPULAS"` = ESQUIPULAS

        - `"IPALA"` = IPALA

        - `"JOCOTAN"` = JOCOTAN

        - `"OLOPA"` = OLOPA

        - `"QUETZALTEPEQUE"` = QUETZALTEPEQUE

        - `"SAN JACINTO"` = SAN JACINTO

        - `"SAN JOSE LA ARADA"` = SAN JOSE LA ARADA

        - `"SAN JUAN LA ERMITA"` = SAN JUAN LA ERMITA


    > **Sub-pregunta** (aparece cuando respuesta = `"EL PROGRESO"`)

      ###### `municipio_de_residencia4`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"EL JICARO"` = EL JICARO

        - `"GUASTATOYA"` = GUASTATOYA

        - `"MORAZAN"` = MORAZAN

        - `"SAN AGUSTIN ACASAGUASTLAN"` = SAN AGUSTIN ACASAGUASTLAN

        - `"SAN ANTONIO LA PAZ"` = SAN ANTONIO LA PAZ

        - `"SAN CRISTOBAL ACASAGUASTLAN"` = SAN CRISTOBAL ACASAGUASTLAN

        - `"SANARATE"` = SANARATE

        - `"SANSARE"` = SANSARE


    > **Sub-pregunta** (aparece cuando respuesta = `"ESCUINTLA"`)

      ###### `municipio_de_residencia5`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"ESCUINTLA"` = ESCUINTLA

        - `"GUANAGAZAPA"` = GUANAGAZAPA

        - `"IZTAPA"` = IZTAPA

        - `"LA DEMOCRACIA"` = LA DEMOCRACIA

        - `"LA GOMERA"` = LA GOMERA

        - `"MASAGUA"` = MASAGUA

        - `"NUEVA CONCEPCION"` = NUEVA CONCEPCION

        - `"PALIN"` = PALIN

        - `"PUERTO DE SAN JOSE"` = PUERTO DE SAN JOSE

        - `"SAN VICENTE PACAYA"` = SAN VICENTE PACAYA

        - `"SANTA LUCIA COTZUMALGUAPA"` = SANTA LUCIA COTZUMALGUAPA

        - `"SIPACATE"` = SIPACATE

        - `"SIQUINALA"` = SIQUINALA

        - `"TIQUISATE"` = TIQUISATE


    > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA"`)

      ###### `municipio_de_residencia6`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"AMATITLAN"` = AMATITLAN

        - `"CHINAUTLA"` = CHINAUTLA

        - `"CHUARRANCHO"` = CHUARRANCHO

        - `"FRAIJANES"` = FRAIJANES

        - `"GUATEMALA"` = GUATEMALA

        - `"MIXCO"` = MIXCO

        - `"PALENCIA"` = PALENCIA

        - `"SAN JOSE DEL GOLFO"` = SAN JOSE DEL GOLFO

        - `"SAN JOSE PINULA"` = SAN JOSE PINULA

        - `"SAN JUAN SACATEPEQUEZ"` = SAN JUAN SACATEPEQUEZ

        - `"SAN MIGUEL PETAPA"` = SAN MIGUEL PETAPA

        - `"SAN PEDRO AYAMPUC"` = SAN PEDRO AYAMPUC

        - `"SAN PEDRO SACATEPEQUEZ"` = SAN PEDRO SACATEPEQUEZ

        - `"SAN RAYMUNDO"` = SAN RAYMUNDO

        - `"SANTA CATARINA PINULA"` = SANTA CATARINA PINULA

        - `"VILLA CANALES"` = VILLA CANALES

        - `"VILLA NUEVA"` = VILLA NUEVA


    > **Sub-pregunta** (aparece cuando respuesta = `"HUEHUETENANGO"`)

      ###### `municipio_de_residencia7`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"AGUACATAN"` = AGUACATAN

        - `"BARILLAS"` = BARILLAS

        - `"CHIANTLA"` = CHIANTLA

        - `"COLOTENANGO"` = COLOTENANGO

        - `"CONCEPCION HUISTA"` = CONCEPCION HUISTA

        - `"CUILCO"` = CUILCO

        - `"HUEHUETENANGO"` = HUEHUETENANGO

        - `"IXTAHUACAN"` = IXTAHUACAN

        - `"JACALTENANGO"` = JACALTENANGO

        - `"LA DEMOCRACIA"` = LA DEMOCRACIA

        - `"LA LIBERTAD"` = LA LIBERTAD

        - `"MALACATANCITO"` = MALACATANCITO

        - `"NENTON"` = NENTON

        - `"PETATAN"` = PETATAN

        - `"SAN ANTONIO HUISTA"` = SAN ANTONIO HUISTA

        - `"SAN GASPAR IXCHIL"` = SAN GASPAR IXCHIL

        - `"SAN JUAN ATITAN"` = SAN JUAN ATITAN

        - `"SAN JUAN IXCOY"` = SAN JUAN IXCOY

        - `"SAN MATEO IXTATAN"` = SAN MATEO IXTATAN

        - `"SAN MIGUEL ACATAN"` = SAN MIGUEL ACATAN

        - `"SAN PEDRO NECTA"` = SAN PEDRO NECTA

        - `"SAN PEDRO SOLOMA"` = SAN PEDRO SOLOMA

        - `"SAN RAFAEL LA INDEPENDENCIA"` = SAN RAFAEL LA INDEPENDENCIA

        - `"SAN RAFAEL PETZAL"` = SAN RAFAEL PETZAL

        - `"SAN SEBASTIAN COATAN"` = SAN SEBASTIAN COATAN

        - `"SAN SEBASTIAN HUEHUETENANGO"` = SAN SEBASTIAN HUEHUETENANGO

        - `"SANTA ANA HUISTA"` = SANTA ANA HUISTA

        - `"SANTA BARBARA"` = SANTA BARBARA

        - `"SANTA EULALIA"` = SANTA EULALIA

        - `"SANTIAGO CHIMALTENANGO"` = SANTIAGO CHIMALTENANGO

        - `"TECTITAN"` = TECTITAN

        - `"TODOS SANTOS CUCHUMATAN"` = TODOS SANTOS CUCHUMATAN

        - `"UNION CANTINIL"` = UNION CANTINIL


    > **Sub-pregunta** (aparece cuando respuesta = `"IZABAL"`)

      ###### `municipio_de_residencia8`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"EL ESTOR"` = EL ESTOR

        - `"LIVINGSTON"` = LIVINGSTON

        - `"LOS AMATES"` = LOS AMATES

        - `"MORALES"` = MORALES

        - `"PUERTO BARRIOS"` = PUERTO BARRIOS


    > **Sub-pregunta** (aparece cuando respuesta = `"JALAPA"`)

      ###### `municipio_de_residencia9`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"JALAPA"` = JALAPA

        - `"MATAQUESCUINTLA"` = MATAQUESCUINTLA

        - `"MONJAS"` = MONJAS

        - `"SAN CARLOS ALZATATE"` = SAN CARLOS ALZATATE

        - `"SAN LUIS JILOTEPEQUE"` = SAN LUIS JILOTEPEQUE

        - `"SAN MANUEL CHAPARRON"` = SAN MANUEL CHAPARRON

        - `"SAN PEDRO PINULA"` = SAN PEDRO PINULA


    > **Sub-pregunta** (aparece cuando respuesta = `"JUTIAPA"`)

      ###### `municipio_de_residencia10`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"AGUA BLANCA"` = AGUA BLANCA

        - `"ASUNCION MITA"` = ASUNCION MITA

        - `"ATESCATEMPA"` = ATESCATEMPA

        - `"COMAPA"` = COMAPA

        - `"CONGUACO"` = CONGUACO

        - `"EL ADELANTO"` = EL ADELANTO

        - `"EL PROGRESO"` = EL PROGRESO

        - `"JALPATAGUA"` = JALPATAGUA

        - `"JEREZ"` = JEREZ

        - `"JUTIAPA"` = JUTIAPA

        - `"MOYUTA"` = MOYUTA

        - `"PASACO"` = PASACO

        - `"QUESADA"` = QUESADA

        - `"SAN JOSE ACATEMPA"` = SAN JOSE ACATEMPA

        - `"SANTA CATARINA MITA"` = SANTA CATARINA MITA

        - `"YUPILTEPEQUE"` = YUPILTEPEQUE

        - `"ZAPOTITLAN"` = ZAPOTITLAN


    > **Sub-pregunta** (aparece cuando respuesta = `"PETÉN"`)

      ###### `municipio_de_residencia11`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"DOLORES"` = DOLORES

        - `"EL CHAL"` = EL CHAL

        - `"FLORES"` = FLORES

        - `"LA LIBERTAD"` = LA LIBERTAD

        - `"LAS CRUCES"` = LAS CRUCES

        - `"MELCHOR DE MENCOS"` = MELCHOR DE MENCOS

        - `"POPTUN"` = POPTUN

        - `"SAN ANDRES"` = SAN ANDRES

        - `"SAN BENITO"` = SAN BENITO

        - `"SAN FRANCISCO"` = SAN FRANCISCO

        - `"SAN JOSE"` = SAN JOSE

        - `"SAN LUIS"` = SAN LUIS

        - `"SANTA ANA"` = SANTA ANA

        - `"SAYAXCHE"` = SAYAXCHE


    > **Sub-pregunta** (aparece cuando respuesta = `"QUETZALTENANGO"`)

      ###### `municipio_de_residencia12`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"ALMOLONGA"` = ALMOLONGA

        - `"CABRICAN"` = CABRICAN

        - `"CAJOLA"` = CAJOLA

        - `"CANTEL"` = CANTEL

        - `"COATEPEQUE"` = COATEPEQUE

        - `"COLOMBA"` = COLOMBA

        - `"CONCEPCION CHIQUIRICHAPA"` = CONCEPCION CHIQUIRICHAPA

        - `"EL PALMAR"` = EL PALMAR

        - `"FLORES COSTA CUCA"` = FLORES COSTA CUCA

        - `"GENOVA"` = GENOVA

        - `"HUITAN"` = HUITAN

        - `"LA ESPERANZA"` = LA ESPERANZA

        - `"OLINTEPEQUE"` = OLINTEPEQUE

        - `"PALESTINA DE LOS ALTOS"` = PALESTINA DE LOS ALTOS

        - `"QUETZALTENANGO"` = QUETZALTENANGO

        - `"SALCAJA"` = SALCAJA

        - `"SAN CARLOS SIJA"` = SAN CARLOS SIJA

        - `"SAN FRANCISCO LA UNION"` = SAN FRANCISCO LA UNION

        - `"SAN JUAN OSTUNCALCO"` = SAN JUAN OSTUNCALCO

        - `"SAN MARTIN SACATEPEQUEZ"` = SAN MARTIN SACATEPEQUEZ

        - `"SAN MATEO"` = SAN MATEO

        - `"SAN MIGUEL SIGÜILA"` = SAN MIGUEL SIGÜILA

        - `"SIBILIA"` = SIBILIA

        - `"ZUNIL"` = ZUNIL


    > **Sub-pregunta** (aparece cuando respuesta = `"QUICHÉ"`)

      ###### `municipio_de_residencia13`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CANILLA"` = CANILLA

        - `"CHAJUL"` = CHAJUL

        - `"CHICAMAN"` = CHICAMAN

        - `"CHICHE"` = CHICHE

        - `"CHICHICASTENANGO"` = CHICHICASTENANGO

        - `"CHINIQUE"` = CHINIQUE

        - `"CUNEN"` = CUNEN

        - `"IXCAN"` = IXCAN

        - `"JOYABAJ"` = JOYABAJ

        - `"NEBAJ"` = NEBAJ

        - `"PACHALUN"` = PACHALUN

        - `"PATZITE"` = PATZITE

        - `"SACAPULAS"` = SACAPULAS

        - `"SAN ANDRES SAJCABAJA"` = SAN ANDRES SAJCABAJA

        - `"SAN ANTONIO ILOTENANGO"` = SAN ANTONIO ILOTENANGO

        - `"SAN BARTOLOME JOCOTENANGO"` = SAN BARTOLOME JOCOTENANGO

        - `"SAN JUAN COTZAL"` = SAN JUAN COTZAL

        - `"SAN MIGUEL USPANTAN"` = SAN MIGUEL USPANTAN

        - `"SAN PEDRO JOCOPILAS"` = SAN PEDRO JOCOPILAS

        - `"SANTA CRUZ DEL QUICHE"` = SANTA CRUZ DEL QUICHE

        - `"ZACUALPA"` = ZACUALPA


    > **Sub-pregunta** (aparece cuando respuesta = `"RETALHULEU"`)

      ###### `municipio_de_residencia14`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CHAMPERICO"` = CHAMPERICO

        - `"EL ASINTAL"` = EL ASINTAL

        - `"NUEVO SAN CARLOS"` = NUEVO SAN CARLOS

        - `"RETALHULEU"` = RETALHULEU

        - `"SAN ANDRES VILLA SECA"` = SAN ANDRES VILLA SECA

        - `"SAN FELIPE"` = SAN FELIPE

        - `"SAN MARTIN ZAPOTITLAN"` = SAN MARTIN ZAPOTITLAN

        - `"SAN SEBASTIAN"` = SAN SEBASTIAN

        - `"SANTA CRUZ MULUA"` = SANTA CRUZ MULUA


    > **Sub-pregunta** (aparece cuando respuesta = `"SACATEPÉQUEZ"`)

      ###### `municipio_de_residencia15`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"ALOTENANGO"` = ALOTENANGO

        - `"ANTIGUA GUATEMALA"` = ANTIGUA GUATEMALA

        - `"CIUDAD VIEJA"` = CIUDAD VIEJA

        - `"JOCOTENANGO"` = JOCOTENANGO

        - `"MAGDALENA MILPAS ALTAS"` = MAGDALENA MILPAS ALTAS

        - `"PASTORES"` = PASTORES

        - `"SAN ANTONIO AGUAS CALIENTES"` = SAN ANTONIO AGUAS CALIENTES

        - `"SAN BARTOLOME MILPAS ALTAS"` = SAN BARTOLOME MILPAS ALTAS

        - `"SAN LUCAS SACATEPEQUEZ"` = SAN LUCAS SACATEPEQUEZ

        - `"SAN MIGUEL DUEÑAS"` = SAN MIGUEL DUEÑAS

        - `"SANTA CATARINA BARAHONA"` = SANTA CATARINA BARAHONA

        - `"SANTA LUCIA MILPAS ALTAS"` = SANTA LUCIA MILPAS ALTAS

        - `"SANTA MARIA DE JESUS"` = SANTA MARIA DE JESUS

        - `"SANTIAGO SACATEPEQUEZ"` = SANTIAGO SACATEPEQUEZ

        - `"SANTO DOMINGO XENACOJ"` = SANTO DOMINGO XENACOJ

        - `"SUMPANGO"` = SUMPANGO


    > **Sub-pregunta** (aparece cuando respuesta = `"SAN MARCOS"`)

      ###### `municipio_de_residencia16`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"AYUTLA"` = AYUTLA

        - `"CATARINA"` = CATARINA

        - `"COMITANCILLO"` = COMITANCILLO

        - `"CONCEPCION TUTUAPA"` = CONCEPCION TUTUAPA

        - `"EL QUETZAL"` = EL QUETZAL

        - `"EL RODEO"` = EL RODEO

        - `"EL TUMBADOR"` = EL TUMBADOR

        - `"ESQUIPULAS PALO GORDO"` = ESQUIPULAS PALO GORDO

        - `"IXCHIGUAN"` = IXCHIGUAN

        - `"LA BLANCA"` = LA BLANCA

        - `"LA REFORMA"` = LA REFORMA

        - `"MALACATAN"` = MALACATAN

        - `"NUEVO PROGRESO"` = NUEVO PROGRESO

        - `"OCOS"` = OCOS

        - `"PAJAPITA"` = PAJAPITA

        - `"RIO BLANCO"` = RIO BLANCO

        - `"SAN ANTONIO SACATEPEQUEZ"` = SAN ANTONIO SACATEPEQUEZ

        - `"SAN CRISTOBAL CUCHO"` = SAN CRISTOBAL CUCHO

        - `"SAN JOSE OJETENAM"` = SAN JOSE OJETENAM

        - `"SAN LORENZO"` = SAN LORENZO

        - `"SAN MARCOS"` = SAN MARCOS

        - `"SAN MIGUEL IXTAHUACAN"` = SAN MIGUEL IXTAHUACAN

        - `"SAN PABLO"` = SAN PABLO

        - `"SAN PEDRO SACATEPEQUEZ"` = SAN PEDRO SACATEPEQUEZ

        - `"SAN RAFAEL PIE DE LA CUESTA"` = SAN RAFAEL PIE DE LA CUESTA

        - `"SIBINAL"` = SIBINAL

        - `"SIPACAPA"` = SIPACAPA

        - `"TACANA"` = TACANA

        - `"TAJUMULCO"` = TAJUMULCO

        - `"TEJUTLA"` = TEJUTLA


    > **Sub-pregunta** (aparece cuando respuesta = `"SANTA ROSA"`)

      ###### `municipio_de_residencia17`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"BARBERENA"` = BARBERENA

        - `"CASILLAS"` = CASILLAS

        - `"CHIQUIMULILLA"` = CHIQUIMULILLA

        - `"CUILAPA"` = CUILAPA

        - `"GUAZACAPAN"` = GUAZACAPAN

        - `"NUEVA SANTA ROSA"` = NUEVA SANTA ROSA

        - `"ORATORIO"` = ORATORIO

        - `"PUEBLO NUEVO VIÑAS"` = PUEBLO NUEVO VIÑAS

        - `"SAN JUAN TECUACO"` = SAN JUAN TECUACO

        - `"SAN RAFAEL LAS FLORES"` = SAN RAFAEL LAS FLORES

        - `"SANTA CRUZ NARANJO"` = SANTA CRUZ NARANJO

        - `"SANTA MARIA IXHUATAN"` = SANTA MARIA IXHUATAN

        - `"SANTA ROSA DE LIMA"` = SANTA ROSA DE LIMA

        - `"TAXISCO"` = TAXISCO


    > **Sub-pregunta** (aparece cuando respuesta = `"SOLOLÁ"`)

      ###### `municipio_de_residencia18`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CONCEPCION"` = CONCEPCION

        - `"NAHUALA"` = NAHUALA

        - `"PANAJACHEL"` = PANAJACHEL

        - `"SAN ANDRES SEMETABAJ"` = SAN ANDRES SEMETABAJ

        - `"SAN ANTONIO PALOPO"` = SAN ANTONIO PALOPO

        - `"SAN JOSE CHACAYA"` = SAN JOSE CHACAYA

        - `"SAN JUAN LA LAGUNA"` = SAN JUAN LA LAGUNA

        - `"SAN LUCAS TOLIMAN"` = SAN LUCAS TOLIMAN

        - `"SAN MARCOS LA LAGUNA"` = SAN MARCOS LA LAGUNA

        - `"SAN PABLO LA LAGUNA"` = SAN PABLO LA LAGUNA

        - `"SAN PEDRO LA LAGUNA"` = SAN PEDRO LA LAGUNA

        - `"SANTA CATARINA IXTAHUACAN"` = SANTA CATARINA IXTAHUACAN

        - `"SANTA CATARINA PALOPO"` = SANTA CATARINA PALOPO

        - `"SANTA CLARA LA LAGUNA"` = SANTA CLARA LA LAGUNA

        - `"SANTA CRUZ LA LAGUNA"` = SANTA CRUZ LA LAGUNA

        - `"SANTA LUCIA UTATLAN"` = SANTA LUCIA UTATLAN

        - `"SANTA MARIA VISITACION"` = SANTA MARIA VISITACION

        - `"SANTIAGO ATITLAN"` = SANTIAGO ATITLAN

        - `"SOLOLA"` = SOLOLA


    > **Sub-pregunta** (aparece cuando respuesta = `"SUCHITEPÉQUEZ"`)

      ###### `municipio_de_residencia19`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CHICACAO"` = CHICACAO

        - `"CUYOTENANGO"` = CUYOTENANGO

        - `"MAZATENANGO"` = MAZATENANGO

        - `"PATULUL"` = PATULUL

        - `"PUEBLO NUEVO"` = PUEBLO NUEVO

        - `"RIO BRAVO"` = RIO BRAVO

        - `"SAMAYAC"` = SAMAYAC

        - `"SAN ANTONIO SUCHITEPEQUEZ"` = SAN ANTONIO SUCHITEPEQUEZ

        - `"SAN BERNARDINO"` = SAN BERNARDINO

        - `"SAN FRANCISCO ZAPOTITLAN"` = SAN FRANCISCO ZAPOTITLAN

        - `"SAN GABRIEL"` = SAN GABRIEL

        - `"SAN JOSE EL IDOLO"` = SAN JOSE EL IDOLO

        - `"SAN JOSE LA MAQUINA"` = SAN JOSE LA MAQUINA

        - `"SAN JUAN BAUTISTA"` = SAN JUAN BAUTISTA

        - `"SAN LORENZO"` = SAN LORENZO

        - `"SAN MIGUEL PANAN"` = SAN MIGUEL PANAN

        - `"SAN PABLO JOCOPILAS"` = SAN PABLO JOCOPILAS

        - `"SANTA BARBARA"` = SANTA BARBARA

        - `"SANTO DOMINGO SUCHITEPEQUEZ"` = SANTO DOMINGO SUCHITEPEQUEZ

        - `"SANTO TOMAS LA UNION"` = SANTO TOMAS LA UNION

        - `"ZUNILITO"` = ZUNILITO


    > **Sub-pregunta** (aparece cuando respuesta = `"TOTONICAPÁN"`)

      ###### `municipio_de_residencia20`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"MOMOSTENANGO"` = MOMOSTENANGO

        - `"SAN ANDRES XECUL"` = SAN ANDRES XECUL

        - `"SAN BARTOLO"` = SAN BARTOLO

        - `"SAN CRISTOBAL TOTONICAPAN"` = SAN CRISTOBAL TOTONICAPAN

        - `"SAN FRANCISCO EL ALTO"` = SAN FRANCISCO EL ALTO

        - `"SANTA LUCIA LA REFORMA"` = SANTA LUCIA LA REFORMA

        - `"SANTA MARIA CHIQUIMULA"` = SANTA MARIA CHIQUIMULA

        - `"TOTONICAPAN"` = TOTONICAPAN


    > **Sub-pregunta** (aparece cuando respuesta = `"ZACAPA"`)

      ###### `municipio_de_residencia21`
      - **Texto**: MUNICIPIO DE RESIDENCIA
      - **Tipo**: Respuesta unica
      - **Obligatorio**: SI
      - **Opciones**:
        - `"CABAÑAS"` = CABAÑAS

        - `"ESTANZUELA"` = ESTANZUELA

        - `"GUALAN"` = GUALAN

        - `"HUITE"` = HUITE

        - `"LA UNION"` = LA UNION

        - `"RIO HONDO"` = RIO HONDO

        - `"SAN DIEGO"` = SAN DIEGO

        - `"SAN JORGE"` = SAN JORGE

        - `"TECULUTAN"` = TECULUTAN

        - `"USUMATLAN"` = USUMATLAN

        - `"ZACAPA"` = ZACAPA


  > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

    ###### `especifique_pais`
    - **Texto**: ESPECIFIQUE
    - **Tipo**: Texto libre
    - **Obligatorio**: SI

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `direccion_de_residencia_`
  - **Texto**: DIRECCIÓN DE RESIDENCIA
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS GENERALES"`)

  ##### `lugar_poblado_`
  - **Texto**: LUGAR POBLADO
  - **Tipo**: Texto libre

#### `antecedentes_medicos_y_de_vacunacion`
- **Texto**: ANTECEDENTES MÉDICOS Y DE VACUNACIÓN
- **Tipo**: Respuesta unica
- **Obligatorio**: SI
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION
- **Opciones**:
  - `"ANTECEDENTES MEDICOS Y DE VACUNACIÓN"` = ANTECEDENTES MEDICOS Y DE VACUNACIÓN

> **Sub-pregunta** (aparece cuando respuesta = `"ANTECEDENTES MEDICOS Y DE VACUNACIÓN"`)

  ##### `paciente_vacunado_`
  - **Texto**: PACIENTE VACUNADO
  - **Tipo**: Respuesta unica
  - **Obligatorio**: SI
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO
    - `" VERBAL"` = VERBAL
    - `"DESCONOCIDO"` = DESCONOCIDO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `tipo_de_vacuna_recibida_`
    - **Texto**: TIPO DE VACUNA RECIBIDA
    - **Tipo**: Respuesta multiple
    - **Opciones**:
      - `"SPR – Sarampión Paperas Rubéola"` = SPR – Sarampión Paperas Rubéola
      - `"SR – Sarampión Rubéola"` = SR – Sarampión Rubéola

    > **Sub-pregunta** (aparece cuando respuesta = `"SPR – Sarampión Paperas Rubéola"`)

      ###### `numero_de_dosis`
      - **Texto**: Número De Dosis
      - **Tipo**: Numerico

    > **Sub-pregunta** (aparece cuando respuesta = `"SPR – Sarampión Paperas Rubéola"`)

      ###### `fecha_de_la_ultima_dosis`
      - **Texto**: Fecha De La Última Dosis
      - **Tipo**: Fecha/Hora

    > **Sub-pregunta** (aparece cuando respuesta = `"SR – Sarampión Rubéola"`)

      ###### `numero_de_dosis_`
      - **Texto**: Número De Dosis
      - **Tipo**: Numerico

    > **Sub-pregunta** (aparece cuando respuesta = `"SR – Sarampión Rubéola"`)

      ###### `fecha_de_la_ultima_dosis_`
      - **Texto**: Fecha De La Última Dosis
      - **Tipo**: Fecha/Hora

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `fuente_de_la_informacion_sobre_la_vacunacion_`
    - **Texto**: FUENTE DE LA INFORMACIÓN SOBRE LA VACUNACIÓN
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"CARNÉ DE VACUNACIÓN"` = CARNÉ DE VACUNACIÓN
      - `"SIGSA 5A CUADERNO"` = SIGSA 5A CUADERNO
      - `"SIGSA 5B OTROS GRUPOS"` = SIGSA 5B OTROS GRUPOS
      - `"REGISTRO ÚNICO DE VACUNACIÓN"` = REGISTRO ÚNICO DE VACUNACIÓN

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `vacunacion_en_el_sector_`
    - **Texto**: VACUNACIÓN EN EL SECTOR
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"MSPAS"` = MSPAS
      - `"IGSS"` = IGSS
      - `"PRIVADO"` = PRIVADO

> **Sub-pregunta** (aparece cuando respuesta = `"ANTECEDENTES MEDICOS Y DE VACUNACIÓN"`)

  ##### `antecedentes_medicos_`
  - **Texto**: ANTECEDENTES MÉDICOS
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO
    - `"DESCONOCIDO"` = DESCONOCIDO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `especifique_ant`
    - **Texto**: ESPECIFIQUE
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"DESNUTRICIÓN"` = DESNUTRICIÓN
      - `"INMUNOCOMPROMISO"` = INMUNOCOMPROMISO
      - `"ENFERMEDAD CRÓNICA"` = ENFERMEDAD CRÓNICA
      - `"OTRO"` = OTRO

    > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

      ###### `especifique_A`
      - **Texto**: ESPECIFIQUE
      - **Tipo**: Texto libre

#### `datos_clinicos`
- **Texto**: DATOS CLÍNICOS
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_DATOS_CLINICOS
- **Opciones**:
  - `"DATOS CLÍNICOS"` = DATOS CLÍNICOS

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `fecha_de_inicio_de_sintomas_`
  - **Texto**: FECHA DE INICIO DE SÍNTOMAS
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `fecha_de_inicio_de_fiebre_`
  - **Texto**: FECHA DE INICIO DE FIEBRE
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `fecha_de_inicio_de_exantema_rash_`
  - **Texto**: FECHA DE INICIO DE EXANTEMA / RASH
  - **Tipo**: Fecha/Hora
  - **Obligatorio**: SI

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `sintomas_`
  - **Texto**: SÍNTOMAS
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `que_sintomas_`
    - **Texto**: ¿QUE SÍNTOMAS?
    - **Tipo**: Respuesta multiple
    - **Opciones**:
      - `"Fiebre"` = Fiebre
      - `"Coriza / Catarro"` = Coriza / Catarro
      - `"Exantema/ Rash"` = Exantema/ Rash
      - `"Manchas de Koplik"` = Manchas de Koplik
      - `"Tos"` = Tos
      - `"Artralgia / Artritis"` = Artralgia / Artritis
      - `"Conjuntivitis"` = Conjuntivitis
      - `"Adenopatías"` = Adenopatías

    > **Sub-pregunta** (aparece cuando respuesta = `"Fiebre"`)

      ###### `temp_c`
      - **Texto**: Fiebre (Temp. C°)
      - **Tipo**: Numerico

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `hospitalizacion_`
  - **Texto**: HOSPITALIZACIÓN
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO
    - `"DESCONOCIDO"` = DESCONOCIDO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `nombre_del_hospital_`
    - **Texto**: NOMBRE DEL HOSPITAL
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `fecha_de_hospitalizacion_`
    - **Texto**: FECHA DE HOSPITALIZACIÓN
    - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `complicaciones_`
  - **Texto**: COMPLICACIONES
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO
    - `"DESCONOCIDO"` = DESCONOCIDO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `especifique_complicaciones_`
    - **Texto**: ESPECIFIQUE COMPLICACIONES
    - **Tipo**: Respuesta multiple
    - **Opciones**:
      - `"NEUMONÍA"` = NEUMONÍA
      - `"ENCEFALITIS"` = ENCEFALITIS
      - `"DIARREA"` = DIARREA
      - `"TROMBOCITOPENIA"` = TROMBOCITOPENIA
      - `"OTITIS MEDIA AGUDA"` = OTITIS MEDIA AGUDA
      - `"CEGUERA"` = CEGUERA
      - `"OTRA"` = OTRA

    > **Sub-pregunta** (aparece cuando respuesta = `"OTRA"`)

      ###### `especique`
      - **Texto**:  (ESPECIQUE)
      - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"DATOS CLÍNICOS"`)

  ##### `aislamiento_respiratorio`
  - **Texto**: AISLAMIENTO RESPIRATORIO
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO
    - `"DESCONOCIDO"` = DESCONOCIDO

  > **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

    ###### `fecha_de_aislamiento`
    - **Texto**: FECHA DE AISLAMIENTO
    - **Tipo**: Fecha/Hora

#### `factores_de_riesgo`
- **Texto**: FACTORES DE RIESGO
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_EXPOSURE_RISK
- **Opciones**:
  - `"Si"` = Si
  - `"No"` = No
  - `"DESCONOCIDO"` = DESCONOCIDO

> **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

  ##### `Existe_caso_en_muni`
  - **Texto**: EXISTE ALGÚN CASO CONFIRMADO EN LA COMUNIDAD O MUNICIPIO DE RESIDENCIA
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"Si"` = Si
    - `"No"` = No
    - `"Desconocido"` = Desconocido

> **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

  ##### `tuvo_contacto_con_un_caso_sospechoso_o_confirmado`
  - **Texto**: TUVO CONTACTO CON UN CASO SOSPECHOSO O CONFIRMADO ENTRE 7-23 DÍAS ANTES DEL INICIO DEL EXANTEMA/RASH
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"Si"` = Si
    - `"No"` = No
    - `"Desconocido"` = Desconocido

> **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

  ##### `viajo_durante_los_7_23_dias`
  - **Texto**: VIAJÓ DURANTE LOS 7-23 DÍAS PREVIOS AL INICIO DEL EXANTEMA O RASH
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"Si"` = Si
    - `"No"` = No

  > **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

    ###### `pais_departamento_y_municipio`
    - **Texto**: PAÍS
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"GUATEMALA"` = GUATEMALA
      - `"OTRO"` = OTRO

    > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA"`)

      ###### `departamento`
      - **Texto**: DEPARTAMENTO
      - **Tipo**: Respuesta unica
      - **Opciones**:
        - `"ALTA VERAPAZ"` = ALTA VERAPAZ
        - `"BAJA VERAPAZ"` = BAJA VERAPAZ
        - `"CHIMALTENANGO"` = CHIMALTENANGO
        - `"CHIQUIMULA"` = CHIQUIMULA
        - `"EL PROGRESO"` = EL PROGRESO
        - `"ESCUINTLA"` = ESCUINTLA
        - `"GUATEMALA"` = GUATEMALA
        - `"HUEHUETENANGO"` = HUEHUETENANGO
        - `"IZABAL"` = IZABAL
        - `"JALAPA"` = JALAPA
        - `"JUTIAPA"` = JUTIAPA
        - `"PETÉN"` = PETÉN
        - `"QUETZALTENANGO"` = QUETZALTENANGO
        - `"QUICHÉ"` = QUICHÉ
        - `"RETALHULEU"` = RETALHULEU
        - `"SACATEPÉQUEZ"` = SACATEPÉQUEZ
        - `"SAN MARCOS"` = SAN MARCOS
        - `"SANTA ROSA"` = SANTA ROSA
        - `"SOLOLÁ"` = SOLOLÁ
        - `"SUCHITEPÉQUEZ"` = SUCHITEPÉQUEZ
        - `"TOTONICAPÁN"` = TOTONICAPÁN
        - `"ZACAPA"` = ZACAPA

    > **Sub-pregunta** (aparece cuando respuesta = `"GUATEMALA"`)

      ###### `municipio`
      - **Texto**: MUNICIPIO
      - **Tipo**: Texto libre

    > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

      ###### `especifique_pais1`
      - **Texto**: ESPECIFIQUE
      - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

    ###### `fecha_de_salida_viaje`
    - **Texto**: FECHA DE SALIDA
    - **Tipo**: Fecha/Hora

  > **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

    ###### `fecha_de_entrada_viaje`
    - **Texto**: FECHA DE ENTRADA
    - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

  ##### `alguna_persona_de_su_casa_ha_viajado_al_exterior`
  - **Texto**: ¿ALGUNA PERSONA DE SU CASA HA VIAJADO AL EXTERIOR?
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"Si"` = Si
    - `"No"` = No

  > **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

    ###### `fecha_de_retorno`
    - **Texto**: Fecha de Retorno
    - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

  ##### `el_paciente_estuvo_en_contacto_con_una_mujer_embarazada1`
  - **Texto**: ¿EL PACIENTE ESTUVO EN CONTACTO CON UNA MUJER EMBARAZADA?
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"Si"` = Si
    - `"No"` = No
    - `"Desconocido"` = Desconocido

> **Sub-pregunta** (aparece cuando respuesta = `"Si"`)

  ##### `fuente_posible_de_contagio1`
  - **Texto**: FUENTE POSIBLE DE CONTAGIO
  - **Tipo**: Respuesta multiple
  - **Opciones**:
    - `"Contacto en el hogar"` = Contacto en el hogar
    - `"Servicio de Salud"` = Servicio de Salud
    - `"Institución Educativa"` = Institución Educativa

    - `"Espacio Público"` = Espacio Público
    - `"Comunidad"` = Comunidad
    - `"Evento Masivo"` = Evento Masivo
    - `"Transporte Internacional"` = Transporte Internacional

    - `"Desconocido"` = Desconocido
    - `"Otro"` = Otro

  > **Sub-pregunta** (aparece cuando respuesta = `"Otro"`)

    ###### `otro_especifique`
    - **Texto**: Otro (especifique)
    - **Tipo**: Texto libre

#### `acciones_de_respuesta`
- **Texto**: ACCIONES DE RESPUESTA
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_ACCIONES_DE_RESPUESTA
- **Opciones**:
  - `"SI"` = SI
  - `"NO"` = NO

> **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

  ##### `se_realizo_busqueda_activa_institucional_de_casos_bai`
  - **Texto**: ¿Se realizó búsqueda activa institucional de casos (BAI)?
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Si
    - `"2"` = No

  > **Sub-pregunta** (aparece cuando respuesta = `"1"`)

    ###### `numero_de_casos_sospechosos_identificados_en_bai`
    - **Texto**: Número de casos sospechosos identificados en BAI
    - **Tipo**: Numerico

> **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

  ##### `se_realizo_busqueda_activa_comunitaria_de_casos_bac`
  - **Texto**: ¿Se realizó búsqueda activa comunitaria de casos (BAC)?
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Si
    - `"2"` = No

  > **Sub-pregunta** (aparece cuando respuesta = `"1"`)

    ###### `numero_de_casos_sospechosos_identificados_en_bac`
    - **Texto**: Número de casos sospechosos identificados en BAC: 
    - **Tipo**: Numerico

> **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

  ##### `hubo_vacunacion_de_bloqueo`
  - **Texto**: ¿Hubo vacunación de bloqueo en las primeras 48 a 72hrs?
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Si
    - `"2"` = No

> **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

  ##### `hubo_vacunacion_con_barrido_documentado`
  - **Texto**: ¿Hubo vacunación con barrido documentado?                  
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Si
    - `"2"` = No

> **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

  ##### `se_realizo_monitoreo_rapido_de_vacunacion`
  - **Texto**: ¿Se realizó monitoreo rápido de vacunación?
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Si
    - `"2"` = No

> **Sub-pregunta** (aparece cuando respuesta = `"SI"`)

  ##### `se_le_administro_vitamina_a`
  - **Texto**: ¿Se le administró vitamina A? 
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Si
    - `"2"` = No
    - `"3"` = Desconocido

  > **Sub-pregunta** (aparece cuando respuesta = `"1"`)

    ###### `numero_de_dosis_de_vitamina_a_recibidas`
    - **Texto**: Número de dosis de vitamina A recibidas 
    - **Tipo**: Numerico

> **Sub-pregunta** (aparece cuando respuesta = `"NO"`)

  ##### `por_que_no_acciones_respuesta`
  - **Texto**: ¿Por qué?
  - **Tipo**: Texto libre

#### `clasificacion`
- **Texto**: CLASIFICACIÓN
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_OUTCOME_STATUS
- **Opciones**:
  - `"CLASIFICADO"` = CLASIFICADO
  - `"2"` = PENDIENTE DE CLASIFICAR

> **Sub-pregunta** (aparece cuando respuesta = `"CLASIFICADO"`)

  ##### `clasificacion_final`
  - **Texto**: CLASIFICACIÓN FINAL
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Sarampion
    - `"2"` = Rubeola
    - `"3"` = Descartado
    - `"5"` = No cumple con la definición de caso

  > **Sub-pregunta** (aparece cuando respuesta = `"1"`)

    ###### `criterio_de_confirmacion_sarampion`
    - **Texto**: CRITERIO DE CONFIRMACION SARAMPION
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"LABSR"` = LABORATORIO
      - `"NE"` = NEXO EPIDEMIOLÓGOCO
      - `"CX"` = CLÍNICO

  > **Sub-pregunta** (aparece cuando respuesta = `"2"`)

    ###### `criterio_de_confirmacion_rubeola`
    - **Texto**: CRITERIO DE CONFIRMACION RUBEOLA
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"LABRB"` = LABORATORIO
      - `"NERB"` = NEXO EPIDEMIOLÓGICO
      - `"CXRB"` = CLÍNICO

  > **Sub-pregunta** (aparece cuando respuesta = `"3"`)

    ###### `criterio_para_descartar_el_caso`
    - **Texto**: CRITERIO PARA DESCARTAR EL CASO
    - **Tipo**: Respuesta unica
    - **Opciones**:
      - `"LAB"` = LABORATORIAL
      - `"RVAC"` = RELACIONADO CON LA VACUNA
      - `"CX2"` = CLINICO
      - `"OTRO"` = OTRO

    > **Sub-pregunta** (aparece cuando respuesta = `"OTRO"`)

      ###### `especifiqueX`
      - **Texto**: ESPECIFIQUE
      - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"CLASIFICADO"`)

  ##### `contacto_de_otro_caso`
  - **Texto**: CONTACTO DE OTRO CASO
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"SI"` = SI
    - `"NO"` = NO

> **Sub-pregunta** (aparece cuando respuesta = `"CLASIFICADO"`)

  ##### `fuente_de_infeccion_de_los_casos_confirmados`
  - **Texto**: FUENTE DE INFECCIÓN DE LOS CASOS CONFIRMADOS
  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Importado
    - `"2"` = Relacionado con la importación

    - `"3"` = Endemico
    - `"4"` = Fuente desconocida

  > **Sub-pregunta** (aparece cuando respuesta = `"1"`)

    ###### `importado_pais_de_importacion`
    - **Texto**: País de Importación
    - **Tipo**: Texto libre

  > **Sub-pregunta** (aparece cuando respuesta = `"2"`)

    ###### `pais_de_importacion`
    - **Texto**: País de Importación
    - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"CLASIFICADO"`)

  ##### `caso_analizado_por`
  - **Texto**: CASO ANALIZADO POR
  - **Tipo**: Respuesta multiple
  - **Opciones**:
    - `"1"` = CONAPI
    - `"2"` = DEGR
    - `"3"` = COMISIÓN NACIONAL
    - `"4"` = OTRO

  > **Sub-pregunta** (aparece cuando respuesta = `"4"`)

    ###### `especifique_otro_clasificacion`
    - **Texto**: Especifique
    - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"CLASIFICADO"`)

  ##### `fecha_de_clasificacion`
  - **Texto**: FECHA DE CLASIFICACIÓN
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"CLASIFICADO"`)

  ##### `condicion_final_del_paciente`
  - **Texto**: CONDICIÓN FINAL DEL PACIENTE

  - **Tipo**: Respuesta unica
  - **Opciones**:
    - `"1"` = Recuperado
    - `"2"` = Con Secuelas
    - `"3"` = Fallecido
    - `"4"` = Desconocido

  > **Sub-pregunta** (aparece cuando respuesta = `"3"`)

    ###### `fecha_de_defuncion`
    - **Texto**: Fecha de  Defunción

    - **Tipo**: Fecha/Hora

  > **Sub-pregunta** (aparece cuando respuesta = `"3"`)

    ###### `causa_de_muerte_segun_certificado_de_defuncion`
    - **Texto**: Causa De Muerte Según Certificado De Defunción
    - **Tipo**: Texto libre

#### `lugares_visitados_y_rutas_de_desplazamiento_del_caso`
- **Texto**: LUGARES VISITADOS Y RUTAS DE DESPLAZAMIENTO DEL CASO
- **Tipo**: Respuesta unica
- **Categoria**: LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_RECENT_TRAVEL
- **Opciones**:
  - `"1"` = SE INVESTIGO
  - `"2"` = NO SÉ INVESTIGO
  - `"DESCONOCIDO"` = DESCONOCIDO

> **Sub-pregunta** (aparece cuando respuesta = `"1"`)

  ##### `sitio_ruta_de_desplazamiento_1`
  - **Texto**: SITIO/RUTA DE DESPLAZAMIENTO
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"1"`)

  ##### `direccion_del_lugar_y_rutas_de_desplazamiento_1`
  - **Texto**: DIRECCIÓN DEL LUGAR Y RUTAS DE DESPLAZAMIENTO
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"1"`)

  ##### `fecha_en_que_visito_el_lugar_ruta_1`
  - **Texto**: FECHAS EN QUE VISITÓ EL LUGAR / RUTA
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"1"`)

  ##### `tipo_de_abordaje_realizado_1`
  - **Texto**: TIPO DE ABORDAJE REALIZADO
  - **Tipo**: Respuesta multiple
  - **Opciones**:
    - `"BLOQUEO"` = BLOQUEO
    - `"BARRIDO"` = BARRIDO
    - `"3"` = BAC
    - `"4"` = BAI

> **Sub-pregunta** (aparece cuando respuesta = `"1"`)

  ##### `fecha_de_abordaje_1`
  - **Texto**: FECHA DE ABORDAJE
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"2"`)

  ##### `sitio_ruta_de_desplazamiento_2`
  - **Texto**: Sitio/ruta de desplazamiento
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"2"`)

  ##### `direccion_del_lugar_y_rutas_de_desplazamiento_2`
  - **Texto**: Dirección del lugar y rutas de desplazamiento
  - **Tipo**: Texto libre

> **Sub-pregunta** (aparece cuando respuesta = `"2"`)

  ##### `fecha_en_que_visito_el_lugar_ruta_2`
  - **Texto**: Fecha en que visitó el lugar/ruta 
  - **Tipo**: Fecha/Hora

> **Sub-pregunta** (aparece cuando respuesta = `"2"`)

  ##### `tipo_de_abordaje_realizado_2`
  - **Texto**: Tipo de abordaje realizado
  - **Tipo**: Respuesta multiple
  - **Opciones**:
    - `"1"` = Bloqueo
    - `"2"` = Barrido
    - `"3"` = BAC
    - `"4"` = BAI

> **Sub-pregunta** (aparece cuando respuesta = `"2"`)

  ##### `fecha_de_abordaje_2`
  - **Texto**: Fecha de abordaje 
  - **Tipo**: Fecha/Hora

### 3.3 Indice Completo de Variables del Cuestionario

Mapa completo de tokens a texto en espanol (1176 tokens de investigacion de caso):

```
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_NO_QUESTION_POR_QUE_NO_ACCIONES_RESPUESTA_TEXT: ¿Por qué?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_HUBO_VACUNACION_CON_BARRIDO_DOCUMENTADO_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_HUBO_VACUNACION_CON_BARRIDO_DOCUMENTADO_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_HUBO_VACUNACION_CON_BARRIDO_DOCUMENTADO_TEXT: ¿Hubo vacunación con barrido documentado?                  
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_HUBO_VACUNACION_DE_BLOQUEO_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_HUBO_VACUNACION_DE_BLOQUEO_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_HUBO_VACUNACION_DE_BLOQUEO_TEXT: ¿Hubo vacunación de bloqueo en las primeras 48 a 72hrs?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_LE_ADMINISTRO_VITAMINA_A_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_LE_ADMINISTRO_VITAMINA_A_ANSWER_1_QUESTION_NUMERO_DE_DOSIS_DE_VITAMINA_A_RECIBIDAS_TEXT: Número de dosis de vitamina A recibidas 
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_LE_ADMINISTRO_VITAMINA_A_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_LE_ADMINISTRO_VITAMINA_A_ANSWER_3_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_LE_ADMINISTRO_VITAMINA_A_TEXT: ¿Se le administró vitamina A? 
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_COMUNITARIA_DE_CASOS_BAC_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_COMUNITARIA_DE_CASOS_BAC_ANSWER_1_QUESTION_NUMERO_DE_CASOS_SOSPECHOSOS_IDENTIFICADOS_EN_BAC_TEXT: Número de casos sospechosos identificados en BAC: 
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_COMUNITARIA_DE_CASOS_BAC_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_COMUNITARIA_DE_CASOS_BAC_TEXT: ¿Se realizó búsqueda activa comunitaria de casos (BAC)?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_INSTITUCIONAL_DE_CASOS_BAI_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_INSTITUCIONAL_DE_CASOS_BAI_ANSWER_1_QUESTION_NUMERO_DE_CASOS_SOSPECHOSOS_IDENTIFICADOS_EN_BAI_TEXT: Número de casos sospechosos identificados en BAI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_INSTITUCIONAL_DE_CASOS_BAI_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_BUSQUEDA_ACTIVA_INSTITUCIONAL_DE_CASOS_BAI_TEXT: ¿Se realizó búsqueda activa institucional de casos (BAI)?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_MONITOREO_RAPIDO_DE_VACUNACION_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_MONITOREO_RAPIDO_DE_VACUNACION_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_ANSWER_SI_QUESTION_SE_REALIZO_MONITOREO_RAPIDO_DE_VACUNACION_TEXT: ¿Se realizó monitoreo rápido de vacunación?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ACCIONES_DE_RESPUESTA_TEXT: ACCIONES DE RESPUESTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_LABEL: ANTECEDENTES MEDICOS Y DE VACUNACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_QUESTION_ESPECIFIQUE_ANT_ANSWER_DESNUTRICION_LABEL: DESNUTRICIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_QUESTION_ESPECIFIQUE_ANT_ANSWER_ENFERMEDAD_CRONICA_LABEL: ENFERMEDAD CRÓNICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_QUESTION_ESPECIFIQUE_ANT_ANSWER_INMUNOCOMPROMISO_LABEL: INMUNOCOMPROMISO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_QUESTION_ESPECIFIQUE_ANT_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_QUESTION_ESPECIFIQUE_ANT_ANSWER_OTRO_QUESTION_ESPECIFIQUE_A_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_ANSWER_SI_QUESTION_ESPECIFIQUE_ANT_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_ANTECEDENTES_MEDICOS_TEXT: ANTECEDENTES MÉDICOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_FUENTE_DE_LA_INFORMACION_SOBRE_LA_VACUNACION_ANSWER_CARNE_DE_VACUNACION_LABEL: CARNÉ DE VACUNACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_FUENTE_DE_LA_INFORMACION_SOBRE_LA_VACUNACION_ANSWER_REGISTRO_UNICO_DE_VACUNACION_LABEL: REGISTRO ÚNICO DE VACUNACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_FUENTE_DE_LA_INFORMACION_SOBRE_LA_VACUNACION_ANSWER_SIGSA_5_A_CUADERNO_LABEL: SIGSA 5A CUADERNO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_FUENTE_DE_LA_INFORMACION_SOBRE_LA_VACUNACION_ANSWER_SIGSA_5_B_OTROS_GRUPOS_LABEL: SIGSA 5B OTROS GRUPOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_FUENTE_DE_LA_INFORMACION_SOBRE_LA_VACUNACION_TEXT: FUENTE DE LA INFORMACIÓN SOBRE LA VACUNACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_ANSWER_SPR_SARAMPION_PAPERAS_RUBEOLA_LABEL: SPR – Sarampión Paperas Rubéola
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_ANSWER_SPR_SARAMPION_PAPERAS_RUBEOLA_QUESTION_FECHA_DE_LA_ULTIMA_DOSIS_TEXT: Fecha De La Última Dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_ANSWER_SPR_SARAMPION_PAPERAS_RUBEOLA_QUESTION_NUMERO_DE_DOSIS_TEXT: Número De Dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_ANSWER_SR_SARAMPION_RUBEOLA_LABEL: SR – Sarampión Rubéola
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_ANSWER_SR_SARAMPION_RUBEOLA_QUESTION_FECHA_DE_LA_ULTIMA_DOSIS_TEXT: Fecha De La Última Dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_ANSWER_SR_SARAMPION_RUBEOLA_QUESTION_NUMERO_DE_DOSIS_TEXT: Número De Dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_TIPO_DE_VACUNA_RECIBIDA_TEXT: TIPO DE VACUNA RECIBIDA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_VACUNACION_EN_EL_SECTOR_ANSWER_IGSS_LABEL: IGSS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_VACUNACION_EN_EL_SECTOR_ANSWER_MSPAS_LABEL: MSPAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_VACUNACION_EN_EL_SECTOR_ANSWER_PRIVADO_LABEL: PRIVADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_SI_QUESTION_VACUNACION_EN_EL_SECTOR_TEXT: VACUNACIÓN EN EL SECTOR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_ANSWER_VERBAL_LABEL: VERBAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_ANSWER_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_QUESTION_PACIENTE_VACUNADO_TEXT: PACIENTE VACUNADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION_TEXT: ANTECEDENTES MÉDICOS Y DE VACUNACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_2_LABEL: PENDIENTE DE CLASIFICAR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_LABEL: CLASIFICADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CASO_ANALIZADO_POR_ANSWER_1_LABEL: CONAPI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CASO_ANALIZADO_POR_ANSWER_2_LABEL: DEGR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CASO_ANALIZADO_POR_ANSWER_3_LABEL: COMISIÓN NACIONAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CASO_ANALIZADO_POR_ANSWER_4_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CASO_ANALIZADO_POR_ANSWER_4_QUESTION_ESPECIFIQUE_OTRO_CLASIFICACION_TEXT: Especifique
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CASO_ANALIZADO_POR_TEXT: CASO ANALIZADO POR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_1_LABEL: Sarampion
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_1_QUESTION_CRITERIO_DE_CONFIRMACION_SARAMPION_ANSWER_CX_LABEL: CLÍNICO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_1_QUESTION_CRITERIO_DE_CONFIRMACION_SARAMPION_ANSWER_LABSR_LABEL: LABORATORIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_1_QUESTION_CRITERIO_DE_CONFIRMACION_SARAMPION_ANSWER_NE_LABEL: NEXO EPIDEMIOLÓGOCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_1_QUESTION_CRITERIO_DE_CONFIRMACION_SARAMPION_TEXT: CRITERIO DE CONFIRMACION SARAMPION
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_2_LABEL: Rubeola
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_2_QUESTION_CRITERIO_DE_CONFIRMACION_RUBEOLA_ANSWER_CXRB_LABEL: CLÍNICO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_2_QUESTION_CRITERIO_DE_CONFIRMACION_RUBEOLA_ANSWER_LABRB_LABEL: LABORATORIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_2_QUESTION_CRITERIO_DE_CONFIRMACION_RUBEOLA_ANSWER_NERB_LABEL: NEXO EPIDEMIOLÓGICO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_2_QUESTION_CRITERIO_DE_CONFIRMACION_RUBEOLA_TEXT: CRITERIO DE CONFIRMACION RUBEOLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_LABEL: Descartado
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_QUESTION_CRITERIO_PARA_DESCARTAR_EL_CASO_ANSWER_CX_2_LABEL: CLINICO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_QUESTION_CRITERIO_PARA_DESCARTAR_EL_CASO_ANSWER_LAB_LABEL: LABORATORIAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_QUESTION_CRITERIO_PARA_DESCARTAR_EL_CASO_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_QUESTION_CRITERIO_PARA_DESCARTAR_EL_CASO_ANSWER_OTRO_QUESTION_ESPECIFIQUE_X_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_QUESTION_CRITERIO_PARA_DESCARTAR_EL_CASO_ANSWER_RVAC_LABEL: RELACIONADO CON LA VACUNA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_3_QUESTION_CRITERIO_PARA_DESCARTAR_EL_CASO_TEXT: CRITERIO PARA DESCARTAR EL CASO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_ANSWER_5_LABEL: No cumple con la definición de caso
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CLASIFICACION_FINAL_TEXT: CLASIFICACIÓN FINAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_ANSWER_1_LABEL: Recuperado
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_ANSWER_2_LABEL: Con Secuelas
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_ANSWER_3_LABEL: Fallecido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_ANSWER_3_QUESTION_CAUSA_DE_MUERTE_SEGUN_CERTIFICADO_DE_DEFUNCION_TEXT: Causa De Muerte Según Certificado De Defunción
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_ANSWER_3_QUESTION_FECHA_DE_DEFUNCION_TEXT: Fecha de  Defunción

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_ANSWER_4_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONDICION_FINAL_DEL_PACIENTE_TEXT: CONDICIÓN FINAL DEL PACIENTE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONTACTO_DE_OTRO_CASO_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONTACTO_DE_OTRO_CASO_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_CONTACTO_DE_OTRO_CASO_TEXT: CONTACTO DE OTRO CASO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FECHA_DE_CLASIFICACION_TEXT: FECHA DE CLASIFICACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_ANSWER_1_LABEL: Importado
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_ANSWER_1_QUESTION_IMPORTADO_PAIS_DE_IMPORTACION_TEXT: País de Importación
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_ANSWER_2_LABEL: Relacionado con la importación

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_ANSWER_2_QUESTION_PAIS_DE_IMPORTACION_TEXT: País de Importación
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_ANSWER_3_LABEL: Endemico
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_ANSWER_4_LABEL: Fuente desconocida
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_ANSWER_CLASIFICADO_QUESTION_FUENTE_DE_INFECCION_DE_LOS_CASOS_CONFIRMADOS_TEXT: FUENTE DE INFECCIÓN DE LOS CASOS CONFIRMADOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_CLASIFICACION_TEXT: CLASIFICACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_LABEL: DATOS CLÍNICOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_AISLAMIENTO_RESPIRATORIO_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_AISLAMIENTO_RESPIRATORIO_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_AISLAMIENTO_RESPIRATORIO_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_AISLAMIENTO_RESPIRATORIO_ANSWER_SI_QUESTION_FECHA_DE_AISLAMIENTO_TEXT: FECHA DE AISLAMIENTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_AISLAMIENTO_RESPIRATORIO_TEXT: AISLAMIENTO RESPIRATORIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_CEGUERA_LABEL: CEGUERA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_DIARREA_LABEL: DIARREA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_ENCEFALITIS_LABEL: ENCEFALITIS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_NEUMONIA_LABEL: NEUMONÍA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_OTITIS_MEDIA_AGUDA_LABEL: OTITIS MEDIA AGUDA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_OTRA_LABEL: OTRA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_OTRA_QUESTION_ESPECIQUE_TEXT:  (ESPECIQUE)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_ANSWER_TROMBOCITOPENIA_LABEL: TROMBOCITOPENIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_ANSWER_SI_QUESTION_ESPECIFIQUE_COMPLICACIONES_TEXT: ESPECIFIQUE COMPLICACIONES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_COMPLICACIONES_TEXT: COMPLICACIONES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_FECHA_DE_INICIO_DE_EXANTEMA_RASH_TEXT: FECHA DE INICIO DE EXANTEMA / RASH
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_FECHA_DE_INICIO_DE_FIEBRE_TEXT: FECHA DE INICIO DE FIEBRE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_FECHA_DE_INICIO_DE_SINTOMAS_TEXT: FECHA DE INICIO DE SÍNTOMAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_HOSPITALIZACION_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_HOSPITALIZACION_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_HOSPITALIZACION_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_HOSPITALIZACION_ANSWER_SI_QUESTION_FECHA_DE_HOSPITALIZACION_TEXT: FECHA DE HOSPITALIZACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_HOSPITALIZACION_ANSWER_SI_QUESTION_NOMBRE_DEL_HOSPITAL_TEXT: NOMBRE DEL HOSPITAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_HOSPITALIZACION_TEXT: HOSPITALIZACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_ADENOPATIAS_LABEL: Adenopatías
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_ARTRALGIA_ARTRITIS_LABEL: Artralgia / Artritis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_CONJUNTIVITIS_LABEL: Conjuntivitis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_CORIZA_CATARRO_LABEL: Coriza / Catarro
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_EXANTEMA_RASH_LABEL: Exantema/ Rash
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_FIEBRE_LABEL: Fiebre
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_FIEBRE_QUESTION_TEMP_C_TEXT: Fiebre (Temp. C°)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_MANCHAS_DE_KOPLIK_LABEL: Manchas de Koplik
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_ANSWER_TOS_LABEL: Tos
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_ANSWER_SI_QUESTION_QUE_SINTOMAS_TEXT: ¿QUE SÍNTOMAS?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_ANSWER_DATOS_CLINICOS_QUESTION_SINTOMAS_TEXT: SÍNTOMAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DATOS_CLINICOS_TEXT: DATOS CLÍNICOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_DENGUE_LABEL: DENGUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_OTRO_ARBOVIROSIS_LABEL: OTRO ARBOVIROSIS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_OTRO_ARBOVIROSIS_QUESTION_ESPECIFIQUE_TEXT: ESPECIFIQUE OTRO ARBOVIROSIS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_OTRO_FEBRIL_EXANTEMATICA_LABEL: OTRO FEBRIL EXANTEMÁTICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_OTRO_FEBRIL_EXANTEMATICA_QUESTION_ESPECIFIQUE_TEXT: ESPECIFIQUE OTRO FEBRIL EXANTEMÁTICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_RUBEOLA_LABEL: RUBÉOLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_SARAMPION_LABEL: SARAMPIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_SARAMPION_QUESTION_CASO_ALTAMENTE_SOSPECHOSO_DE_SARAMPION_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_SARAMPION_QUESTION_CASO_ALTAMENTE_SOSPECHOSO_DE_SARAMPION_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_ANSWER_SARAMPION_QUESTION_CASO_ALTAMENTE_SOSPECHOSO_DE_SARAMPION_TEXT: CASO ALTAMENTE SOSPECHOSO DE SARAMPIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_DIAGNOSTICO_DE_SOSPECHA_TEXT: DIAGNOSTICO DE SOSPECHA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_NO_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_ALGUNA_PERSONA_DE_SU_CASA_HA_VIAJADO_AL_EXTERIOR_ANSWER_NO_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_ALGUNA_PERSONA_DE_SU_CASA_HA_VIAJADO_AL_EXTERIOR_ANSWER_SI_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_ALGUNA_PERSONA_DE_SU_CASA_HA_VIAJADO_AL_EXTERIOR_ANSWER_SI_QUESTION_FECHA_DE_RETORNO_TEXT: Fecha de Retorno
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_ALGUNA_PERSONA_DE_SU_CASA_HA_VIAJADO_AL_EXTERIOR_TEXT: ¿ALGUNA PERSONA DE SU CASA HA VIAJADO AL EXTERIOR?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EL_PACIENTE_ESTUVO_EN_CONTACTO_CON_UNA_MUJER_EMBARAZADA_1_ANSWER_DESCONOCIDO_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EL_PACIENTE_ESTUVO_EN_CONTACTO_CON_UNA_MUJER_EMBARAZADA_1_ANSWER_NO_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EL_PACIENTE_ESTUVO_EN_CONTACTO_CON_UNA_MUJER_EMBARAZADA_1_ANSWER_SI_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EL_PACIENTE_ESTUVO_EN_CONTACTO_CON_UNA_MUJER_EMBARAZADA_1_TEXT: ¿EL PACIENTE ESTUVO EN CONTACTO CON UNA MUJER EMBARAZADA?
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EXISTE_CASO_EN_MUNI_ANSWER_DESCONOCIDO_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EXISTE_CASO_EN_MUNI_ANSWER_NO_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EXISTE_CASO_EN_MUNI_ANSWER_SI_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_EXISTE_CASO_EN_MUNI_TEXT: EXISTE ALGÚN CASO CONFIRMADO EN LA COMUNIDAD O MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_COMUNIDAD_LABEL: Comunidad
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_CONTACTO_EN_EL_HOGAR_LABEL: Contacto en el hogar
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_DESCONOCIDO_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_ESPACIO_PUBLICO_LABEL: Espacio Público
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_EVENTO_MASIVO_LABEL: Evento Masivo
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_INSTITUCION_EDUCATIVA_LABEL: Institución Educativa

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_OTRO_LABEL: Otro
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_OTRO_QUESTION_OTRO_ESPECIFIQUE_TEXT: Otro (especifique)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_SERVICIO_DE_SALUD_LABEL: Servicio de Salud
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_ANSWER_TRANSPORTE_INTERNACIONAL_LABEL: Transporte Internacional

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_FUENTE_POSIBLE_DE_CONTAGIO_1_TEXT: FUENTE POSIBLE DE CONTAGIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_TUVO_CONTACTO_CON_UN_CASO_SOSPECHOSO_O_CONFIRMADO_ANSWER_DESCONOCIDO_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_TUVO_CONTACTO_CON_UN_CASO_SOSPECHOSO_O_CONFIRMADO_ANSWER_NO_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_TUVO_CONTACTO_CON_UN_CASO_SOSPECHOSO_O_CONFIRMADO_ANSWER_SI_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_TUVO_CONTACTO_CON_UN_CASO_SOSPECHOSO_O_CONFIRMADO_TEXT: TUVO CONTACTO CON UN CASO SOSPECHOSO O CONFIRMADO ENTRE 7-23 DÍAS ANTES DEL INICIO DEL EXANTEMA/RASH
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_NO_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_FECHA_DE_ENTRADA_VIAJE_TEXT: FECHA DE ENTRADA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_FECHA_DE_SALIDA_VIAJE_TEXT: FECHA DE SALIDA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_LABEL: GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_ALTA_VERAPAZ_LABEL: ALTA VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_BAJA_VERAPAZ_LABEL: BAJA VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_CHIMALTENANGO_LABEL: CHIMALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_CHIQUIMULA_LABEL: CHIQUIMULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_EL_PROGRESO_LABEL: EL PROGRESO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_ESCUINTLA_LABEL: ESCUINTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_GUATEMALA_LABEL: GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_HUEHUETENANGO_LABEL: HUEHUETENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_IZABAL_LABEL: IZABAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_JALAPA_LABEL: JALAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_JUTIAPA_LABEL: JUTIAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_PETEN_LABEL: PETÉN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_QUETZALTENANGO_LABEL: QUETZALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_QUICHE_LABEL: QUICHÉ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_RETALHULEU_LABEL: RETALHULEU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_SACATEPEQUEZ_LABEL: SACATEPÉQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_SANTA_ROSA_LABEL: SANTA ROSA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_SAN_MARCOS_LABEL: SAN MARCOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_SOLOLA_LABEL: SOLOLÁ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_SUCHITEPEQUEZ_LABEL: SUCHITEPÉQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_TOTONICAPAN_LABEL: TOTONICAPÁN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_ANSWER_ZACAPA_LABEL: ZACAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_TEXT: DEPARTAMENTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_TEXT: MUNICIPIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_ANSWER_OTRO_QUESTION_ESPECIFIQUE_PAIS_1_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_ANSWER_SI_QUESTION_PAIS_DEPARTAMENTO_Y_MUNICIPIO_TEXT: PAÍS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_ANSWER_SI_QUESTION_VIAJO_DURANTE_LOS_7_23_DIAS_TEXT: VIAJÓ DURANTE LOS 7-23 DÍAS PREVIOS AL INICIO DEL EXANTEMA O RASH
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FACTORES_DE_RIESGO_TEXT: FACTORES DE RIESGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_LABEL: UNIDAD NOTIFICADORA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_CARGO_DE_QUIEN_INVESTIGA_TEXT: CARGO DE QUIÉN INVESTIGA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_CORREO_ELECTRONICO_TEXT: CORREO ELECTRÓNICO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_LABEL: ALTA VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_CAHABON_LABEL: CAHABON
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_CAMPUR_LABEL: CAMPUR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_CHAHAL_LABEL: CHAHAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_CHISEC_LABEL: CHISEC
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_COBAN_LABEL: COBAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_FRAY_BARTOLOME_DE_LAS_CASAS_LABEL: FRAY BARTOLOME DE LAS CASAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_LANQUIN_LABEL: LANQUIN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_LA_TINTA_LABEL: LA TINTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_PANZOS_LABEL: PANZOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_RAXRUHA_LABEL: RAXRUHA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SANTA_CRUZ_VERAPAZ_LABEL: SANTA CRUZ VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SAN_CRISTOBAL_VERAPAZ_LABEL: SAN CRISTOBAL VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SAN_JUAN_CHAMELCO_LABEL: SAN JUAN CHAMELCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SAN_PEDRO_CARCHA_LABEL: SAN PEDRO CARCHA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SENAHU_LABEL: SENAHU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_TACTIC_LABEL: TACTIC
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_TAMAHU_LABEL: TAMAHU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_TELEMAN_LABEL: TELEMAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_TUCURU_LABEL: TUCURU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ALTA_VERAPAZ_QUESTION_SERVICIO_DE_SALUD_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_LABEL: BAJA VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_CUBULCO_LABEL: CUBULCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_EL_CHOL_LABEL: EL CHOL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_GRANADOS_LABEL: GRANADOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_PURULHA_LABEL: PURULHA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_RABINAL_LABEL: RABINAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SALAMA_LABEL: SALAMA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SAN_JERONIMO_LABEL: SAN JERONIMO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_ANSWER_SAN_MIGUEL_CHICAJ_LABEL: SAN MIGUEL CHICAJ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_BAJA_VERAPAZ_QUESTION_SERVICIO_DE_SALUD_1_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_LABEL: CHIMALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_ACATENANGO_LABEL: ACATENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_CHIMALTENANGO_LABEL: CHIMALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_EL_TEJAR_LABEL: EL TEJAR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_PAQUIP_TECPAN_GUATEMALA_LABEL: PAQUIP TECPAN GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_PARRAMOS_LABEL: PARRAMOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_PATZICIA_LABEL: PATZICIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_PATZUN_LABEL: PATZUN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SANTA_APOLONIA_LABEL: SANTA APOLONIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SANTA_CRUZ_BALANYA_LABEL: SANTA CRUZ BALANYA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SAN_ANDRES_ITZAPA_LABEL: SAN ANDRES ITZAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SAN_JOSE_POAQUIL_LABEL: SAN JOSE POAQUIL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SAN_JUAN_COMALAPA_LABEL: SAN JUAN COMALAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SAN_MARTIN_JILOTEPEQUE_LABEL: SAN MARTIN JILOTEPEQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SAN_MIGUEL_POCHUTA_LABEL: SAN MIGUEL POCHUTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_SAN_PEDRO_YEPOCAPA_LABEL: SAN PEDRO YEPOCAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_TECPAN_GUATEMALA_LABEL: TECPAN GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_ANSWER_ZARAGOZA_LABEL: ZARAGOZA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CHI_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIMALTENANGO_QUESTION_SERVICIO_DE_SALUD_2_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_LABEL: CHIQUIMULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_CAMOTAN_LABEL: CAMOTAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_CHIQUIMULA_LABEL: CHIQUIMULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_CONCEPCION_LAS_MINAS_LABEL: CONCEPCION LAS MINAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_ESQUIPULAS_LABEL: ESQUIPULAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_IPALA_LABEL: IPALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_JOCOTAN_LABEL: JOCOTAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_OLOPA_LABEL: OLOPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_QUETZALTEPEQUE_LABEL: QUETZALTEPEQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_SAN_JACINTO_LABEL: SAN JACINTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_SAN_JOSE_LA_ARADA_LABEL: SAN JOSE LA ARADA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_ANSWER_SAN_JUAN_LA_ERMITA_LABEL: SAN JUAN LA ERMITA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_CH_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_CHIQUIMULA_QUESTION_SERVICIO_DE_SALUD_3_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_LABEL: EL PROGRESO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_EL_JICARO_LABEL: EL JICARO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_GUASTATOYA_LABEL: GUASTATOYA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_MORAZAN_LABEL: MORAZAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_SANARATE_LABEL: SANARATE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_SANSARE_LABEL: SANSARE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_SAN_AGUSTIN_ACASAGUASTLAN_LABEL: SAN AGUSTIN ACASAGUASTLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_SAN_ANTONIO_LA_PAZ_LABEL: SAN ANTONIO LA PAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_ANSWER_SAN_CRISTOBAL_ACASAGUASTLAN_LABEL: SAN CRISTOBAL ACASAGUASTLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_1_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_EL_PROGRESO_QUESTION_SERVICIO_DE_SALUD_4_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_LABEL: ESCUINTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_ESCUINTLA_LABEL: ESCUINTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_GUANAGAZAPA_LABEL: GUANAGAZAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_LA_DEMOCRACIA_LABEL: LA DEMOCRACIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_LA_GOMERA_LABEL: LA GOMERA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_MASAGUA_LABEL: MASAGUA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_NUEVA_CONCEPCION_LABEL: NUEVA CONCEPCION
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_PALIN_LABEL: PALIN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_PUERTO_IZTAPA_LABEL: PUERTO IZTAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_PUERTO_SAN_JOSE_LABEL: PUERTO SAN JOSE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_SANTA_LUCIA_COTZUMALGUAPA_LABEL: SANTA LUCIA COTZUMALGUAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_SAN_VICENTE_PACAYA_LABEL: SAN VICENTE PACAYA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_SIPACATE_LABEL: SIPACATE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_SIQUINALA_LABEL: SIQUINALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_ANSWER_TIQUISATE_LABEL: TIQUISATE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_3_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ESCUINTLA_QUESTION_SERVICIO_DE_SALUD_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_LABEL: GUATEMALA CENTRAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_BETHANIA_LABEL: BETHANIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_CENTRO_AMERICA_LABEL: CENTRO AMERICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_EL_AMPARO_LABEL: EL AMPARO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_EL_PARAISO_LABEL: EL PARAISO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_JUSTO_RUFINO_BARRIOS_LABEL: JUSTO RUFINO BARRIOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_SANTA_ELENA_III_LABEL: SANTA ELENA III
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_SAN_RAFAEL_LABEL: SAN RAFAEL LA LAGUNA II
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_ZONA_11_LABEL: ZONA 11
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_ZONA_1_LABEL: ZONA 1
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_ZONA_3_LABEL: ZONA 3
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_ZONA_5_LABEL: ZONA 5
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_ANSWER_ZONA_6_LABEL: ZONA 6
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_4_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_CENTRAL_QUESTION_SERVICIO_DE_SALUD_5_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_LABEL: GUATEMALA NOR OCCIDENTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_CHUARRANCHO_LABEL: CHUARRANCHO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_CIUDAD_QUETZAL_LABEL: CIUDAD QUETZAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_COMUNIDAD_LABEL: COMUNIDAD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_EL_MILAGRO_LABEL: EL MILAGRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_MIXCO_LABEL: MIXCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_PRIMERO_DE_JULIO_LABEL: PRIMERO DE JULIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_SAN_JUAN_SACATEPEQUEZ_LABEL: SAN JUAN SACATEPEQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_SAN_PEDRO_SACATEPEQUEZ_LABEL: SAN PEDRO SACATEPEQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_SAN_RAYMUNDO_LABEL: SAN RAYMUNDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_ANSWER_SATELITE_LABEL: SATELITE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_5_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_OCCIDENTE_QUESTION_SERVICIO_DE_SALUD_6_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_LABEL: GUATEMALA NOR ORIENTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_CHINAUTLA_LABEL: CHINAUTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_FRAIJANES_LABEL: FRAIJANES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_PALENCIA_LABEL: PALENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_SANTA_CATARINA_PINULA_LABEL: SANTA CATARINA PINULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_SAN_JOSE_DEL_GOLFO_LABEL: SAN JOSE DEL GOLFO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_SAN_JOSE_PINULA_LABEL: SAN JOSE PINULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_SAN_PEDRO_AYAMPUC_LABEL: SAN PEDRO AYAMPUC
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_ANSWER_TIERRA_NUEVA_LABEL: TIERRA NUEVA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_6_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_NOR_ORIENTE_QUESTION_SERVICIO_DE_SALUD_7_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_LABEL: GUATEMALA SUR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_AMATITLAN_LABEL: AMATITLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_BOCA_DEL_MONTE_LABEL: BOCA DEL MONTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_CIUDAD_REAL_LABEL: CIUDAD REAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_EL_MEZQUITAL_LABEL: EL MEZQUITAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_PERONIA_LABEL: PERONIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_SAN_MIGUEL_PETAPA_LABEL: SAN MIGUEL PETAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_VILLA_CANALES_LABEL: VILLA CANALES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_ANSWER_VILLA_NUEVA_LABEL: VILLA NUEVA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_7_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_GUATEMALA_SUR_QUESTION_SERVICIO_DE_SALUD_8_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_LABEL: HUEHUETENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_AGUACATAN_LABEL: AGUACATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_BARILLAS_LABEL: BARILLAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_CHIANTLA_LABEL: CHIANTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_COLOTENANGO_LABEL: COLOTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_CONCEPCION_HUISTA_LABEL: CONCEPCION HUISTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_CUILCO_LABEL: CUILCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_HUEHUETENANGO_NORTE_EL_CALVARIO_LABEL: HUEHUETENANGO NORTE EL CALVARIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_HUEHUETENANGO_SUR_LABEL: HUEHUETENANGO SUR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_JACALTENANGO_LABEL: JACALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_LA_DEMOCRACIA_LABEL: LA DEMOCRACIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_LA_LIBERTAD_LABEL: LA LIBERTAD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_MALACATANCITO_LABEL: MALACATANCITO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_NENTON_LABEL: NENTON
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_PETATAN_LABEL: PETATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SANTA_ANA_HUISTA_LABEL: SANTA ANA HUISTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SANTA_BARBARA_LABEL: SANTA BARBARA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SANTA_EULALIA_LABEL: SANTA EULALIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SANTIAGO_CHIMALTENANGO_LABEL: SANTIAGO CHIMALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_ANTONIO_HUISTA_LABEL: SAN ANTONIO HUISTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_GASPAR_IXCHIL_LABEL: SAN GASPAR IXCHIL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_IDELFONSO_IXTAHUACAN_LABEL: SAN IDELFONSO IXTAHUACAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_JUAN_ATITAN_LABEL: SAN JUAN ATITAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_JUAN_IXCOY_LABEL: SAN JUAN IXCOY
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_MATEO_IXTATAN_LABEL: SAN MATEO IXTATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_MIGUEL_ACATAN_LABEL: SAN MIGUEL ACATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_PEDRO_NECTA_LABEL: SAN PEDRO NECTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_RAFAEL_LA_INDEPENDENCIA_LABEL: SAN RAFAEL LA INDEPENDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_RAFAEL_PETZAL_LABEL: SAN RAFAEL PETZAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_SEBASTIAN_COATAN_LABEL: SAN SEBASTIAN COATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SAN_SEBASTIAN_HUEHUETENANGO_LABEL: SAN SEBASTIAN HUEHUETENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_SOLOMA_LABEL: SOLOMA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_TECTITAN_LABEL: TECTITAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_TODOS_SANTOS_CUCHUMATAN_LABEL: TODOS SANTOS CUCHUMATÁN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_ANSWER_UNION_CANTINIL_LABEL: UNION CANTINIL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_8_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_HUEHUETENANGO_QUESTION_SERVICIO_DE_SALUD_9_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_LABEL: IXCÁN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_9_ANSWER_INGENIEROS_LABEL: INGENIEROS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_9_ANSWER_PLAYA_GRANDE_LABEL: PLAYA GRANDE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_9_ANSWER_PUEBLO_NUEVO_LABEL: PUEBLO NUEVO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_9_ANSWER_TZETUN_LABEL: TZETUN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_9_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXCAN_QUESTION_SERVICIO_DE_SALUD_10_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXIL_LABEL: IXIL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXIL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_10_ANSWER_CHAJUL_LABEL: CHAJUL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXIL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_10_ANSWER_NEBAJ_LABEL: NEBAJ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXIL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_10_ANSWER_SAN_JUAN_COTZAL_LABEL: SAN JUAN COTZAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXIL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_10_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IXIL_QUESTION_SERVICIO_DE_SALUD_11_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_LABEL: IZABAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_EL_ESTOR_LABEL: EL ESTOR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_FRONTERA_RIO_DULCE_LABEL: FRONTERA RIO DULCE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_LIVINGSTON_LABEL: LIVINGSTON
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_LOS_AMATES_LABEL: LOS AMATES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_MORALES_LABEL: MORALES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_NAVAJOA_LABEL: NAVAJOA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_PUERTO_BARRIOS_LABEL: PUERTO BARRIOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_ANSWER_SANTO_TOMAS_DE_CASTILLA_LABEL: SANTO TOMAS DE CASTILLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_11_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_IZABAL_QUESTION_SERVICIO_DE_SALUD_12_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_LABEL: JALAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_JALAPA_LABEL: JALAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_MATAQUESCUINTLA_LABEL: MATAQUESCUINTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_MONJAS_LABEL: MONJAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_SANYUYO_LABEL: SANYUYO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_SAN_CARLOS_ALZATATE_LABEL: SAN CARLOS ALZATATE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_SAN_LUIS_JILOTEPEQUE_LABEL: SAN LUIS JILOTEPEQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_SAN_MANUEL_CHAPARRON_LABEL: SAN MANUEL CHAPARRON
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_ANSWER_SAN_PEDRO_PINULA_LABEL: SAN PEDRO PINULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_12_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JALAPA_QUESTION_SERVICIO_DE_SALUD_13_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_LABEL: JUTIAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_AGUA_BLANCA_LABEL: AGUA BLANCA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_ASUNCION_MITA_LABEL: ASUNCION MITA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_ATESCATEMPA_LABEL: ATESCATEMPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_CIUDAD_PEDRO_DE_ALVARADO_LABEL: CIUDAD PEDRO DE ALVARADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_COMAPA_LABEL: COMAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_CONGUACO_LABEL: CONGUACO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_EL_ADELANTO_LABEL: EL ADELANTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_EL_PROGRESO_LABEL: EL PROGRESO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_JALPATAGUA_LABEL: JALPATAGUA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_JEREZ_LABEL: JEREZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_JUTIAPA_LABEL: JUTIAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_LOS_ANONOS_LABEL: LOS ANONOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_MOYUTA_LABEL: MOYUTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_PASACO_LABEL: PASACO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_QUEZADA_LABEL: QUEZADA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_SANTA_CATARINA_MITA_LABEL: SANTA CATARINA MITA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_SAN_JOSE_ACATEMPA_LABEL: SAN JOSE ACATEMPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_YUPILTEPEQUE_LABEL: YUPILTEPEQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_ANSWER_ZAPOTITLAN_LABEL: ZAPOTITLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_13_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_JUTIAPA_QUESTION_SERVICIO_DE_SALUD_14_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_LABEL: PETÉN NORTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_ANSWER_FLORES_LABEL: FLORES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_ANSWER_MELCHOR_DE_MENCOS_LABEL: MELCHOR DE MENCOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_ANSWER_SAN_ANDRES_LABEL: SAN ANDRES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_ANSWER_SAN_BENITO_LABEL: SAN BENITO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_ANSWER_SAN_FRANCISCO_LABEL: SAN FRANCISCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_ANSWER_SAN_JOSE_LABEL: SAN JOSE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_14_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_NORTE_QUESTION_SERVICIO_DE_SALUD_15_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_LABEL: PETÉN SUR OCCIDENTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_ANSWER_EL_NARANJO_LABEL: EL NARANJO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_ANSWER_LAS_CRUCES_LABEL: LAS CRUCES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_ANSWER_LA_LIBERTAD_LABEL: LA LIBERTAD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_ANSWER_NUEVA_ESPERANZA_LABEL: NUEVA ESPERANZA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_ANSWER_SAYAXCHE_LABEL: SAYAXCHE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_ANSWER_TIERRA_BLANCA_LABEL: TIERRA BLANCA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_15_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_OCCIDENTE_QUESTION_SERVICIO_DE_SALUD_18_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_LABEL: PETÉN SUR ORIENTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_ANSWER_CHACTE_LABEL: CHACTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_ANSWER_DOLORES_LABEL: DOLORES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_ANSWER_EL_CHAL_LABEL: EL CHAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_ANSWER_POPTUN_LABEL: POPTUN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_ANSWER_SANTA_ANA_LABEL: SANTA ANA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_ANSWER_SAN_LUIS_LABEL: SAN LUIS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_16_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_PETEN_SUR_ORIENTE_QUESTION_SERVICIO_DE_SALUD_19_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_LABEL: QUETZALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_ALMOLONGA_LABEL: ALMOLONGA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_CABRICAN_LABEL: CABRICAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_CAJOLA_LABEL: CAJOLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_CANTEL_LABEL: CANTEL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_COATEPEQUE_LABEL: COATEPEQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_COLOMBA_LABEL: COLOMBA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_CONCEPCION_CHIQUIRICHAPA_LABEL: CONCEPCION CHIQUIRICHAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_EL_PALMAR_LABEL: EL PALMAR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_FLORES_COSTA_CUCA_LABEL: FLORES COSTA CUCA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_GENOVA_LABEL: GENOVA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_HUITAN_LABEL: HUITAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_LA_ESPERANZA_LABEL: LA ESPERANZA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_OLINTEPEQUE_LABEL: OLINTEPEQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_PALESTINA_DE_LOS_ALTOS_LABEL: PALESTINA DE LOS ALTOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_QUETZALTENANGO_LABEL: QUETZALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SALCAJA_LABEL: SALCAJA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SAN_CARLOS_SIJA_LABEL: SAN CARLOS SIJA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SAN_FRANCISCO_LA_UNION_LABEL: SAN FRANCISCO LA UNION
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SAN_JUAN_OSTUNCALCO_LABEL: SAN JUAN OSTUNCALCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SAN_MARTIN_SACATEPEQUEZ_LABEL: SAN MARTIN SACATEPEQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SAN_MATEO_LABEL: SAN MATEO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SAN_MIGUEL_SIGUILA_LABEL: SAN MIGUEL SIGUILA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_SIBILIA_LABEL: SIBILIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_ANSWER_ZUNIL_LABEL: ZUNIL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_17_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUETZALTENANGO_QUESTION_SERVICIO_DE_SALUD_20_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_LABEL: QUICHÉ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CANILLA_LABEL: CANILLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CHICAMAN_LABEL: CHICAMAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CHICHE_LABEL: CHICHE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CHICHICASTENANGO_LABEL: CHICHICASTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CHINIQUE_LABEL: CHINIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CHUPOL_LABEL: CHUPOL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_CUNEN_LABEL: CUNEN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_JOYABAJ_LABEL: JOYABAJ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_LA_PARROQUIA_LABEL: LA PARROQUIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_LA_TANA_LABEL: LA TAÑA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_PACHALUM_LABEL: PACHALUM
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_PATZITE_LABEL: PATZITE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_SACAPULAS_LABEL: SACAPULAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_SANTA_CRUZ_DEL_QUICHE_LABEL: SANTA CRUZ DEL QUICHE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_SAN_ANDRES_SAJCABAJA_LABEL: SAN ANDRES SAJCABAJA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_SAN_ANTONIO_ILOTENANGO_LABEL: SAN ANTONIO ILOTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_SAN_BARTOLOME_JOCOTENANGO_LABEL: SAN BARTOLOME JOCOTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_SAN_PEDRO_JOCOPILAS_LABEL: SAN PEDRO JOCOPILAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_USPANTAN_LABEL: USPANTAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_ANSWER_ZACUALPA_LABEL: ZACUALPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_18_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_QUICHE_QUESTION_SERVICIO_DE_SALUD_22_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_LABEL: RETALHULEU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_CABALLO_BLANCO_LABEL: CABALLO BLANCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_CHAMPERICO_LABEL: CHAMPERICO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_EL_ASINTAL_LABEL: EL ASINTAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_LA_MAQUINA_LABEL: LA MAQUINA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_NUEVO_SAN_CARLOS_LABEL: NUEVO SAN CARLOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_RETALHULEU_LABEL: RETALHULEU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_SANTA_CRUZ_MULUA_LABEL: SANTA CRUZ MULUA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_SAN_ANDRES_VILLA_SECA_LABEL: SAN ANDRES VILLA SECA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_SAN_FELIPE_LABEL: SAN FELIPE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_SAN_MARTIN_ZAPOTITLAN_LABEL: SAN MARTIN ZAPOTITLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_ANSWER_SAN_SEBASTIAN_LABEL: SAN SEBASTIAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_19_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_RETALHULEU_QUESTION_SERVICIO_DE_SALUD_23_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_LABEL: SACATEPÉQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_20_ANSWER_ANTIGUA_GUATEMALA_LABEL: ANTIGUA GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_20_ANSWER_SANTIAGO_SACATEPEQUEZ_LABEL: SANTIAGO SACATEPEQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_20_ANSWER_SAN_JUAN_ALOTENANGO_LABEL: SAN JUAN ALOTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_20_ANSWER_SUMPANGO_LABEL: SUMPANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_20_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SACATEPEQUEZ_QUESTION_SERVICIO_DE_SALUD_24_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_LABEL: SANTA ROSA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_BARBERENA_LABEL: BARBERENA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_CASILLAS_LABEL: CASILLAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_CHIQUIMULILLA_LABEL: CHIQUIMULILLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_CUILAPA_LABEL: CUILAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_GUAZACAPAN_LABEL: GUAZACAPAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_NUEVA_SANTA_ROSA_LABEL: NUEVA SANTA ROSA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_ORATORIO_LABEL: ORATORIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_PUEBLO_NUEVO_VINAS_LABEL: PUEBLO NUEVO VIÑAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_SANTA_CRUZ_NARANJO_LABEL: SANTA CRUZ NARANJO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_SANTA_MARIA_IXHUATAN_LABEL: SANTA MARIA IXHUATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_SANTA_ROSA_DE_LIMA_LABEL: SANTA ROSA DE LIMA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_SAN_JUAN_TECUACO_LABEL: SAN JUAN TECUACO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_SAN_RAFAEL_LAS_FLORES_LABEL: SAN RAFAEL LAS FLORES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_ANSWER_TAXISCO_LABEL: TAXISCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_22_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SANTA_ROSA_QUESTION_SERVICIO_DE_SALUD_26_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_LABEL: SAN MARCOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_COMITANCILLO_LABEL: COMITANCILLO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_CONCEPCION_TUTUAPA_LABEL: CONCEPCION TUTUAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_EL_QUETZAL_LABEL: EL QUETZAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_EL_RODEO_LABEL: EL RODEO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_EL_TUMBADOR_LABEL: EL TUMBADOR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_IXCHIGUAN_LABEL: IXCHIGUAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_LA_BLANCA_LABEL: LA BLANCA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_LA_REFORMA_LABEL: LA REFORMA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_MALACATAN_LABEL: MALACATAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_JOSE_OJETENAM_LABEL: SAN JOSE OJETENAM
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_LORENZO_LABEL: SAN LORENZO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_MARCOS_LABEL: SAN MARCOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_MIGUEL_IXTAHUACAN_LABEL: SAN MIGUEL IXTAHUACAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_PABLO_LABEL: SAN PABLO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_PEDRO_SACATEPEQUEZ_LABEL: SAN PEDRO SACATEPEQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SAN_RAFAEL_PIE_DE_LA_CUESTA_LABEL: SAN RAFAEL PIE DE LA CUESTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SIBINAL_LABEL: SIBINAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_SIPACAPA_LABEL: SIPACAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_TACANA_LABEL: TACANA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_TAJUMULCO_LABEL: TAJUMULCO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_TECUN_UMAN_LABEL: TECUN UMAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_ANSWER_TEJUTLA_LABEL: TEJUTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_21_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SAN_MARCOS_QUESTION_SERVICIO_DE_SALUD_25_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_LABEL: SOLOLÁ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_GUINEALES_LABEL: GUINEALES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_LA_CEIBA_LABEL: LA CEIBA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_NAHUALA_LABEL: NAHUALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_PANAJACHEL_LABEL: PANAJACHEL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SANTA_CATARINA_IXTAHUACAN_LABEL: SANTA CATARINA IXTAHUACAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SANTA_CLARA_LA_LAGUNA_LABEL: SANTA CLARA LA LAGUNA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SANTA_LUCIA_UTATLAN_LABEL: SANTA LUCIA UTATLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SANTIAGO_ATITLAN_LABEL: SANTIAGO ATITLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SAN_ANDRES_LABEL: SAN ANDRES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SAN_ANTONIO_LABEL: SAN ANTONIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SAN_JUAN_LA_LAGUNA_LABEL: SAN JUAN LA LAGUNA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SAN_LUCAS_TOLIMAN_LABEL: SAN LUCAS TOLIMAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SAN_PABLO_LA_LAGUNA_LABEL: SAN PABLO LA LAGUNA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SAN_PEDRO_LA_LAGUNA_LABEL: SAN PEDRO LA LAGUNA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_SOLOLA_LABEL: SOLOLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_ANSWER_XEJUYUP_BOCA_COSTA_DE_NAHUALA_LABEL: XEJUYUP BOCA COSTA DE NAHUALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_23_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SOLOLA_QUESTION_SERVICIO_DE_SALUD_27_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_LABEL: SUCHITEPÉQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_CHICACAO_LABEL: CHICACAO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_CUYOTENANGO_LABEL: CUYOTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_LA_MAQUINA_LABEL: LA MAQUINA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_MAZATENANGO_LABEL: MAZATENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_PATULUL_LABEL: PATULUL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_PUEBLO_NUEVO_LABEL: PUEBLO NUEVO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_RIO_BRAVO_LABEL: RIO BRAVO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAMAYAC_LABEL: SAMAYAC
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SANTA_BARBARA_LABEL: SANTA BARBARA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SANTO_DOMINGO_SUCHITEPEQUEZ_LABEL: SANTO DOMINGO SUCHITEPEQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SANTO_TOMAS_LA_UNION_LABEL: SANTO TOMAS LA UNION
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_ANTONIO_LABEL: SAN ANTONIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_BERNARDINO_LABEL: SAN BERNARDINO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_FRANCISCO_ZAPOTITLAN_LABEL: SAN FRANCISCO ZAPOTITLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_GABRIEL_LABEL: SAN GABRIEL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_JOSE_EL_IDOLO_LABEL: SAN JOSE EL IDOLO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_JUAN_BAUTISTA_LABEL: SAN JUAN BAUTISTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_LORENZO_LABEL: SAN LORENZO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_MIGUEL_PANAN_LABEL: SAN MIGUEL PANAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_SAN_PABLO_JOCOPILAS_LABEL: SAN PABLO JOCOPILAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_ANSWER_ZUNILITO_LABEL: ZUNILITO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_24_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_SUCHITEPEQUEZ_QUESTION_SERVICIO_DE_SALUD_28_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_LABEL: TOTONICAPAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_MOMOSTENANGO_LABEL: MOMOSTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SANTA_LUCIA_LA_REFORMA_LABEL: SANTA LUCIA LA REFORMA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SANTA_MARIA_CHIQUIMULA_LABEL: SANTA MARIA CHIQUIMULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SAN_ANDRES_XECUL_LABEL: SAN ANDRES XECUL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SAN_BARTOLO_AGUAS_CALIENTES_LABEL: SAN BARTOLO AGUAS CALIENTES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SAN_CRISTOBAL_TOTONICAPAN_LABEL: SAN CRISTOBAL TOTONICAPAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SAN_FRANCISCO_EL_ALTO_LABEL: SAN FRANCISCO EL ALTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_SAN_VICENTE_BUENABAJ_LABEL: SAN VICENTE BUENABAJ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_ANSWER_TOTONICAPAN_LABEL: TOTONICAPÁN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_25_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_TOTONICAPAN_QUESTION_SERVICIO_DE_SALUD_30_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_LABEL: ZACAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_CABANAS_LABEL: CABAÑAS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_ESTANZUELA_LABEL: ESTANZUELA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_GUALAN_LABEL: GUALAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_HUITE_LABEL: HUITE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_LA_UNION_LABEL: LA UNION
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_RIO_HONDO_LABEL: RIO HONDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_SAN_DIEGO_LABEL: SAN DIEGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_SAN_JORGE_LABEL: SAN JORGE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_TECULUTAN_LABEL: TECULUTAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_USUMATLAN_LABEL: USUMATLAN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_ANSWER_ZACAPA_LABEL: ZACAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_DISTRITO_MUNICIPAL_DE_SALUD_DMS_26_TEXT: DISTRITO MUNICIPAL DE SALUD (DMS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_ANSWER_ZACAPA_QUESTION_SERVICIO_DE_SALUD_31_TEXT: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_DIRECCION_DE_AREA_DE_SALUD_TEXT: DIRECCIÓN DEPARTAMENTAL DE REDES INTEGRADAS DE SERVICIOS DE SALUD (DDRISS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FECHA_DE_CONSULTA_TEXT: FECHA DE CONSULTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FECHA_DE_INVESTIGACION_DOMICILIARIA_TEXT: FECHA DE INVESTIGACIÓN DOMICILIARIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_AUTO_NOTIFICACION_POR_NUMERO_GRATUITO_LABEL: AUTO NOTIFICACIÓN POR NÚMERO GRATUITO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_BUSQUEDA_ACTIVA_COMUNITARIA_LABEL: BÚSQUEDA ACTIVA COMUNITARIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_BUSQUEDA_ACTIVA_INSTITUCIONAL_LABEL: BÚSQUEDA ACTIVA INSTITUCIONAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_BUSQUEDA_ACTIVA_LABORATORIAL_LABEL: BÚSQUEDA ACTIVA LABORATORIAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_CASO_REPORTADO_POR_LA_COMUNIDAD_LABEL: CASO REPORTADO POR LA COMUNIDAD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_INVESTIGACION_DE_CONTACTOS_LABEL: INVESTIGACIÓN DE CONTACTOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_LABORATORIO_LABEL: LABORATORIO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_OTRO_QUESTION_ESPECIFIQUE_FUENTE_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_ANSWER_SERVICIO_DE_SALUD_LABEL: SERVICIO DE SALUD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_FUENTE_DE_NOTIFICACION_TEXT: FUENTE DE NOTIFICACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_NOMBRE_DE_QUIEN_INVESTIGA_TEXT: NOMBRE DE QUIÉN INVESTIGA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_OTRO_ESTABLECIMIENTO_ANSWER_ESTABLECIMIENTO_PRIVADO_LABEL: ESTABLECIMIENTO PRIVADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_OTRO_ESTABLECIMIENTO_ANSWER_ESTABLECIMIENTO_PRIVADO_QUESTION_ESPECIFIQUE_PRIVADO_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_OTRO_ESTABLECIMIENTO_ANSWER_SEGURO_SOCIAL_IGSS_LABEL: SEGURO SOCIAL (IGSS)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_OTRO_ESTABLECIMIENTO_ANSWER_SEGURO_SOCIAL_IGSS_QUESTION_ESPECIFIQUE_ESTABLECIMIENTO_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_OTRO_ESTABLECIMIENTO_TEXT: SEGURO SOCIAL O ESTABLECIMIENTO PRIVADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_ANSWER_FECHA_DE_NOTIFICACION_QUESTION_TELEFONO_TEXT: TELEFONO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_NOTIFICACION_TEXT: DATOS DE LA UNIDAD NOTIFICADORA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_LABEL: DATOS GENERALES
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_DPI_LABEL: DPI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_DPI_QUESTION_NO_DE_DPI_TEXT: NO. DE DPI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_OTRO_QUESTION_ESPECIFIQUE_CUI_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_PASAPORTE_LABEL: PASAPORTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_PASAPORTE_QUESTION_NO_DE_PASAPORTE_TEXT: NO. DE PASAPORTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_TEXT: CÓDIGO ÚNICO DE IDENTIFICACIÓN (DPI, PASAPORTE, OTRO)

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_DIRECCION_DE_RESIDENCIA_TEXT: DIRECCIÓN DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_BASICOS_LABEL: BÁSICOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_DIVERSIFICADO_LABEL: DIVERSIFICADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_NINGUNO_LABEL: NINGUNO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_NO_APLICA_LABEL: NO APLICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_NO_INDICA_LABEL: NO INDICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_PRE_PRIMARIA_LABEL: PRE PRIMARIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_PRIMARIA_LABEL: PRIMARIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_ANSWER_UNIVERSIDAD_LABEL: UNIVERSIDAD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_ESCOLARIDAD_TEXT: ESCOLARIDAD
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_EXTRANJERO_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_EXTRANJERO_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_EXTRANJERO_TEXT: EXTRANJERO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_LUGAR_POBLADO_TEXT: LUGAR POBLADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_MIGRANTE_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_MIGRANTE_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_MIGRANTE_TEXT: MIGRANTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_NO_LABEL: NO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_LABEL: SI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_DPI_LABEL: DPI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_DPI_QUESTION_NO_DE_DPI_TEXT: NO. DE DPI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_OTRO_QUESTION_ESPECIFIQUE_DOC_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_PASAPORTE_LABEL: PASAPORTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_ANSWER_PASAPORTE_QUESTION_NO_DE_PASAPORTE_TEXT: NO. DE PASAPORTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_CODIGO_UNICO_DE_IDENTIFICACION_DPI_PASAPORTE_OTRO_TEXT: CODIGO ÚNICO DE IDENTIFICACIÓN DEL TUTOR (DPI, PASAPORTE, OTRO)
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_ANSWER_SI_QUESTION_PARENTESCO_TEXT: PARENTESCO DEL TUTOR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_NOMBRE_DEL_TUTOR_TEXT: TIENE TUTOR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_OCUPACION_TEXT: OCUPACIÓN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_LABEL: GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_LABEL: ALTA VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_CAHABON_LABEL: CAHABON

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_CHAHAL_LABEL: CHAHAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_CHISEC_LABEL: CHISEC

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_COBAN_LABEL: COBAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_FRAY_BARTOLOME_DE_LAS_CASAS_LABEL: FRAY BARTOLOME DE LAS CASAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_LANQUIN_LABEL: LANQUIN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_LA_TINTA_LABEL: LA TINTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_PANZOS_LABEL: PANZOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_RAXRUHA_LABEL: RAXRUHA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_SANTA_CRUZ_VERAPAZ_LABEL: SANTA CRUZ VERAPAZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_SAN_CRISTOBAL_VERAPAZ_LABEL: SAN CRISTOBAL VERAPAZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_SAN_JUAN_CHAMELCO_LABEL: SAN JUAN CHAMELCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_SAN_PEDRO_CARCHA_LABEL: SAN PEDRO CARCHA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_SENAHU_LABEL: SENAHU

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_TACTIC_LABEL: TACTIC

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_TAMAHU_LABEL: TAMAHU

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_ANSWER_TUCURU_LABEL: TUCURU

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ALTA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_LABEL: BAJA VERAPAZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_CUBULCO_LABEL: CUBULCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_EL_CHOL_LABEL: EL CHOL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_GRANADOS_LABEL: GRANADOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_PURULHA_LABEL: PURULHA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_RABINAL_LABEL: RABINAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_SALAMA_LABEL: SALAMA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_SAN_JERONIMO_LABEL: SAN JERONIMO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_ANSWER_SAN_MIGUEL_CHICAJ_LABEL: SAN MIGUEL CHICAJ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_BAJA_VERAPAZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_1_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_LABEL: CHIMALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_ACATENANGO_LABEL: ACATENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_CHIMALTENANGO_LABEL: CHIMALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_EL_TEJAR_LABEL: EL TEJAR
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_PARRAMOS_LABEL: PARRAMOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_PATZICIA_LABEL: PATZICIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_PATZUN_LABEL: PATZUN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_POCHUTA_LABEL: POCHUTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_SANTA_APOLONIA_LABEL: SANTA APOLONIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_SANTA_CRUZ_BALANYA_LABEL: SANTA CRUZ BALANYA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_SAN_ANDRES_ITZAPA_LABEL: SAN ANDRES ITZAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_SAN_JOSE_POAQUIL_LABEL: SAN JOSE POAQUIL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_SAN_JUAN_COMALAPA_LABEL: SAN JUAN COMALAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_SAN_MARTIN_JILOTEPEQUE_LABEL: SAN MARTIN JILOTEPEQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_TECPAN_GUATEMALA_LABEL: TECPAN GUATEMALA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_YEPOCAPA_LABEL: YEPOCAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_ANSWER_ZARAGOZA_LABEL: ZARAGOZA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIMALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_2_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_LABEL: CHIQUIMULA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_CAMOTAN_LABEL: CAMOTAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_CHIQUIMULA_LABEL: CHIQUIMULA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_CONCEPCION_LAS_MINAS_LABEL: CONCEPCION LAS MINAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_ESQUIPULAS_LABEL: ESQUIPULAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_IPALA_LABEL: IPALA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_JOCOTAN_LABEL: JOCOTAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_OLOPA_LABEL: OLOPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_QUETZALTEPEQUE_LABEL: QUETZALTEPEQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_SAN_JACINTO_LABEL: SAN JACINTO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_SAN_JOSE_LA_ARADA_LABEL: SAN JOSE LA ARADA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_ANSWER_SAN_JUAN_LA_ERMITA_LABEL: SAN JUAN LA ERMITA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_CHIQUIMULA_QUESTION_MUNICIPIO_DE_RESIDENCIA_3_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_LABEL: EL PROGRESO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_EL_JICARO_LABEL: EL JICARO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_GUASTATOYA_LABEL: GUASTATOYA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_MORAZAN_LABEL: MORAZAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_SANARATE_LABEL: SANARATE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_SANSARE_LABEL: SANSARE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_SAN_AGUSTIN_ACASAGUASTLAN_LABEL: SAN AGUSTIN ACASAGUASTLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_SAN_ANTONIO_LA_PAZ_LABEL: SAN ANTONIO LA PAZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_ANSWER_SAN_CRISTOBAL_ACASAGUASTLAN_LABEL: SAN CRISTOBAL ACASAGUASTLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_EL_PROGRESO_QUESTION_MUNICIPIO_DE_RESIDENCIA_4_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_LABEL: ESCUINTLA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_ESCUINTLA_LABEL: ESCUINTLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_GUANAGAZAPA_LABEL: GUANAGAZAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_IZTAPA_LABEL: IZTAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_LA_DEMOCRACIA_LABEL: LA DEMOCRACIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_LA_GOMERA_LABEL: LA GOMERA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_MASAGUA_LABEL: MASAGUA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_NUEVA_CONCEPCION_LABEL: NUEVA CONCEPCION

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_PALIN_LABEL: PALIN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_PUERTO_DE_SAN_JOSE_LABEL: PUERTO DE SAN JOSE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_SANTA_LUCIA_COTZUMALGUAPA_LABEL: SANTA LUCIA COTZUMALGUAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_SAN_VICENTE_PACAYA_LABEL: SAN VICENTE PACAYA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_SIPACATE_LABEL: SIPACATE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_SIQUINALA_LABEL: SIQUINALA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_ANSWER_TIQUISATE_LABEL: TIQUISATE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ESCUINTLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_5_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_LABEL: GUATEMALA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_AMATITLAN_LABEL: AMATITLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_CHINAUTLA_LABEL: CHINAUTLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_CHUARRANCHO_LABEL: CHUARRANCHO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_FRAIJANES_LABEL: FRAIJANES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_GUATEMALA_LABEL: GUATEMALA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_MIXCO_LABEL: MIXCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_PALENCIA_LABEL: PALENCIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SANTA_CATARINA_PINULA_LABEL: SANTA CATARINA PINULA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_JOSE_DEL_GOLFO_LABEL: SAN JOSE DEL GOLFO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_JOSE_PINULA_LABEL: SAN JOSE PINULA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_JUAN_SACATEPEQUEZ_LABEL: SAN JUAN SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_MIGUEL_PETAPA_LABEL: SAN MIGUEL PETAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_PEDRO_AYAMPUC_LABEL: SAN PEDRO AYAMPUC

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_PEDRO_SACATEPEQUEZ_LABEL: SAN PEDRO SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_SAN_RAYMUNDO_LABEL: SAN RAYMUNDO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_VILLA_CANALES_LABEL: VILLA CANALES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_ANSWER_VILLA_NUEVA_LABEL: VILLA NUEVA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_MUNICIPIO_DE_RESIDENCIA_6_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_LABEL: HUEHUETENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_AGUACATAN_LABEL: AGUACATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_BARILLAS_LABEL: BARILLAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_CHIANTLA_LABEL: CHIANTLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_COLOTENANGO_LABEL: COLOTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_CONCEPCION_HUISTA_LABEL: CONCEPCION HUISTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_CUILCO_LABEL: CUILCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_HUEHUETENANGO_LABEL: HUEHUETENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_IXTAHUACAN_LABEL: IXTAHUACAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_JACALTENANGO_LABEL: JACALTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_LA_DEMOCRACIA_LABEL: LA DEMOCRACIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_LA_LIBERTAD_LABEL: LA LIBERTAD

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_MALACATANCITO_LABEL: MALACATANCITO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_NENTON_LABEL: NENTON

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_PETATAN_LABEL: PETATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SANTA_ANA_HUISTA_LABEL: SANTA ANA HUISTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SANTA_BARBARA_LABEL: SANTA BARBARA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SANTA_EULALIA_LABEL: SANTA EULALIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SANTIAGO_CHIMALTENANGO_LABEL: SANTIAGO CHIMALTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_ANTONIO_HUISTA_LABEL: SAN ANTONIO HUISTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_GASPAR_IXCHIL_LABEL: SAN GASPAR IXCHIL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_JUAN_ATITAN_LABEL: SAN JUAN ATITAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_JUAN_IXCOY_LABEL: SAN JUAN IXCOY

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_MATEO_IXTATAN_LABEL: SAN MATEO IXTATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_MIGUEL_ACATAN_LABEL: SAN MIGUEL ACATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_PEDRO_NECTA_LABEL: SAN PEDRO NECTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_PEDRO_SOLOMA_LABEL: SAN PEDRO SOLOMA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_RAFAEL_LA_INDEPENDENCIA_LABEL: SAN RAFAEL LA INDEPENDENCIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_RAFAEL_PETZAL_LABEL: SAN RAFAEL PETZAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_SEBASTIAN_COATAN_LABEL: SAN SEBASTIAN COATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_SAN_SEBASTIAN_HUEHUETENANGO_LABEL: SAN SEBASTIAN HUEHUETENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_TECTITAN_LABEL: TECTITAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_TODOS_SANTOS_CUCHUMATAN_LABEL: TODOS SANTOS CUCHUMATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_ANSWER_UNION_CANTINIL_LABEL: UNION CANTINIL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_HUEHUETENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_7_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_LABEL: IZABAL
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_QUESTION_MUNICIPIO_DE_RESIDENCIA_8_ANSWER_EL_ESTOR_LABEL: EL ESTOR

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_QUESTION_MUNICIPIO_DE_RESIDENCIA_8_ANSWER_LIVINGSTON_LABEL: LIVINGSTON

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_QUESTION_MUNICIPIO_DE_RESIDENCIA_8_ANSWER_LOS_AMATES_LABEL: LOS AMATES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_QUESTION_MUNICIPIO_DE_RESIDENCIA_8_ANSWER_MORALES_LABEL: MORALES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_QUESTION_MUNICIPIO_DE_RESIDENCIA_8_ANSWER_PUERTO_BARRIOS_LABEL: PUERTO BARRIOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_IZABAL_QUESTION_MUNICIPIO_DE_RESIDENCIA_8_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_LABEL: JALAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_JALAPA_LABEL: JALAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_MATAQUESCUINTLA_LABEL: MATAQUESCUINTLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_MONJAS_LABEL: MONJAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_SAN_CARLOS_ALZATATE_LABEL: SAN CARLOS ALZATATE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_SAN_LUIS_JILOTEPEQUE_LABEL: SAN LUIS JILOTEPEQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_SAN_MANUEL_CHAPARRON_LABEL: SAN MANUEL CHAPARRON

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_ANSWER_SAN_PEDRO_PINULA_LABEL: SAN PEDRO PINULA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JALAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_9_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_LABEL: JUTIAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_AGUA_BLANCA_LABEL: AGUA BLANCA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_ASUNCION_MITA_LABEL: ASUNCION MITA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_ATESCATEMPA_LABEL: ATESCATEMPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_COMAPA_LABEL: COMAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_CONGUACO_LABEL: CONGUACO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_EL_ADELANTO_LABEL: EL ADELANTO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_EL_PROGRESO_LABEL: EL PROGRESO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_JALPATAGUA_LABEL: JALPATAGUA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_JEREZ_LABEL: JEREZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_JUTIAPA_LABEL: JUTIAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_MOYUTA_LABEL: MOYUTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_PASACO_LABEL: PASACO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_QUESADA_LABEL: QUESADA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_SANTA_CATARINA_MITA_LABEL: SANTA CATARINA MITA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_SAN_JOSE_ACATEMPA_LABEL: SAN JOSE ACATEMPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_YUPILTEPEQUE_LABEL: YUPILTEPEQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_ANSWER_ZAPOTITLAN_LABEL: ZAPOTITLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_JUTIAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_10_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_LABEL: PETÉN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_DOLORES_LABEL: DOLORES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_EL_CHAL_LABEL: EL CHAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_FLORES_LABEL: FLORES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_LAS_CRUCES_LABEL: LAS CRUCES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_LA_LIBERTAD_LABEL: LA LIBERTAD

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_MELCHOR_DE_MENCOS_LABEL: MELCHOR DE MENCOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_POPTUN_LABEL: POPTUN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SANTA_ANA_LABEL: SANTA ANA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SAN_ANDRES_LABEL: SAN ANDRES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SAN_BENITO_LABEL: SAN BENITO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SAN_FRANCISCO_LABEL: SAN FRANCISCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SAN_JOSE_LABEL: SAN JOSE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SAN_LUIS_LABEL: SAN LUIS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_ANSWER_SAYAXCHE_LABEL: SAYAXCHE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_PETEN_QUESTION_MUNICIPIO_DE_RESIDENCIA_11_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_LABEL: QUETZALTENANGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_ALMOLONGA_LABEL: ALMOLONGA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_CABRICAN_LABEL: CABRICAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_CAJOLA_LABEL: CAJOLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_CANTEL_LABEL: CANTEL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_COATEPEQUE_LABEL: COATEPEQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_COLOMBA_LABEL: COLOMBA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_CONCEPCION_CHIQUIRICHAPA_LABEL: CONCEPCION CHIQUIRICHAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_EL_PALMAR_LABEL: EL PALMAR

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_FLORES_COSTA_CUCA_LABEL: FLORES COSTA CUCA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_GENOVA_LABEL: GENOVA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_HUITAN_LABEL: HUITAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_LA_ESPERANZA_LABEL: LA ESPERANZA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_OLINTEPEQUE_LABEL: OLINTEPEQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_PALESTINA_DE_LOS_ALTOS_LABEL: PALESTINA DE LOS ALTOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_QUETZALTENANGO_LABEL: QUETZALTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SALCAJA_LABEL: SALCAJA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SAN_CARLOS_SIJA_LABEL: SAN CARLOS SIJA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SAN_FRANCISCO_LA_UNION_LABEL: SAN FRANCISCO LA UNION

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SAN_JUAN_OSTUNCALCO_LABEL: SAN JUAN OSTUNCALCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SAN_MARTIN_SACATEPEQUEZ_LABEL: SAN MARTIN SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SAN_MATEO_LABEL: SAN MATEO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SAN_MIGUEL_SIGUILA_LABEL: SAN MIGUEL SIGÜILA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_SIBILIA_LABEL: SIBILIA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_ANSWER_ZUNIL_LABEL: ZUNIL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUETZALTENANGO_QUESTION_MUNICIPIO_DE_RESIDENCIA_12_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_LABEL: QUICHÉ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CANILLA_LABEL: CANILLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CHAJUL_LABEL: CHAJUL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CHICAMAN_LABEL: CHICAMAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CHICHE_LABEL: CHICHE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CHICHICASTENANGO_LABEL: CHICHICASTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CHINIQUE_LABEL: CHINIQUE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_CUNEN_LABEL: CUNEN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_IXCAN_LABEL: IXCAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_JOYABAJ_LABEL: JOYABAJ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_NEBAJ_LABEL: NEBAJ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_PACHALUN_LABEL: PACHALUN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_PATZITE_LABEL: PATZITE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SACAPULAS_LABEL: SACAPULAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SANTA_CRUZ_DEL_QUICHE_LABEL: SANTA CRUZ DEL QUICHE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SAN_ANDRES_SAJCABAJA_LABEL: SAN ANDRES SAJCABAJA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SAN_ANTONIO_ILOTENANGO_LABEL: SAN ANTONIO ILOTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SAN_BARTOLOME_JOCOTENANGO_LABEL: SAN BARTOLOME JOCOTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SAN_JUAN_COTZAL_LABEL: SAN JUAN COTZAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SAN_MIGUEL_USPANTAN_LABEL: SAN MIGUEL USPANTAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_SAN_PEDRO_JOCOPILAS_LABEL: SAN PEDRO JOCOPILAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_ANSWER_ZACUALPA_LABEL: ZACUALPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_QUICHE_QUESTION_MUNICIPIO_DE_RESIDENCIA_13_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_LABEL: RETALHULEU
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_CHAMPERICO_LABEL: CHAMPERICO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_EL_ASINTAL_LABEL: EL ASINTAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_NUEVO_SAN_CARLOS_LABEL: NUEVO SAN CARLOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_RETALHULEU_LABEL: RETALHULEU

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_SANTA_CRUZ_MULUA_LABEL: SANTA CRUZ MULUA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_SAN_ANDRES_VILLA_SECA_LABEL: SAN ANDRES VILLA SECA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_SAN_FELIPE_LABEL: SAN FELIPE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_SAN_MARTIN_ZAPOTITLAN_LABEL: SAN MARTIN ZAPOTITLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_ANSWER_SAN_SEBASTIAN_LABEL: SAN SEBASTIAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_RETALHULEU_QUESTION_MUNICIPIO_DE_RESIDENCIA_14_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_LABEL: SACATEPÉQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_ALOTENANGO_LABEL: ALOTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_ANTIGUA_GUATEMALA_LABEL: ANTIGUA GUATEMALA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_CIUDAD_VIEJA_LABEL: CIUDAD VIEJA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_JOCOTENANGO_LABEL: JOCOTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_MAGDALENA_MILPAS_ALTAS_LABEL: MAGDALENA MILPAS ALTAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_PASTORES_LABEL: PASTORES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SANTA_CATARINA_BARAHONA_LABEL: SANTA CATARINA BARAHONA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SANTA_LUCIA_MILPAS_ALTAS_LABEL: SANTA LUCIA MILPAS ALTAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SANTA_MARIA_DE_JESUS_LABEL: SANTA MARIA DE JESUS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SANTIAGO_SACATEPEQUEZ_LABEL: SANTIAGO SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SANTO_DOMINGO_XENACOJ_LABEL: SANTO DOMINGO XENACOJ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SAN_ANTONIO_AGUAS_CALIENTES_LABEL: SAN ANTONIO AGUAS CALIENTES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SAN_BARTOLOME_MILPAS_ALTAS_LABEL: SAN BARTOLOME MILPAS ALTAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SAN_LUCAS_SACATEPEQUEZ_LABEL: SAN LUCAS SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SAN_MIGUEL_DUENAS_LABEL: SAN MIGUEL DUEÑAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_ANSWER_SUMPANGO_LABEL: SUMPANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SACATEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_15_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_LABEL: SANTA ROSA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_BARBERENA_LABEL: BARBERENA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_CASILLAS_LABEL: CASILLAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_CHIQUIMULILLA_LABEL: CHIQUIMULILLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_CUILAPA_LABEL: CUILAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_GUAZACAPAN_LABEL: GUAZACAPAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_NUEVA_SANTA_ROSA_LABEL: NUEVA SANTA ROSA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_ORATORIO_LABEL: ORATORIO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_PUEBLO_NUEVO_VINAS_LABEL: PUEBLO NUEVO VIÑAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_SANTA_CRUZ_NARANJO_LABEL: SANTA CRUZ NARANJO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_SANTA_MARIA_IXHUATAN_LABEL: SANTA MARIA IXHUATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_SANTA_ROSA_DE_LIMA_LABEL: SANTA ROSA DE LIMA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_SAN_JUAN_TECUACO_LABEL: SAN JUAN TECUACO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_SAN_RAFAEL_LAS_FLORES_LABEL: SAN RAFAEL LAS FLORES

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_ANSWER_TAXISCO_LABEL: TAXISCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SANTA_ROSA_QUESTION_MUNICIPIO_DE_RESIDENCIA_17_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_LABEL: SAN MARCOS
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_AYUTLA_LABEL: AYUTLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_CATARINA_LABEL: CATARINA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_COMITANCILLO_LABEL: COMITANCILLO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_CONCEPCION_TUTUAPA_LABEL: CONCEPCION TUTUAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_EL_QUETZAL_LABEL: EL QUETZAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_EL_RODEO_LABEL: EL RODEO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_EL_TUMBADOR_LABEL: EL TUMBADOR

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_ESQUIPULAS_PALO_GORDO_LABEL: ESQUIPULAS PALO GORDO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_IXCHIGUAN_LABEL: IXCHIGUAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_LA_BLANCA_LABEL: LA BLANCA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_LA_REFORMA_LABEL: LA REFORMA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_MALACATAN_LABEL: MALACATAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_NUEVO_PROGRESO_LABEL: NUEVO PROGRESO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_OCOS_LABEL: OCOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_PAJAPITA_LABEL: PAJAPITA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_RIO_BLANCO_LABEL: RIO BLANCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_ANTONIO_SACATEPEQUEZ_LABEL: SAN ANTONIO SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_CRISTOBAL_CUCHO_LABEL: SAN CRISTOBAL CUCHO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_JOSE_OJETENAM_LABEL: SAN JOSE OJETENAM

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_LORENZO_LABEL: SAN LORENZO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_MARCOS_LABEL: SAN MARCOS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_MIGUEL_IXTAHUACAN_LABEL: SAN MIGUEL IXTAHUACAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_PABLO_LABEL: SAN PABLO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_PEDRO_SACATEPEQUEZ_LABEL: SAN PEDRO SACATEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SAN_RAFAEL_PIE_DE_LA_CUESTA_LABEL: SAN RAFAEL PIE DE LA CUESTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SIBINAL_LABEL: SIBINAL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_SIPACAPA_LABEL: SIPACAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_TACANA_LABEL: TACANA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_TAJUMULCO_LABEL: TAJUMULCO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_ANSWER_TEJUTLA_LABEL: TEJUTLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SAN_MARCOS_QUESTION_MUNICIPIO_DE_RESIDENCIA_16_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_LABEL: SOLOLÁ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_CONCEPCION_LABEL: CONCEPCION

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_NAHUALA_LABEL: NAHUALA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_PANAJACHEL_LABEL: PANAJACHEL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTA_CATARINA_IXTAHUACAN_LABEL: SANTA CATARINA IXTAHUACAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTA_CATARINA_PALOPO_LABEL: SANTA CATARINA PALOPO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTA_CLARA_LA_LAGUNA_LABEL: SANTA CLARA LA LAGUNA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTA_CRUZ_LA_LAGUNA_LABEL: SANTA CRUZ LA LAGUNA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTA_LUCIA_UTATLAN_LABEL: SANTA LUCIA UTATLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTA_MARIA_VISITACION_LABEL: SANTA MARIA VISITACION

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SANTIAGO_ATITLAN_LABEL: SANTIAGO ATITLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_ANDRES_SEMETABAJ_LABEL: SAN ANDRES SEMETABAJ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_ANTONIO_PALOPO_LABEL: SAN ANTONIO PALOPO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_JOSE_CHACAYA_LABEL: SAN JOSE CHACAYA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_JUAN_LA_LAGUNA_LABEL: SAN JUAN LA LAGUNA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_LUCAS_TOLIMAN_LABEL: SAN LUCAS TOLIMAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_MARCOS_LA_LAGUNA_LABEL: SAN MARCOS LA LAGUNA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_PABLO_LA_LAGUNA_LABEL: SAN PABLO LA LAGUNA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SAN_PEDRO_LA_LAGUNA_LABEL: SAN PEDRO LA LAGUNA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_ANSWER_SOLOLA_LABEL: SOLOLA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SOLOLA_QUESTION_MUNICIPIO_DE_RESIDENCIA_18_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_LABEL: SUCHITEPÉQUEZ
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_CHICACAO_LABEL: CHICACAO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_CUYOTENANGO_LABEL: CUYOTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_MAZATENANGO_LABEL: MAZATENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_PATULUL_LABEL: PATULUL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_PUEBLO_NUEVO_LABEL: PUEBLO NUEVO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_RIO_BRAVO_LABEL: RIO BRAVO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAMAYAC_LABEL: SAMAYAC

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SANTA_BARBARA_LABEL: SANTA BARBARA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SANTO_DOMINGO_SUCHITEPEQUEZ_LABEL: SANTO DOMINGO SUCHITEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SANTO_TOMAS_LA_UNION_LABEL: SANTO TOMAS LA UNION

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_ANTONIO_SUCHITEPEQUEZ_LABEL: SAN ANTONIO SUCHITEPEQUEZ

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_BERNARDINO_LABEL: SAN BERNARDINO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_FRANCISCO_ZAPOTITLAN_LABEL: SAN FRANCISCO ZAPOTITLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_GABRIEL_LABEL: SAN GABRIEL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_JOSE_EL_IDOLO_LABEL: SAN JOSE EL IDOLO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_JOSE_LA_MAQUINA_LABEL: SAN JOSE LA MAQUINA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_JUAN_BAUTISTA_LABEL: SAN JUAN BAUTISTA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_LORENZO_LABEL: SAN LORENZO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_MIGUEL_PANAN_LABEL: SAN MIGUEL PANAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_SAN_PABLO_JOCOPILAS_LABEL: SAN PABLO JOCOPILAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_ANSWER_ZUNILITO_LABEL: ZUNILITO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_SUCHITEPEQUEZ_QUESTION_MUNICIPIO_DE_RESIDENCIA_19_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_LABEL: TOTONICAPÁN
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_MOMOSTENANGO_LABEL: MOMOSTENANGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_SANTA_LUCIA_LA_REFORMA_LABEL: SANTA LUCIA LA REFORMA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_SANTA_MARIA_CHIQUIMULA_LABEL: SANTA MARIA CHIQUIMULA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_SAN_ANDRES_XECUL_LABEL: SAN ANDRES XECUL

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_SAN_BARTOLO_LABEL: SAN BARTOLO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_SAN_CRISTOBAL_TOTONICAPAN_LABEL: SAN CRISTOBAL TOTONICAPAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_SAN_FRANCISCO_EL_ALTO_LABEL: SAN FRANCISCO EL ALTO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_ANSWER_TOTONICAPAN_LABEL: TOTONICAPAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_TOTONICAPAN_QUESTION_MUNICIPIO_DE_RESIDENCIA_20_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_LABEL: ZACAPA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_CABANAS_LABEL: CABAÑAS

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_ESTANZUELA_LABEL: ESTANZUELA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_GUALAN_LABEL: GUALAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_HUITE_LABEL: HUITE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_LA_UNION_LABEL: LA UNION

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_RIO_HONDO_LABEL: RIO HONDO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_SAN_DIEGO_LABEL: SAN DIEGO

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_SAN_JORGE_LABEL: SAN JORGE

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_TECULUTAN_LABEL: TECULUTAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_USUMATLAN_LABEL: USUMATLAN

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_ANSWER_ZACAPA_LABEL: ZACAPA

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_ANSWER_ZACAPA_QUESTION_MUNICIPIO_DE_RESIDENCIA_21_TEXT: MUNICIPIO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_GUATEMALA_QUESTION_DEPARTAMENTO_DE_RESIDENCIA_TEXT: DEPARTAMENTO DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_OTRO_LABEL: OTRO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_ANSWER_OTRO_QUESTION_ESPECIFIQUE_PAIS_TEXT: ESPECIFIQUE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PAIS_DE_RESIDENCIA_TEXT: PAÍS DE RESIDENCIA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_GARIFUNA_LABEL: GARÍFUNA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_LADINO_LABEL: LADINO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_LABEL: MAYA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_ACHI_LABEL: Achi´
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_AKATEKA_LABEL: Akateka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_AWAKATEKA_LABEL: Awakateka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_CHALCHITEKA_LABEL: Chalchiteka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_CHORTI_LABEL: Ch’orti’
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_CHUJ_LABEL: Chuj
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_ITZA_LABEL: Itza’
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_IXIL_LABEL: Ixil
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_JAKALTEKA_LABEL: Jakalteka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_KAQCHIKEL_LABEL: Kaqchikel
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_K_ICHE_LABEL: K´iche´
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_MAM_LABEL: Mam
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_MOPAN_LABEL: Mopan
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_NO_INDICA_LABEL: No indica
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_POCOMCHI_LABEL: Pocomchi’
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_POQOMAM_LABEL: Poqomam
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_QANJOBAL_LABEL: Q’anjob’al
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_QEQCHI_LABEL: Q'eqchi'
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_SAKAPULTEKA_LABEL: Sakapulteka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_SIPAKAPENSA_LABEL: Sipakapensa
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_TEKTITEKA_LABEL: Tektiteka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_TZUTUJIL_LABEL: Tz’utujil
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_ANSWER_USPANTEKA_LABEL: Uspanteka
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_MAYA_QUESTION_COMUNIDAD_LINGUISTICA_TEXT: COMUNIDAD LINGUÍSTICA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_ANSWER_XINCA_LABEL: XINCA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_PUEBLO_TEXT: PUEBLO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_ANSWER_DATOS_GENERALES_QUESTION_TELEFONO_TEXT: TELÉFONO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_INFORMACION_DEL_PACIENTE_TEXT: INFORMACIÓN DEL PACIENTE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_LABEL: SE INVESTIGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_DIRECCION_DEL_LUGAR_Y_RUTAS_DE_DESPLAZAMIENTO_1_TEXT: DIRECCIÓN DEL LUGAR Y RUTAS DE DESPLAZAMIENTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_FECHA_DE_ABORDAJE_1_TEXT: FECHA DE ABORDAJE
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_FECHA_EN_QUE_VISITO_EL_LUGAR_RUTA_1_TEXT: FECHAS EN QUE VISITÓ EL LUGAR / RUTA
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_SITIO_RUTA_DE_DESPLAZAMIENTO_1_TEXT: SITIO/RUTA DE DESPLAZAMIENTO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_1_ANSWER_3_LABEL: BAC
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_1_ANSWER_4_LABEL: BAI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_1_ANSWER_BARRIDO_LABEL: BARRIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_1_ANSWER_BLOQUEO_LABEL: BLOQUEO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_1_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_1_TEXT: TIPO DE ABORDAJE REALIZADO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_LABEL: NO SÉ INVESTIGO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_DIRECCION_DEL_LUGAR_Y_RUTAS_DE_DESPLAZAMIENTO_2_TEXT: Dirección del lugar y rutas de desplazamiento
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_FECHA_DE_ABORDAJE_2_TEXT: Fecha de abordaje 
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_FECHA_EN_QUE_VISITO_EL_LUGAR_RUTA_2_TEXT: Fecha en que visitó el lugar/ruta 
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_SITIO_RUTA_DE_DESPLAZAMIENTO_2_TEXT: Sitio/ruta de desplazamiento
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_2_ANSWER_1_LABEL: Bloqueo
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_2_ANSWER_2_LABEL: Barrido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_2_ANSWER_3_LABEL: BAC
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_2_ANSWER_4_LABEL: BAI
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_2_QUESTION_TIPO_DE_ABORDAJE_REALIZADO_2_TEXT: Tipo de abordaje realizado
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_ANSWER_DESCONOCIDO_LABEL: DESCONOCIDO
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CASEINVESTIGATIONTEMPLATE_QUESTION_LUGARES_VISITADOS_Y_RUTAS_DE_DESPLAZAMIENTO_DEL_CASO_TEXT: LUGARES VISITADOS Y RUTAS DE DESPLAZAMIENTO DEL CASO
```

## 4. Plantilla de Investigacion de Contactos

Total preguntas: 5

#### `visita_a_de_investigacion_de_contactos_directos`
- **Texto**: Visita a de investigación de contactos directos
- **Tipo**: SINGLE_ANSWER
- **Opciones**:
  - `"1"` = Si
  - `"2"` = No

#### `fecha_de_investigacion_de_contactos_directos`
- **Texto**: Fecha de investigación de contactos directos
- **Tipo**: DATE_TIME

#### `antecedente_vacunal_sr_o_spr`
- **Texto**: Antecedente vacunal (SR o SPR)

- **Tipo**: SINGLE_ANSWER
- **Opciones**:
  - `"1"` = Desconocido
  - `"2"` = 0 dosis
  - `"3"` = 1 dosis
  - `"4"` = 2 dosis

#### `signos_segun_definicion_de_caso`
- **Texto**: Signos según definición de caso
- **Tipo**: MULTIPLE_ANSWERS
- **Opciones**:
  - `"1"` = Fiebre
  - `"2"` = Exantema
  - `"3"` = No

#### `contacto_vacunado_durante_la_investigacion`
- **Texto**: Contacto vacunado durante la investigación
- **Tipo**: SINGLE_ANSWER
- **Opciones**:
  - `"1"` = Si
  - `"2"` = No

### 4.1 Tokens de Contactos

```
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTE_VACUNAL_SR_O_SPR_ANSWER_1_LABEL: Desconocido
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTE_VACUNAL_SR_O_SPR_ANSWER_2_LABEL: 0 dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTE_VACUNAL_SR_O_SPR_ANSWER_3_LABEL: 1 dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTE_VACUNAL_SR_O_SPR_ANSWER_4_LABEL: 2 dosis
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_ANTECEDENTE_VACUNAL_SR_O_SPR_TEXT: Antecedente vacunal (SR o SPR)

LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_CONTACTO_VACUNADO_DURANTE_LA_INVESTIGACION_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_CONTACTO_VACUNADO_DURANTE_LA_INVESTIGACION_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_CONTACTO_VACUNADO_DURANTE_LA_INVESTIGACION_TEXT: Contacto vacunado durante la investigación
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_FECHA_DE_INVESTIGACION_DE_CONTACTOS_DIRECTOS_TEXT: Fecha de investigación de contactos directos
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_SIGNOS_SEGUN_DEFINICION_DE_CASO_ANSWER_1_LABEL: Fiebre
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_SIGNOS_SEGUN_DEFINICION_DE_CASO_ANSWER_2_LABEL: Exantema
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_SIGNOS_SEGUN_DEFINICION_DE_CASO_ANSWER_3_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_SIGNOS_SEGUN_DEFINICION_DE_CASO_TEXT: Signos según definición de caso
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_VISITA_A_DE_INVESTIGACION_DE_CONTACTOS_DIRECTOS_ANSWER_1_LABEL: Si
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_VISITA_A_DE_INVESTIGACION_DE_CONTACTOS_DIRECTOS_ANSWER_2_LABEL: No
LNG_OUTBREAK_BA06833F-3B4D-4BD5-B4DD-4B27A8C20F19_CONTACTINVESTIGATIONTEMPLATE_QUESTION_VISITA_A_DE_INVESTIGACION_DE_CONTACTOS_DIRECTOS_TEXT: Visita a de investigación de contactos directos
```

## 5. Datos de Referencia (Reference Data)

### 5.1 Genero

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_GENDER_FEMALE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE` | SI |  |

### 5.2 Clasificacion de Caso

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT` | SI | #f0b341 |
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMED` | SI | #f41818 |
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_PROBABLE` | SI | #5b50ec |
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_NOT_A_CASE_DISCARDED` | SI | #a59c9c |
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SOSPECHOSO_DESCARTADO` | NO | #49ae00 |
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_CONFIRMADO_POR_NEXO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SOSPECHOSO_E` | NO |  |

### 5.3 Desenlace (Outcome)

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OUTCOME_DECEASED` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OUTCOME_RECOVERED` | SI |  |

### 5.4 Estado de Embarazo

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NONE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NOT_PREGNANT` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NO_APLICA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NO_SABE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_FIRST_TRIMESTER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_SECOND_TRIMESTER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_THIRD_TRIMESTER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_YES_TRIMESTER_UNKNOWN` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_DESCONOCIDO` | SI |  |

### 5.5 Ocupacion

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_ALBANIL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_BUTCHER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_CALL_CENTER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_CHILD` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_CIVIL_SERVANT` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_DEPENDIENTE_DE_TIENDA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_FARMER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_FORESTRY` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HEALTH_CARE_WORKER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HEALTH_LABORATORY_WORKER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HOTELERIA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_HOTELERIA_RESTAURANTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_LIMPIEZA_DOMESTICA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_MAQUILA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_MINING` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_OFICINA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_OTHER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_RELIGIOUS_LEADER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_STUDENT` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_TAXI_DRIVER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_TEACHER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_TRADITIONAL_HEALER` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_UNKNOWN` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_OCCUPATION_WORKING_WITH_ANIMALS` | NO |  |

### 5.6 Tipo de Documento

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_NATIONAL_ID_CARD` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_PASSPORT` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_OTHER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_ARCHIVED_ID` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_EXTERNAL_ID` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_VACCINATION_CARD` | NO |  |

### 5.7 Vacunas

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_VACCINE_INFLUENZA` | NO | #ffffff |
| `LNG_REFERENCE_DATA_CATEGORY_VACCINE_SPR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_VACCINE_SPRV` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_VACCINE_SR` | SI |  |

### 5.8 Estado de Vacunacion

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_VACCINE_STATUS_VACCINATED` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_VACCINE_STATUS_NOT_VACCINATED` | SI |  |

### 5.9 Tipo de Prueba de Laboratorio

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PCR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_RT_PCR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_IG_C_OR_IG_M` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PARTIAL_GENOME_SEQUENCING` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_IG_M_RUBEOLA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_IG_G` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_WHOLE_GENOME_SEQUENCING` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_IG_G_RUBEOLA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PRUEBA_DE_ANTPIGENO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_AVIDEZ` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_AVIDEZ_RUBEOLA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_OTHER_SPECIFY_IN_NOTES_FIELD` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_ANTIGEN_DETECTED` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_HISTOPATHOLOGY` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_VIRUS_CULTURE` | NO |  |

### 5.10 Resultado de Laboratorio

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_MUESTRA_INADECUADA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_INVALIDO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_NO_FUE_PROCESADA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_ALTA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_BAJA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE_FOR_OTHER_PATHOGENS_SPECIFY_IN_NOTES_FIELD` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_NEGATIVE` | SI |  |

### 5.11 Estado del Resultado de Lab

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_STATUS_IN_PROGRESS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_STATUS_COMPLETED` | SI |  |

### 5.12 Tipo de Muestra

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_FARINGEO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_NASAL` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_FAECES` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SERUM` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_NASOFARINGEO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_PLEURAL_FLUID` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_URINE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_LIQUIDO_CEFALORRAQUIDEO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SPUTUM` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BIOPSIA_DE_CEREBRO_BULBO_MEDULA_ESPINAL` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_OTHER_SPECIFY_IN_NOTES_FIELD` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_INTESTINO_DELGADO_FALLECIDO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SEGMENTO_DE_NERVIO_AFECTADO_FALLECIDO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BLOOD` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_CSF` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_ENDOTRACHEAL_ASPIRATE` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SKIN_BIOPSY` | NO |  |

### 5.13 Nombre de Laboratorio

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_LAB_NAME_LABORATORIO_NACIONAL_DE_SALUD_LNS` | SI |  |

### 5.14 Nivel de Riesgo

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_1_LOW` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_2_MEDIUM` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_3_HIGH` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_DOMICILIAR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_ESCOLAR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_INSTITUCIONES_DE_CUIDADO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_LABORAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_REUNION_SOCIAL` | SI |  |

### 5.15 Tipo de Direccion

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_USUAL_PLACE_OF_RESIDENCE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_PREVIOUS_USUAL_PLACE_OF_RESIDENCE` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_DIRECCION_DE_EVENTO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_UBICACION_DE_UNIDAD_NOTIFICADORA_SEGUN_EL_MSPAS` | NO |  |

### 5.16 Nivel de Certeza (Tipo de Contacto)

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_DOMICILIAR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_ESCOLAR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_INSTITUCIONES_DE_CUIDADO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_LABORAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_REUNION_SOCIAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_1_LOW` | NO | #ffffff |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_2_MEDIUM` | NO | #ffffff |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_3_HIGH` | NO | #ffffff |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_CONTACTO_DIRECTO_PERMANECE_EN_EL_MISMO_ENTORNO_CERCANO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_CONTACTO_INDIRECTO_VIAJAR_JUNTOS_1_METRO` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_PERSONA_QUE_BRINDA_ATENCION_SIN_EPP` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_MIGRANTE` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_VIVE_EN_EL_MISMO_LUGAR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_CONTACTO_CERCANO_MENOS_DE_1_5_MTS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CERTAINTY_LEVEL_BRINDA_ATENCION_SIN_EPP` | SI |  |

### 5.17 Estado de Investigacion

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_INVESTIGATION_STATUS_COMPLETE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INVESTIGATION_STATUS_IN_PROGRESS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INVESTIGATION_STATUS_NOT_REACHED` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INVESTIGATION_STATUS_REACHED` | SI |  |

### 5.18 Institucion (DAS/Hospital)

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_ALTA_VERAPAZ` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_BAJA_VERAPAZ` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_CHIMALTENANGO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_CHIQUIMULA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_EL_PROGRESO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_ESCUINTLA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_GUATEMALA_CENTRAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_GUATEMALA_NOR_OCCIDENTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_GUATEMALA_NOR_ORIENTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_GUATEMALA_SUR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_HUEHUETENANGO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_IXCAN` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_IXIL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_IZABAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_JALAPA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_JUTIAPA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_PETEN_NORTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_PETEN_SUR_OCCIDENTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_PETEN_SUR_ORIENTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_QUETZALTENANGO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_QUICHE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_RETALHULEU` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_SACATEPEQUEZ` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_SANTA_ROSA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_SAN_MARCOS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_SOLOLA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_SUCHITEPEQUEZ` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_TOTONICAPAN` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_DAS_ZACAPA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_GENERIC` | SI | #007c0a |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_HOSPITAL_PRIVADO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_IGSS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_PRUEBA_PILOTO` | SI | #1b0290 |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_PRUEBA_PILOTO_MSPAS` | SI | #f27613 |
| `LNG_REFERENCE_DATA_CATEGORY_INSTITUTION_NAME_USUARIOS_PARA_ENTRENAMIENTO_MSPAS` | SI | #009d8a |

### 5.19 Enfermedad

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_2019_N_CO_V` | SI | #ed0000 |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_RUBEOLA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_ACUTE_RESPIRATORY_DISEASE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_CHOLERA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_EBOLA_VIRUS_DISEASE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_INFLUENZA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_LEPTOSPIROSIS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_MARBURG_VIRUS_DISEASE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_MEASLES` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_MIDDLE_EASI_RESPIRATORY_SYNDROME_CORONAVIRUS_MERS_CO_V` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_MPOX` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_PLAGUE_PNEUMONIC` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_DISEASE_YELLOW_FEVER` | SI | #e8e323 |

### 5.20 Tipo de Exposicion

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_FAMILIAR` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_SLEPT_ATE_OR_SPEND_TIME_IN_SAME_HOUSEHOLD` | NO | #9370db |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_COMUNITARIO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_DIRECT_PHYSICAL_CONTACT` | NO | #ffa500 |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_TOUCHED_BODY_FLUIDS` | NO | #f2c87c |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_VUELO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_ATE_DRANK_CONTAMINATED_MATERIAL` | NO | #dcb6f4 |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_PERSONAL_DE_SALUD` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_MIGRANTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_EXPOSURE_TYPE_OTHER_PLEASE_SPECIFY_IN_COMMENT_FIELD` | SI | #966161 |

### 5.21 Contexto de Transmision

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_FAMILY` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_MEASLES` | SI | #1dbecb |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_SARAMPION_2` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_NOSOCOMIAL_TRANSMISSION` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_CO_WORKERS` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_FRIENDS` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_TRAVEL_TO_OUTBREAK_AREA` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_CONTEXT_OF_TRANSMISSION_UNKNOWN` | NO |  |

### 5.22 Tipo de Fecha (DateRanges)

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_ISOLATION` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_CUARENTENA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_HOSPITALIZATION` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_ICU_ADMISSION` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_HOSPITALIZATION_FOR_OTHER_MEDICAL_CONDITIONS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_OTHER` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_A_E_VISIT` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_PRIMARY_HEALTH_CARE_PHC_GP_ETC_VISIT` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_OUTPATIENT_VISIT` | SI |  |

### 5.23 Estado Diario de Seguimiento

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_SEEN_OK` | SI | #46c59c |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_SEEN_NOT_OK` | SI | #d64545 |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_MISSED` | SI | #bda825 |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_NOT_ATTEMPTED` | SI | #bb359e |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_NOT_PERFORMED` | SI | #928585 |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_INFO_RASTREO_INCOMPLETA` | SI | #9eb2b7 |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_HOY_NO_TOCA` | NO | #3928f0 |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_NO_RESPONDIO` | SI | #db6588 |
| `LNG_REFERENCE_DATA_CONTACT_DAILY_FOLLOW_UP_STATUS_TYPE_RECHAZO_SEGUIMIENTO` | SI | #8865db |

### 5.24 Estado Final de Seguimiento

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CONTACT_FINAL_FOLLOW_UP_STATUS_TYPE_UNDER_FOLLOW_UP` | SI |  |
| `LNG_REFERENCE_DATA_CONTACT_FINAL_FOLLOW_UP_STATUS_TYPE_FOLLOW_UP_COMPLETED` | SI |  |
| `LNG_REFERENCE_DATA_CONTACT_FINAL_FOLLOW_UP_STATUS_TYPE_LOST_TO_FOLLOW_UP` | SI |  |
| `LNG_REFERENCE_DATA_CONTACT_FINAL_FOLLOW_UP_STATUS_TYPE_DIED` | NO |  |
| `LNG_REFERENCE_DATA_CONTACT_FINAL_FOLLOW_UP_STATUS_TYPE_SE_CONVIERTO_EN_UN_CASO` | SI |  |
| `LNG_REFERENCE_DATA_CONTACT_FINAL_FOLLOW_UP_STATUS_TYPE_SEGUIMIENTO_IMPOSIBLE` | SI | #ffffff |

### 5.25 Categorias de Preguntas

| Valor (API) | Activo | Color |
|-------------|--------|-------|
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_CLINICAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_A_0_DATA_COLLECTOR_INFORMATION` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_INITIAL_RESPIRATORY_SAMPLE_COLLECTION` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_FORM_COMPLETION` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_HEALTH_CARE_INTERACTIONS` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_OUTCOME_STATUS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_CONTACT_DETAILS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_ACCIONES_DE_RESPUESTA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_ANTECEDENTES_MEDICOS_Y_DE_VACUNACION` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_CASE_IDENTIFICATION` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_CONTACT_WITH_CONFIRMED_PATIENT` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_DATOS_CLINICOS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_DATOS_DE_LA_UNIDAD_NOTIFICADORA` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_DROMEDARY_CAMEL_CONTACT` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_EPIDEMIOLOGY_AND_EXPOSURE` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_EXPOSURE_RISK` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_FICHA_EPIDEMIOLOGICA_DE_VIGILANCIA_DE_SARAMPION_RUBEOLA_DIRECCION_DE_EPIDEMIOLOGIA_Y_GESTION_DE_RIESGO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_HEALTH_CARE_VISITS` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_HISTORY_OF_PRESENT_ILNESS` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_INFORMACION_DEL_PACIENTE` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_LABORATORIO` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_MINISTERIO_DE_SALUD_PUBLICA_Y_ASISTENCIA_SOCIAL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_OTHER_ANIMAL_CONTACT` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_PATIENTS_CONDITION` | NO |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_RECENT_TRAVEL` | SI |  |
| `LNG_REFERENCE_DATA_CATEGORY_QUESTION_CATEGORY_UNDERLYING_MEDICAL_CONDITIONS` | SI |  |

## 6. Jerarquia de Ubicaciones (Location Hierarchy)

Total ubicaciones: 782

Niveles: ADMIN_LEVEL_0 (Pais) > ADMIN_LEVEL_1 (Departamento) > ADMIN_LEVEL_2 (DAS/Hospital) > ADMIN_LEVEL_3 (Municipio)

### Pais: Guatemala (`65c6cd0f-0be1-4848-9c0e-d4f422fc61ea`)

### Departamentos (ADMIN_LEVEL_1)

| Departamento | ID | Hijos |
|--------------|-----|-------|
| Alta Verapaz | `16` | 4 |
| Baja Verapaz | `15` | 2 |
| Chimaltenango | `4` | 2 |
| Chiquimula | `20` | 2 |
| El Progreso | `2` | 2 |
| Escuintla | `5` | 3 |
| Guatemala | `1` | 21 |
| Huehuetenango | `13` | 4 |
| Izabal | `18` | 3 |
| Jalapa | `21` | 2 |
| Jutiapa | `22` | 2 |
| Petén | `17` | 7 |
| Quetzaltenango | `9` | 5 |
| Quiché | `14` | 7 |
| Retalhuleu | `11` | 2 |
| Sacatepéquez | `3` | 2 |
| San Marcos | `12` | 3 |
| Santa Rosa | `6` | 2 |
| Sololá | `7` | 2 |
| Suchitepéquez | `10` | 2 |
| Totonicapán | `8` | 2 |
| Zacapa | `19` | 2 |

### DAS, Hospitales y Municipios (ADMIN_LEVEL_2 y ADMIN_LEVEL_3)

#### Alta Verapaz

- **DAS Alta Verapáz** (`220`) - 23 municipios
  - Cahabon (`7b49cb07-b564-4bcc-a46a-171d361c827b`)
  - Campur (`4314fcf2-5064-44fd-a7f4-816df8a7c8a9`)
  - Carcha (`007a3e27-c42f-453e-b029-515e99395494`)
  - Chahal (`1614`)
  - Chamelco (`0f3dae7c-2c67-4b6e-8e2a-d3012436f11b`)
  - Chisec (`1613`)
  - Cobán (`1601`)
  - Fray Bartolomé de Las Casas (`1615`)
  - Panzós (`1607`)
  - Raxruhá (`1617`)
  - San Agustín Lanquín (`1611`)
  - San Cristóbal Verapaz (`1603`)
  - San Juan Chamelco (`1610`)
  - San Miguel Tucurú (`1606`)
  - San Pedro Carchá (`1609`)
  - Santa Catalina La Tinta (`1616`)
  - Santa Cruz Verapaz (`1602`)
  - Santa María Cahabón (`1612`)
  - Senahú (`1608`)
  - Tactic (`1604`)
  - Tamahú (`1605`)
  - Teleman (`9d40e626-e842-4586-9604-9fd47d452ac6`)
  - Tucuru (`8f5ed7c7-3b09-4c7b-91fb-9734f65b9ffa`)
- Hosp Coban (`254`)
- Hosp Fray Bartolome (`270`)
- Hosp La Tinta (`271`)

#### Baja Verapaz

- **DAS Baja Verapaz** (`219`) - 8 municipios
  - Cubulco (`1504`)
  - Granados (`1505`)
  - Purulhá (`1508`)
  - Rabinal (`1503`)
  - Salamá (`1501`)
  - San Jerónimo (`1507`)
  - San Miguel Chicaj (`1502`)
  - Santa Cruz El Chol (`1506`)
- Hosp Salama (`253`)

#### Chimaltenango

- **DAS Chimaltenango** (`207`) - 17 municipios
  - Acatenango (`411`)
  - Chimaltenango (`401`)
  - DMS Vii Sanarate (`20520768`)
  - El Tejar (`416`)
  - Parramos (`414`)
  - Patzicía (`409`)
  - Patzún (`407`)
  - San Andrés Itzapa (`413`)
  - San José Poaquil (`402`)
  - San Juan Comalapa (`404`)
  - San Martín Jilotepeque (`403`)
  - San Miguel Pochuta (`408`)
  - San Pedro Yepocapa (`412`)
  - Santa Apolonia (`405`)
  - Santa Cruz Balanyá (`410`)
  - Tecpán Guatemala (`406`)
  - Zaragoza (`415`)
- Hosp Chimaltenango (`237`)

#### Chiquimula

- **DAS Chiquimula** (`224`) - 11 municipios
  - Camotán (`2005`)
  - Chiquimula (`2001`)
  - Concepción Las Minas (`2008`)
  - Esquipulas (`2007`)
  - Ipala (`2011`)
  - Jocotán (`2004`)
  - Olopa (`2006`)
  - Quezaltepeque (`2009`)
  - San Jacinto (`2010`)
  - San José La Arada (`2002`)
  - San Juan Ermita (`2003`)
- Hosp Chiquimula (`262`)

#### El Progreso

- **DAS El Progreso** (`205`) - 10 municipios
  - DMS S (`20520566`)
  - DMS V El Jicaro (`20520565`)
  - El Jícaro (`d61f7eaf-9e8b-4c5e-b3aa-b130b1ea373d`)
  - Guastatoya (`201`)
  - Morazán (`86872de9-5c80-4d0e-9fbd-0a4d1695ae72`)
  - San Agustín Acasaguastlán (`dda9f1f8-5ac0-4d11-be64-5f51510ff26f`)
  - San Antonio La Paz (`887f1cd0-456f-4b03-a81d-41a34bb2cd58`)
  - San Cristóbal Acasaguastlán (`e81a24f2-e8a8-4121-8404-fe4adc2ee0d4`)
  - Sanarate (`86a1cf65-765b-4072-893d-6878521ed73b`)
  - Sansare (`c024aab6-450e-49df-a6b7-f82b1a84b0b1`)
- Hosp El Progreso (`234`)

#### Escuintla

- **DAS Escuintla** (`208`) - 15 municipios
  - DMS Viii San Antonio La Paz (`20520869`)
  - Escuintla (`501`)
  - Guanagazapa (`508`)
  - Iztapa (`510`)
  - La Democracia (`503`)
  - La Gomera (`507`)
  - Masagua (`505`)
  - Nueva Concepción (`513`)
  - Palín (`511`)
  - San José (`509`)
  - San Vicente Pacaya (`512`)
  - Santa Lucía Cotzumalguapa (`502`)
  - Sipacate (`514`)
  - Siquinalá (`504`)
  - Tiquisate (`506`)
- Hosp Escuintla (`238`)
- Hosp Tiquisate (`239`)

#### Guatemala

- **DAS Guatemala Central** (`278`) - 1 municipios
  - Ciudad de Guatemala (`101`)
- **DAS Guatemala Nor-Occidente** (`203`) - 11 municipios
  - Chuarrancho (`112`)
  - Ciudad Quetzal (`aaba647f-ad07-4ae6-b60d-358cbc5ae7bc`)
  - Comunidad (`6353ab10-1427-47a3-81c0-25653567b258`)
  - DMS III San Agustin Acasaguastlan (`20520363`)
  - El Milagro (`e2f7551e-29e3-4e1b-b2c5-c2376e611ec3`)
  - Mixco (`108`)
  - Primero de Julio (`7618b0b2-f84b-48d1-89c2-bb7a2fb45a9f`)
  - San Juan Sacatepéquez (`110`)
  - San Pedro Sacatepéquez (`109`)
  - San Raymundo (`111`)
  - Satelite (`93eb556f-2a26-48b1-8236-5a79a127ee88`)
- **DAS Guatemala Nor-Oriente** (`202`) - 8 municipios
  - Chinautla (`106`)
  - DMS Morazan  (`20520262`)
  - Fraijanes (`113`)
  - Palencia (`105`)
  - San José Pinula (`103`)
  - San José del Golfo (`104`)
  - San Pedro Ayampuc (`107`)
  - Santa Catarina Pinula (`102`)
- **DAS Guatemala Sur** (`204`) - 5 municipios
  - Amatitlán (`114`)
  - DMS Iv San Cristobal Acasaguastlan (`20520464`)
  - San Miguel Petapa (`117`)
  - Villa Canales (`116`)
  - Villa Nueva (`115`)
- Hosp Amatitlan (`233`)
- Hosp Centro Médico (`3c69ed77-b413-4ed5-ad0d-6519eff3006d`)
- Hosp Centro Médico Militar (`282f02ae-345f-488f-957a-3f221042e5a1`)
- Hosp El Pilar (`752f3dc9-9988-4fde-8864-00e7fe1ae7b8`)
- Hosp Herrera Llerandi (`81944163-5bf5-4d62-befb-457a474e70ba`)
- Hosp Infectologia (`231`)
- Hosp La Esperanza (`06a39388-8a92-45b5-a2d8-0694273a00b4`)
- Hosp Ortopedia (`229`)
- Hosp Parque de la Industria (`e3cc8bbc-4d7d-4535-9d65-693f19d811c4`)
- Hosp Roosevelt (`230`)
- Hosp Salud Mental (`228`)
- Hosp San Juan de Dios (`227`)
- Hosp San Vicente (`232`)
- Hosp Sanatorio La Paz (`6dd39616-8a75-4127-8125-0643097f727f`)
- Hosp Villa Nueva  (`285`)
- Hosp Yardem (`f0c35679-bdcf-4d70-b566-e06188c78c49`)
- IGSS (`78b5c166-c284-4e4f-a84e-854cb276dce1`)

#### Huehuetenango

- **DAS Huehuetenango** (`216`) - 33 municipios
  - Aguacatán (`1327`)
  - Chiantla (`1302`)
  - Colotenango (`1319`)
  - Concepción Huista (`1322`)
  - Cuilco (`1304`)
  - Huehuetenango (`1301`)
  - Jacaltenango (`1307`)
  - La Democracia (`1312`)
  - La Libertad (`1311`)
  - Malacatancito (`1303`)
  - Nentón (`1305`)
  - Petatán (`1333`)
  - San Antonio Huista (`1324`)
  - San Gaspar Ixchil (`1329`)
  - San Ildefonso Ixtahuacán (`1309`)
  - San Juan Atitán (`1316`)
  - San Juan Ixcoy (`1323`)
  - San Mateo Ixtatán (`1318`)
  - San Miguel Acatán (`1313`)
  - San Pedro Necta (`1306`)
  - San Pedro Soloma (`1308`)
  - San Rafael La Independencia (`1314`)
  - San Rafael Petzal (`1328`)
  - San Sebastián Coatán (`1325`)
  - San Sebastián Huehuetenango (`1320`)
  - Santa Ana Huista (`1331`)
  - Santa Bárbara (`1310`)
  - Santa Cruz Barillas (`1326`)
  - Santa Eulalia (`1317`)
  - Santiago Chimaltenango (`1330`)
  - Tectitán (`1321`)
  - Todos Santos Cuchumatán (`1315`)
  - Unión Cantinil (`1332`)
- Hosp Barillas (`284`)
- Hosp Huehuetenengo (`250`)
- Hosp San Pedro Necta (`251`)

#### Izabal

- **DAS Izabal** (`222`) - 5 municipios
  - El Estor (`1803`)
  - Livingston (`1802`)
  - Los Amates (`1805`)
  - Morales (`1804`)
  - Puerto Barrios (`1801`)
- Hosp Infantil de Puerto Barrios (`260`)
- Hosp Puerto Barrios (`259`)

#### Jalapa

- **DAS Jalapa** (`225`) - 7 municipios
  - Jalapa (`2101`)
  - Mataquescuintla (`2107`)
  - Monjas (`2106`)
  - San Carlos Alzatate (`2105`)
  - San Luis Jilotepeque (`2103`)
  - San Manuel Chaparrón (`2104`)
  - San Pedro Pinula (`2102`)
- Hosp Jalapa (`263`)

#### Jutiapa

- **DAS Jutiapa** (`226`) - 19 municipios
  - Agua Blanca (`2204`)
  - Asunción Mita (`2205`)
  - Atescatempa (`2207`)
  - Ciudad Pedro De Alvarado (`160e4421-950f-4b10-8858-e6995a80e3d7`)
  - Comapa (`2211`)
  - Conguaco (`2213`)
  - El Adelanto (`2209`)
  - El Progreso (`2202`)
  - Jalpatagua (`2212`)
  - Jerez (`2208`)
  - Jutiapa (`2201`)
  - Los Anonos (`23cf9782-f3a1-4efd-8d48-4910d5e64dd7`)
  - Moyuta (`2214`)
  - Pasaco (`2215`)
  - Quesada (`2217`)
  - San José Acatempa (`2216`)
  - Santa Catarina Mita (`2203`)
  - Yupiltepeque (`2206`)
  - Zapotitlán (`2210`)
- Hosp Jutiapa (`264`)

#### Petén

- **DAS Petén Norte** (`221`) - 6 municipios
  - Flores (`1701`)
  - Melchor de Mencos (`1711`)
  - San Andrés (`1704`)
  - San Benito (`1703`)
  - San Francisco (`1706`)
  - San José (`1702`)
- **DAS Petén Sur Occidente** (`265`) - 3 municipios
  - La Libertad (`1705`)
  - Las Cruces (`1713`)
  - Sayaxché (`1710`)
- **DAS Petén Sur Oriente** (`266`) - 5 municipios
  - Dolores (`1708`)
  - El Chal (`1714`)
  - Poptún (`1712`)
  - San Luis (`1709`)
  - Santa Ana (`1707`)
- Hosp Melchor de Mencos (`256`)
- Hosp Poptun (`258`)
- Hosp San Benito (`255`)
- Hosp Sayaxche (`257`)

#### Quetzaltenango

- **DAS Quetzaltenango** (`212`) - 24 municipios
  - Almolonga (`913`)
  - Cabricán (`906`)
  - Cajolá (`907`)
  - Cantel (`914`)
  - Coatepeque (`920`)
  - Colomba Costa Cuca (`917`)
  - Concepción Chiquirichapa (`911`)
  - El Palmar (`919`)
  - Flores Costa Cuca (`922`)
  - Génova (`921`)
  - Huitán (`915`)
  - La Esperanza (`923`)
  - Palestina de Los Altos (`924`)
  - Quetzaltenango (`901`)
  - Salcajá (`902`)
  - San Carlos Sija (`904`)
  - San Francisco La Unión (`918`)
  - San Juan Olintepeque (`903`)
  - San Juan Ostuncalco (`909`)
  - San Martín Sacatepéquez (`912`)
  - San Mateo (`910`)
  - San Miguel Siguilá (`908`)
  - Sibilia (`905`)
  - Zunil (`916`)
- Hosp Cefemerq (`7240c1d5-ea18-48bb-8b98-4c1887f3f13d`)
- Hosp Coatepeque (`245`)
- Hosp Regional de Occidente (`243`)
- Hosp Rodolfo Robles (`244`)

#### Quiché

- **DAS Ixcán** (`218`) - 1 municipios
  - Playa Grande Ixcán (`1420`)
- **DAS Ixil** (`283`) - 3 municipios
  - Chajul (`1405`)
  - San Juan Cotzal (`1411`)
  - Santa María Nebaj (`1413`)
- **DAS Quiché** (`217`) - 17 municipios
  - Canillá (`1418`)
  - Chicamán (`1419`)
  - Chiché (`1402`)
  - Chinique (`1403`)
  - Cunén (`1410`)
  - Joyabaj (`1412`)
  - Pachalum (`1421`)
  - Patzité (`1407`)
  - Sacapulas (`1416`)
  - San Andrés Sajcabajá (`1414`)
  - San Antonio Ilotenango (`1408`)
  - San Bartolomé Jocotenango (`1417`)
  - San Miguel Uspantán (`1415`)
  - San Pedro Jocopilas (`1409`)
  - Santa Cruz del Quiché (`1401`)
  - Santo Tomás Chichicastenango (`1406`)
  - Zacualpa (`1404`)
- Hosp Joyabaj (`267`)
- Hosp Nebaj (`268`)
- Hosp Quiche (`252`)
- Hosp Uspantan (`269`)

#### Retalhuleu

- **DAS Retalhuleu** (`214`) - 9 municipios
  - Champerico (`1107`)
  - El Asintal (`1109`)
  - Nuevo San Carlos (`1108`)
  - Retalhuleu (`1101`)
  - San Andrés Villa Seca (`1106`)
  - San Felipe (`1105`)
  - San Martín Zapotitlán (`1104`)
  - San Sebastián (`1102`)
  - Santa Cruz Muluá (`1103`)
- Hosp Retalhuleu (`247`)

#### Sacatepéquez

- **DAS Sacatepéquez** (`206`) - 17 municipios
  - Antigua Guatemala (`301`)
  - Ciudad Vieja (`312`)
  - DMS Vi Sansare (`20520667`)
  - Jocotenango (`302`)
  - Magdalena Milpas Altas (`310`)
  - Pastores (`303`)
  - San Antonio Aguas Calientes (`315`)
  - San Bartolomé Milpas Altas (`307`)
  - San Juan Alotenango (`314`)
  - San Lucas Sacatepéquez (`308`)
  - San Miguel Dueñas (`313`)
  - Santa Catarina Barahona (`316`)
  - Santa Lucía Milpas Altas (`309`)
  - Santa María de Jesús (`311`)
  - Santiago Sacatepéquez (`306`)
  - Santo Domingo Xenacoj (`305`)
  - Sumpango (`304`)
- Hosp Antigua Guatemala (`235`)

#### San Marcos

- **DAS San Marcos** (`215`) - 30 municipios
  - Ayutla (`1217`)
  - Catarina (`1216`)
  - Comitancillo (`1204`)
  - Concepción Tutuapa (`1206`)
  - El Quetzal (`1220`)
  - El Tumbador (`1213`)
  - Esquipulas Palo Gordo (`1227`)
  - Ixchiguán (`1223`)
  - La Blanca (`1230`)
  - La Reforma (`1221`)
  - Malacatán (`1215`)
  - Nuevo Progreso (`1212`)
  - Ocós (`1218`)
  - Pajapita (`1222`)
  - Río Blanco (`1228`)
  - San Antonio Sacatepéquez (`1203`)
  - San Cristóbal Cucho (`1225`)
  - San José Ojetenam (`1224`)
  - San José el Rodeo (`1214`)
  - San Lorenzo (`1229`)
  - San Marcos (`1201`)
  - San Miguel Ixtahuacán (`1205`)
  - San Pablo (`1219`)
  - San Pedro Sacatepéquez (`1202`)
  - San Rafael Pie de la Cuesta (`1211`)
  - Sibinal (`1208`)
  - Sipacapa (`1226`)
  - Tacaná (`1207`)
  - Tajumulco (`1209`)
  - Tejutla (`1210`)
- Hosp Malacatan (`249`)
- Hosp San Marcos (`248`)

#### Santa Rosa

- **DAS Santa Rosa** (`209`) - 14 municipios
  - Barberena (`602`)
  - Casillas (`604`)
  - Chiquimulilla (`608`)
  - Cuilapa (`601`)
  - Guazacapán (`611`)
  - Nueva Santa Rosa (`614`)
  - Oratorio (`606`)
  - Pueblo Nuevo Viñas (`613`)
  - San Juan Tecuaco (`607`)
  - San Rafael Las Flores (`605`)
  - Santa Cruz Naranjo (`612`)
  - Santa María Ixhuatán (`610`)
  - Santa Rosa de Lima (`603`)
  - Taxisco (`609`)
- Hosp Cuilapa (`240`)

#### Sololá

- **DAS Sololá** (`210`) - 19 municipios
  - Concepción (`708`)
  - Nahualá (`705`)
  - Panajachel (`710`)
  - San Andrés Semetabaj (`709`)
  - San Antonio Palopó (`712`)
  - San José Chacayá (`702`)
  - San Juan La Laguna (`717`)
  - San Lucas Tolimán (`713`)
  - San Marcos La Laguna (`716`)
  - San Pablo La Laguna (`715`)
  - San Pedro La Laguna (`718`)
  - Santa Catarina Ixtahuacán (`706`)
  - Santa Catarina Palopó (`711`)
  - Santa Clara La Laguna (`707`)
  - Santa Cruz La Laguna (`714`)
  - Santa Lucía Utatlán (`704`)
  - Santa María Visitación (`703`)
  - Santiago Atitlán (`719`)
  - Sololá (`701`)
- Hosp Solola  (`241`)

#### Suchitepéquez

- **DAS Suchitepéquez** (`213`) - 21 municipios
  - Chicacao (`1013`)
  - Cuyotenango (`1002`)
  - Mazatenango (`1001`)
  - Patulul (`1014`)
  - Pueblo Nuevo (`1019`)
  - Río Bravo (`1020`)
  - Samayac (`1008`)
  - San Antonio Suchitepéquez (`1010`)
  - San Bernardino (`1004`)
  - San Francisco Zapotitlán (`1003`)
  - San Gabriel (`1012`)
  - San José La Máquina (`1021`)
  - San José el Ídolo (`1005`)
  - San Juan Bautista (`1016`)
  - San Lorenzo (`1007`)
  - San Miguel Panán (`1011`)
  - San Pablo Jocopilas (`1009`)
  - Santa Bárbara (`1015`)
  - Santo Domingo Suchitepéquez (`1006`)
  - Santo Tomas La Unión (`1017`)
  - Zunilito (`1018`)
- Hosp Mazatenango (`246`)

#### Totonicapán

- **DAS Totonicapán** (`211`) - 9 municipios
  - Momostenango (`805`)
  - San Andrés Xecul (`804`)
  - San Bartolo Aguas Calientes (`808`)
  - San Cristóbal Totonicapán (`802`)
  - San Francisco El Alto (`803`)
  - San Vicente Buenabaj (`89b2453d-6d3a-4104-afc7-2f9274014ce1`)
  - Santa Lucía la Reforma (`807`)
  - Santa María Chiquimula (`806`)
  - Totonicapán (`801`)
- Hosp Totonicapan (`242`)

#### Zacapa

- **DAS Zacapa** (`223`) - 11 municipios
  - Cabañas (`1907`)
  - Estanzuela (`1902`)
  - Gualán (`1904`)
  - Huité (`1910`)
  - La Unión (`1909`)
  - Río Hondo (`1903`)
  - San Diego (`1908`)
  - San Jorge (`1911`)
  - Teculután (`1905`)
  - Usumatlán (`1906`)
  - Zacapa (`1901`)
- Hosp Zacapa (`261`)

## 7. Restricciones de Datos de Referencia del Brote

El brote tiene filtros especificos para ciertos tipos de datos de referencia:

### LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST

- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PCR`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_IG_C_OR_IG_M`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PARTIAL_GENOME_SEQUENCING`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_WHOLE_GENOME_SEQUENCING`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_OTHER_SPECIFY_IN_NOTES_FIELD`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_AVIDEZ`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_IG_G`: Permitido

### LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE

- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_URINE`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_NASOFARINGEO`: Permitido
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SERUM`: Permitido

## 8. Campos Visibles y Obligatorios

### cases

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `ageDob` | SI | NO |
| `dateOfOnset` | SI | SI |
| `dateOfReporting` | SI | SI |
| `firstName` | SI | SI |
| `followUp[status]` | SI | NO |
| `gender` | SI | SI |
| `lastName` | SI | SI |
| `middleName` | SI | NO |
| `pregnancyStatus` | SI | NO |
| `visualId` | SI | SI |

### events

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `address____addressLine1` | SI | NO |
| `address____city` | SI | NO |
| `address____geoLocation` | SI | NO |
| `address____geoLocationAccurate` | SI | NO |
| `address____locationId` | SI | NO |
| `address____phoneNumber` | SI | NO |
| `address____typeId` | SI | SI |
| `date` | SI | SI |
| `dateOfReporting` | SI | SI |
| `description` | SI | NO |
| `endDate` | SI | NO |
| `eventCategory` | SI | NO |
| `name` | SI | SI |
| `responsibleUserId` | SI | NO |
| `visualId` | SI | NO |

### contacts

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `addresses____addressLine1` | SI | NO |
| `addresses____city` | SI | NO |
| `addresses____date` | SI | NO |
| `addresses____geoLocation` | SI | NO |
| `addresses____geoLocationAccurate` | SI | NO |
| `addresses____locationId` | SI | SI |
| `addresses____postalCode` | SI | NO |
| `addresses____typeId` | SI | SI |
| `ageDob` | SI | NO |
| `dateOfReporting` | SI | SI |
| `documents____number` | SI | NO |
| `documents____type` | SI | NO |
| `firstName` | SI | SI |
| `followUpTeamId` | SI | NO |
| `followUp[status]` | SI | NO |
| `gender` | SI | NO |
| `isDateOfReportingApproximate` | SI | NO |
| `lastName` | SI | NO |
| `middleName` | SI | NO |
| `pregnancyStatus` | SI | NO |
| `visualId` | SI | NO |

### contacts-of-contacts

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `addresses____addressLine1` | SI | NO |
| `addresses____city` | SI | NO |
| `addresses____date` | SI | NO |
| `addresses____geoLocation` | SI | NO |
| `addresses____geoLocationAccurate` | SI | NO |
| `addresses____locationId` | SI | SI |
| `addresses____phoneNumber` | SI | NO |
| `addresses____postalCode` | SI | NO |
| `addresses____typeId` | SI | SI |
| `ageDob` | SI | NO |
| `dateOfReporting` | SI | SI |
| `documents____number` | SI | SI |
| `documents____type` | SI | SI |
| `firstName` | SI | SI |
| `gender` | SI | NO |
| `lastName` | SI | NO |
| `middleName` | SI | NO |
| `pregnancyStatus` | SI | NO |
| `responsibleUserId` | SI | NO |
| `visualId` | SI | NO |

### follow-ups

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `address____addressLine1` | SI | NO |
| `address____city` | SI | NO |
| `address____date` | SI | NO |
| `address____geoLocation` | SI | NO |
| `address____geoLocationAccurate` | SI | NO |
| `address____locationId` | SI | NO |
| `address____phoneNumber` | SI | NO |
| `address____postalCode` | SI | NO |
| `address____typeId` | SI | SI |
| `date` | SI | SI |
| `responsibleUserId` | SI | NO |
| `statusId` | SI | SI |
| `targeted` | SI | NO |
| `teamId` | SI | NO |

### lab-results

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `dateOfResult` | SI | NO |
| `dateSampleDelivered` | SI | NO |
| `dateSampleTaken` | SI | SI |
| `dateTesting` | SI | NO |
| `labName` | SI | NO |
| `notes` | SI | NO |
| `quantitativeResult` | SI | NO |
| `result` | SI | SI |
| `sampleIdentifier` | SI | NO |
| `sampleType` | SI | NO |
| `sequence[dateResult]` | SI | NO |
| `sequence[dateSampleSent]` | SI | NO |
| `sequence[hasSequence]` | SI | NO |
| `sequence[labId]` | SI | NO |
| `sequence[noSequenceReason]` | SI | NO |
| `sequence[resultId]` | SI | NO |
| `status` | SI | NO |
| `testType` | SI | NO |
| `testedFor` | SI | NO |

### relationships

| Campo | Visible | Obligatorio |
|-------|---------|-------------|
| `certaintyLevelId` | SI | NO |
| `clusterId` | SI | NO |
| `comment` | SI | NO |
| `contactDate` | SI | SI |
| `contactDateEstimated` | SI | NO |
| `dateOfFirstContact` | SI | NO |
| `socialRelationshipTypeId` | SI | NO |

## 9. Ejemplo de Caso Completo (POST Payload)

Basado en SR-0004 (el caso mas completo de los 5 existentes):

```json
{
  "firstName": "NOMBRE",
  "middleName": "SEGUNDO_NOMBRE",
  "lastName": "APELLIDOS",
  "gender": "LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE",
  "dob": "1990-01-15T00:00:00.000Z",
  "age": {
    "years": 36,
    "months": 0
  },
  "dateOfOnset": "2026-03-24T00:00:00.000Z",
  "dateOfReporting": "2026-03-26T00:00:00.000Z",
  "isDateOfReportingApproximate": false,
  "pregnancyStatus": "LNG_REFERENCE_DATA_CATEGORY_PREGNANCY_STATUS_NO_APLICA",
  "classification": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
  "outcomeId": "LNG_REFERENCE_DATA_CATEGORY_OUTCOME_ALIVE",
  "riskLevel": "LNG_REFERENCE_DATA_CATEGORY_RISK_LEVEL_DOMICILIAR",
  "addresses": [
    {
      "typeId": "LNG_REFERENCE_DATA_CATEGORY_ADDRESS_TYPE_USUAL_PLACE_OF_RESIDENCE",
      "locationId": "LOCATION_UUID_HERE",
      "city": "ZONA 1",
      "addressLine1": "6 AV 18-20 zona 4",
      "phoneNumber": "54390350"
    }
  ],
  "documents": [
    {
      "type": "LNG_REFERENCE_DATA_CATEGORY_DOCUMENT_TYPE_NATIONAL_ID_CARD",
      "number": "1686819271401"
    }
  ],
  "vaccinesReceived": [
    {
      "vaccine": "LNG_REFERENCE_DATA_CATEGORY_VACCINE_SR",
      "status": "LNG_REFERENCE_DATA_CATEGORY_VACCINE_STATUS_VACCINATED",
      "date": "2026-02-15T00:00:00.000Z"
    }
  ],
  "dateRanges": [
    {
      "typeId": "LNG_REFERENCE_DATA_CATEGORY_PERSON_DATE_TYPE_ISOLATION",
      "startDate": "2026-03-26T00:00:00.000Z",
      "endDate": "2026-04-05T00:00:00.000Z"
    }
  ],
  "questionnaireAnswers": {
    "diagnostico_de_sospecha_": [
      {
        "value": "SARAMPION"
      }
    ],
    "caso_altamente_sospechoso_de_sarampion": [
      {
        "value": "SI"
      }
    ],
    "fecha_de_notificacion": [
      {
        "value": "Fecha de Notificacion"
      }
    ],
    "informacion_del_paciente": [
      {
        "value": "DATOS GENERALES"
      }
    ],
    "antecedentes_medicos_y_de_vacunacion": [
      {
        "value": "ANTECEDENTES MEDICOS Y DE VACUNACION"
      }
    ],
    "datos_clinicos": [
      {
        "value": "DATOS CLINICOS"
      }
    ],
    "direccion_de_area_de_salud": [
      {
        "value": "QUICHE"
      }
    ],
    "fecha_de_consulta": [
      {
        "value": "2026-03-25T00:00:00.000Z"
      }
    ],
    "fecha_de_investigacion_domiciliaria": [
      {
        "value": "2026-03-26T00:00:00.000Z"
      }
    ],
    "nombre_de_quien_investiga": [
      {
        "value": "David Rivera"
      }
    ],
    "cargo_de_quien_investiga": [
      {
        "value": "Estadigrafo"
      }
    ],
    "telefono": [
      {
        "value": "58560121"
      }
    ],
    "correo_electronico": [
      {
        "value": "correo@ejemplo.com"
      }
    ],
    "fuente_de_notificacion_": [
      {
        "value": "SERVICIO DE SALUD"
      }
    ],
    "distrito_municipal_de_salud_dms18": [
      {
        "value": "SANTA CRUZ DEL QUICHE"
      }
    ],
    "servicio_de_salud_22": [
      {
        "value": "consulta externa"
      }
    ],
    "codigo_unico_de_identificacion_dpi_pasaporte_otro": [
      {
        "value": "DPI"
      }
    ],
    "pueblo": [
      {
        "value": "MAYA"
      }
    ],
    "comunidad_linguistica": [
      {
        "value": "K'iche'"
      }
    ],
    "extranjero_": [
      {
        "value": "NO"
      }
    ],
    "migrante": [
      {
        "value": "NO"
      }
    ],
    "ocupacion_": [
      {
        "value": "medico"
      }
    ],
    "escolaridad_": [
      {
        "value": "UNIVERSIDAD"
      }
    ],
    "telefono_": [
      {
        "value": "54390350"
      }
    ],
    "pais_de_residencia_": [
      {
        "value": "GUATEMALA"
      }
    ],
    "direccion_de_residencia_": [
      {
        "value": "6 AV 18-20 zona 4"
      }
    ],
    "lugar_poblado_": [
      {
        "value": "Urbano"
      }
    ],
    "no_de_dpi": [
      {
        "value": "1686819271401"
      }
    ],
    "departamento_de_residencia_": [
      {
        "value": "QUICHE"
      }
    ],
    "municipio_de_residencia13": [
      {
        "value": "SANTA CRUZ DEL QUICHE"
      }
    ],
    "paciente_vacunado_": [
      {
        "value": "SI"
      }
    ],
    "tipo_de_vacuna_recibida_": [
      {
        "value": [
          "SR - Sarampion Rubeola"
        ]
      }
    ],
    "fuente_de_la_informacion_sobre_la_vacunacion_": [
      {
        "value": "REGISTRO UNICO DE VACUNACION"
      }
    ],
    "vacunacion_en_el_sector_": [
      {
        "value": "MSPAS"
      }
    ],
    "numero_de_dosis_": [
      {
        "value": 2
      }
    ],
    "fecha_de_la_ultima_dosis_": [
      {
        "value": "2026-02-15T00:00:00.000Z"
      }
    ],
    "antecedentes_medicos_": [
      {
        "value": "SI"
      }
    ],
    "especifique_ant": [
      {
        "value": "ENFERMEDAD CRONICA"
      }
    ],
    "fecha_de_inicio_de_sintomas_": [
      {
        "value": "2026-03-24T00:00:00.000Z"
      }
    ],
    "fecha_de_inicio_de_fiebre_": [
      {
        "value": "2026-03-24T00:00:00.000Z"
      }
    ],
    "fecha_de_inicio_de_exantema_rash_": [
      {
        "value": "2026-03-25T00:00:00.000Z"
      }
    ],
    "sintomas_": [
      {
        "value": "SI"
      }
    ],
    "que_sintomas_": [
      {
        "value": [
          "Fiebre",
          "Coriza / Catarro",
          "Exantema/ Rash",
          "Tos"
        ]
      }
    ],
    "temp_c": [
      {
        "value": 38
      }
    ],
    "hospitalizacion_": [
      {
        "value": "NO"
      }
    ],
    "complicaciones_": [
      {
        "value": "NO"
      }
    ],
    "aislamiento_respiratorio": [
      {
        "value": "NO"
      }
    ],
    "factores_de_riesgo": [
      {
        "value": "No"
      }
    ],
    "acciones_de_respuesta": [
      {
        "value": "SI"
      }
    ],
    "se_realizo_busqueda_activa_institucional_de_casos_bai": [
      {
        "value": "1"
      }
    ],
    "se_realizo_busqueda_activa_comunitaria_de_casos_bac": [
      {
        "value": "1"
      }
    ],
    "hubo_vacunacion_de_bloqueo": [
      {
        "value": "1"
      }
    ],
    "hubo_vacunacion_con_barrido_documentado": [
      {
        "value": "2"
      }
    ],
    "se_realizo_monitoreo_rapido_de_vacunacion": [
      {
        "value": "2"
      }
    ],
    "se_le_administro_vitamina_a": [
      {
        "value": "2"
      }
    ],
    "clasificacion": [
      {
        "value": "2"
      }
    ],
    "clasificacion_final": [
      {
        "value": "1"
      }
    ],
    "contacto_de_otro_caso": [
      {
        "value": "NO"
      }
    ],
    "caso_analizado_por": [
      {
        "value": [
          "2"
        ]
      }
    ],
    "fecha_de_clasificacion": [
      {
        "value": "2026-03-26T00:00:00.000Z"
      }
    ],
    "condicion_final_del_paciente": [
      {
        "value": "1"
      }
    ],
    "lugares_visitados_y_rutas_de_desplazamiento_del_caso": [
      {
        "value": "2"
      }
    ],
    "sitio_ruta_de_desplazamiento_2": [
      {
        "value": "ciudad capital"
      }
    ],
    "direccion_del_lugar_y_rutas_de_desplazamiento_2": [
      {
        "value": "ciudad capital"
      }
    ],
    "fecha_en_que_visito_el_lugar_ruta_2": [
      {
        "value": "2026-03-12T00:00:00.000Z"
      }
    ],
    "tipo_de_abordaje_realizado_2": [
      {
        "value": [
          "1"
        ]
      }
    ],
    "fecha_de_abordaje_2": [
      {
        "value": "2026-03-26T00:00:00.000Z"
      }
    ]
  }
}
```

## 10. Resultados de Laboratorio (Lab Results)

Los resultados de laboratorio se envian como recursos separados, NO como parte del caso.

### Endpoint
```
POST /api/outbreaks/{outbreakId}/cases/{caseId}/lab-results
GET  /api/outbreaks/{outbreakId}/cases/{caseId}/lab-results
```

### Payload de ejemplo
```json
{
  "dateSampleTaken": "2026-03-26T00:00:00.000Z",
  "dateSampleDelivered": "2026-03-26T00:00:00.000Z",
  "dateTesting": "2026-03-27T00:00:00.000Z",
  "dateOfResult": "2026-03-28T00:00:00.000Z",
  "labName": "LNG_REFERENCE_DATA_CATEGORY_LAB_NAME_LABORATORIO_NACIONAL_DE_SALUD_LNS",
  "sampleType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SERUM",
  "testType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_IG_C_OR_IG_M",
  "result": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE",
  "status": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_STATUS_COMPLETED",
  "quantitativeResult": null,
  "notes": "IgM positivo para sarampion",
  "questionnaireAnswers": {}
}
```

### Tipos de prueba permitidos en este brote

- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PCR`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_IG_C_OR_IG_M`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_PARTIAL_GENOME_SEQUENCING`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_WHOLE_GENOME_SEQUENCING`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_OTHER_SPECIFY_IN_NOTES_FIELD`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_AVIDEZ`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_SEROLOGIA_IG_G`

### Tipos de muestra permitidos en este brote

- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_URINE`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_HISOPADO_NASOFARINGEO`
- `LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_SERUM`

## 11. Referencia de Endpoints API

```
BASE = https://godataguatemala.mspas.gob.gt/api
OUTBREAK_ID = ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19

# Autenticacion
POST   /oauth/token

# Casos
GET    /outbreaks/{id}/cases
GET    /outbreaks/{id}/cases/count
GET    /outbreaks/{id}/cases/{caseId}
POST   /outbreaks/{id}/cases
PUT    /outbreaks/{id}/cases/{caseId}
DELETE /outbreaks/{id}/cases/{caseId}

# Lab Results
GET    /outbreaks/{id}/cases/{caseId}/lab-results
POST   /outbreaks/{id}/cases/{caseId}/lab-results

# Contactos
GET    /outbreaks/{id}/contacts
POST   /outbreaks/{id}/contacts
GET    /outbreaks/{id}/cases/{caseId}/contacts

# Relaciones (caso-contacto)
GET    /outbreaks/{id}/relationships
POST   /outbreaks/{id}/relationships

# Seguimiento de contactos
GET    /outbreaks/{id}/contacts/{contactId}/follow-ups

# Ubicaciones
GET    /locations
GET    /locations/hierarchical

# Datos de referencia
GET    /reference-data

# Brote completo
GET    /outbreaks/{id}
```

## 12. Campos Dinamicos por DAS (Distrito Municipal de Salud)

IMPORTANTE: Los campos `distrito_municipal_de_salud_dms*` y `servicio_de_salud_*`
tienen SUFIJOS NUMERICOS que cambian segun la DAS seleccionada.
Esto se debe a que son sub-preguntas condicionales.

Mapeo observado en los datos reales:

| DAS (direccion_de_area_de_salud) | Campo DMS | Campo Servicio |
|----------------------------------|-----------|----------------|
| CHIQUIMULA | `distrito_municipal_de_salud_dms_CH` | `?` |
| GUATEMALA CENTRAL | `distrito_municipal_de_salud_dms4` | `servicio_de_salud_5` |
| IXCÁN | `distrito_municipal_de_salud_dms9` | `servicio_de_salud_10` |
| QUICHÉ | `distrito_municipal_de_salud_dms18` | `servicio_de_salud_22` |
| SAN MARCOS | `distrito_municipal_de_salud_dms21` | `servicio_de_salud_25` |

Variables DMS completas (del template):

- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_alta_verapaz_question_distrito_municipal_de_salud_dms`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_baja_verapaz_question_distrito_municipal_de_salud_dms`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_chimaltenango_question_distrito_municipal_de_salud_dms_chi`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_chiquimula_question_distrito_municipal_de_salud_dms_ch`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_el_progreso_question_distrito_municipal_de_salud_dms_1`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_escuintla_question_distrito_municipal_de_salud_dms_3`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_central_question_distrito_municipal_de_salud_dms_4`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_nor_occidente_question_distrito_municipal_de_salud_dms_5`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_nor_oriente_question_distrito_municipal_de_salud_dms_6`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_sur_question_distrito_municipal_de_salud_dms_7`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_huehuetenango_question_distrito_municipal_de_salud_dms_8`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_ixcan_question_distrito_municipal_de_salud_dms_9`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_ixil_question_distrito_municipal_de_salud_dms_10`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_izabal_question_distrito_municipal_de_salud_dms_11`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_jalapa_question_distrito_municipal_de_salud_dms_12`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_jutiapa_question_distrito_municipal_de_salud_dms_13`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_peten_norte_question_distrito_municipal_de_salud_dms_14`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_peten_sur_occidente_question_distrito_municipal_de_salud_dms_15`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_peten_sur_oriente_question_distrito_municipal_de_salud_dms_16`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_quetzaltenango_question_distrito_municipal_de_salud_dms_17`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_quiche_question_distrito_municipal_de_salud_dms_18`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_retalhuleu_question_distrito_municipal_de_salud_dms_19`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_sacatepequez_question_distrito_municipal_de_salud_dms_20`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_santa_rosa_question_distrito_municipal_de_salud_dms_22`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_san_marcos_question_distrito_municipal_de_salud_dms_21`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_solola_question_distrito_municipal_de_salud_dms_23`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_suchitepequez_question_distrito_municipal_de_salud_dms_24`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_totonicapan_question_distrito_municipal_de_salud_dms_25`: DISTRITO MUNICIPAL DE SALUD (DMS)
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_zacapa_question_distrito_municipal_de_salud_dms_26`: DISTRITO MUNICIPAL DE SALUD (DMS)

- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_alta_verapaz_question_servicio_de_salud`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_baja_verapaz_question_servicio_de_salud_1`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_chimaltenango_question_servicio_de_salud_2`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_chiquimula_question_servicio_de_salud_3`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_el_progreso_question_servicio_de_salud_4`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_escuintla_question_servicio_de_salud`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_central_question_servicio_de_salud_5`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_nor_occidente_question_servicio_de_salud_6`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_nor_oriente_question_servicio_de_salud_7`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_guatemala_sur_question_servicio_de_salud_8`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_huehuetenango_question_servicio_de_salud_9`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_ixcan_question_servicio_de_salud_10`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_ixil_question_servicio_de_salud_11`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_izabal_question_servicio_de_salud_12`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_jalapa_question_servicio_de_salud_13`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_jutiapa_question_servicio_de_salud_14`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_peten_norte_question_servicio_de_salud_15`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_peten_sur_occidente_question_servicio_de_salud_18`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_peten_sur_oriente_question_servicio_de_salud_19`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_quetzaltenango_question_servicio_de_salud_20`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_quiche_question_servicio_de_salud_22`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_retalhuleu_question_servicio_de_salud_23`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_sacatepequez_question_servicio_de_salud_24`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_santa_rosa_question_servicio_de_salud_26`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_san_marcos_question_servicio_de_salud_25`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_solola_question_servicio_de_salud_27`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_suchitepequez_question_servicio_de_salud_28`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_totonicapan_question_servicio_de_salud_30`: SERVICIO DE SALUD
- `lng_outbreak_ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19_fecha_de_notificacion_answer_fecha_de_notificacion_question_direccion_de_area_de_salud_answer_zacapa_question_servicio_de_salud_31`: SERVICIO DE SALUD

## 13. Observaciones Clave para Implementacion

1. **questionnaireAnswers formato**: Siempre es `{"variable": [{"value": X}]}` donde X puede ser string, number, date-string, o array de strings
2. **Campos markup/encabezado**: Variables como `informacion_del_paciente`, `antecedentes_medicos_y_de_vacunacion`, `datos_clinicos` son ENCABEZADOS de seccion, no datos reales. Su valor es el titulo de la seccion.
3. **Campos condicionales**: Muchos campos solo aparecen cuando una pregunta padre tiene cierta respuesta (ej: `tipo_de_vacuna_recibida_` solo aparece si `paciente_vacunado_` = 'SI')
4. **Sufijos numericos**: Los campos `distrito_municipal_de_salud_dms*` y `servicio_de_salud_*` y `municipio_de_residencia*` tienen sufijos numericos que varian segun la DAS. Esto es una particularidad del template de GoData donde sub-preguntas se generan con IDs unicos.
5. **classification vs clasificacion_final**: `classification` es un campo estandar GoData (ref_data). `clasificacion_final` es del cuestionario custom y usa valores numericos ('1', '2', etc.)
6. **Sin lab results template**: El brote no tiene `labResultsTemplate` custom, usa los campos estandar de GoData para lab results.
7. **Idioma GTRC**: La instancia usa un idioma custom 'Espanol GTRC' (ID: `d86b2070-fad9-4699-8be9-a8ae5cc0edd2`) para las traducciones de los tokens del template.
8. **Multiples DAS por departamento**: Guatemala tiene 4 DAS (Central, Nor-Occidente, Nor-Oriente, Sur). Peten tiene 3 (Norte, Sur Occidente, Sur Oriente). Quiche tiene 3 (Quiche, Ixcan, Ixil).
9. **Ubicaciones incluyen hospitales**: Las ubicaciones de nivel 2 incluyen tanto DAS como hospitales especificos (Hosp Roosevelt, Hosp San Juan de Dios, etc.)
10. **IGSS como ubicacion**: Hay una ubicacion especifica para IGSS bajo Guatemala: `78b5c166-c284-4e4f-a84e-854cb276dce1`
