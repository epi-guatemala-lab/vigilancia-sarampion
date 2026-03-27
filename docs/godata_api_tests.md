# GoData Guatemala API - Test Results

**Date**: 2026-03-27
**URL**: https://godataguatemala.mspas.gob.gt/api
**User**: practica4@gmail.com
**Outbreak**: ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19 ("Taller Sarampion")

---

## TEST 1: Authentication

**Endpoint**: `POST /api/oauth/token`
**Status**: 200 OK

```json
{
  "token_type": "bearer",
  "expires_in": 600,
  "access_token": "w5dd8BdEKZAAptTq5jmI..."
}
```

**Findings**:
- Token format: Bearer (OAuth2), NOT the standard GoData `id`-based token
- TTL: 600 seconds (10 minutes) -- relatively short, must handle re-auth
- No user ID returned in token response (unlike standard GoData)
- No rate limit headers observed

---

## TEST 2: User Info

**Endpoint**: `GET /api/users/me`
**Status**: 403 Forbidden

```json
{
  "error": {
    "statusCode": 403,
    "code": "MISSING_REQUIRED_PERMISSION",
    "message": "Logged in user must have (at least) one of the following permissions to access this endpoint: user_view."
  }
}
```

**Finding**: User `practica4@gmail.com` does NOT have `user_view` permission. Cannot inspect own permissions programmatically.

---

## TEST 3: List Outbreaks

**Endpoint**: `GET /api/outbreaks`
**Status**: 200 OK

| Field | Value |
|-------|-------|
| **Count** | 1 outbreak visible |
| **ID** | ba06833f-3b4d-4bd5-b4dd-4b27a8c20f19 |
| **Name** | Taller Sarampion |
| **Disease** | LNG_REFERENCE_DATA_CATEGORY_DISEASE_MEASLES |
| **Active** | True |
| **Start** | 2025-12-15 |
| **End** | 2027-12-31 |
| **Case ID Mask** | SR-9999 |
| **Contact ID Mask** | CO-9999 |

---

## TEST 4: Outbreak Details

**Endpoint**: `GET /api/outbreaks/{id}`
**Status**: 200 OK

### Case Investigation Template
- **Size**: 463,644 bytes (large custom template)
- **9 top-level sections**:
  1. `diagnostico_de_sospecha_` - Dropdown: SARAMPION, RUBEOLA, DENGUE, OTRO ARBOVIROSIS, OTRO FEBRIL EXANTEMATICA
  2. `fecha_de_notificacion` [REQUIRED]
  3. `informacion_del_paciente`
  4. `antecedentes_medicos_y_de_vacunacion` [REQUIRED]
  5. `datos_clinicos`
  6. `factores_de_riesgo` - SI/NO/DESCONOCIDO
  7. `acciones_de_respuesta` - SI/NO
  8. `clasificacion` - CLASIFICADO / 2
  9. `lugares_visitados_y_rutas_de_desplazamiento_del_caso`

### Case Classifications Available
| ID | Active |
|----|--------|
| CONFIRMADO_POR_NEXO | Yes |
| CONFIRMED | Yes |
| NOT_A_CASE_DISCARDED | Yes |
| PROBABLE | Yes |
| SOSPECHOSO_DESCARTADO | No |
| SOSPECHOSO_E | No |
| SUSPECT | Yes |

---

## TEST 5: Create Case

**Endpoint**: `POST /api/outbreaks/{id}/cases`
**Status**: 200 OK

### Minimal Payload Tested
```json
{
  "firstName": "PRUEBA",
  "middleName": "GODATA",
  "lastName": "TEST AUTOMATICO",
  "gender": "LNG_REFERENCE_DATA_CATEGORY_GENDER_MALE",
  "dob": "1990-01-15T00:00:00.000Z",
  "age": {"years": 36, "months": 0},
  "dateOfReporting": "2026-03-27T00:00:00.000Z",
  "dateOfOnset": "2026-03-25T00:00:00.000Z",
  "classification": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
  "questionnaireAnswers": { ... }
}
```

### Response
```json
{
  "id": "1dee8900-4078-477b-b3c6-87c9e24e714c",
  "visualId": null,
  "firstName": "PRUEBA",
  "classification": "LNG_REFERENCE_DATA_CATEGORY_CASE_CLASSIFICATION_SUSPECT",
  "createdAt": "2026-03-27T20:16:17.549Z"
}
```

### KEY FINDING: visualId is NULL for API-created cases
- Cases created through the web UI get auto-generated visualIds (SR-0001, SR-0002, etc.)
- Cases created through the API get `visualId: null`
- The `caseIdMask: SR-9999` only applies to web UI
- **We MUST set `visualId` explicitly in the payload** if we want case numbers

### Update Case (PUT)
**Status**: 200 OK -- partial updates work, only sends changed fields.

---

## TEST 6: Lab Results

**Endpoint**: `POST /api/outbreaks/{id}/cases/{caseId}/lab-results`
**Status**: 200 OK

### Payload
```json
{
  "sampleType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BLOOD",
  "dateSampleTaken": "2026-03-26T00:00:00.000Z",
  "testType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_LAB_TEST_ELISA_IGM",
  "testedFor": "LNG_REFERENCE_DATA_CATEGORY_DISEASE_MEASLES",
  "result": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE",
  "dateOfResult": "2026-03-27T00:00:00.000Z",
  "labName": "Laboratorio Nacional de Salud - TEST"
}
```

### Response
```json
{
  "id": "227eed5b-bce7-4c26-9f96-d03d94adf154",
  "sampleType": "LNG_REFERENCE_DATA_CATEGORY_TYPE_OF_SAMPLE_BLOOD",
  "result": "LNG_REFERENCE_DATA_CATEGORY_LAB_TEST_RESULT_POSITIVE"
}
```

### Lab Test Result Values Available
| ID | Active |
|----|--------|
| ALTA | Yes |
| BAJA | Yes |
| INVALIDO | Yes |
| MUESTRA_INADECUADA | Yes |
| NEGATIVE | Yes |
| NO_FUE_PROCESADA | Yes |
| POSITIVE | Yes |
| POSITIVE_FOR_OTHER_PATHOGENS | No |

### Sample Types Available (17 total)
- BLOOD, CSF, BIOPSIA_DE_CEREBRO_BULBO_MEDULA_ESPINAL, and 14 more

### Lab Test Types Available (15 total)
- ANTIGEN_DETECTED, AVIDEZ_RUBEOLA, ELISA_IGM, HISTOPATHOLOGY, and 11 more

---

## TEST 7: Error Testing

| Test | Payload | Status | Behavior |
|------|---------|--------|----------|
| **Empty payload** | `{}` | 200 | ACCEPTED! Creates case with no data. GoData does NOT validate required fields on API. |
| **Invalid outbreak** | Wrong UUID | 403 | "access denied to the given outbreak" |
| **Invalid gender** | `"INVALID_GENDER"` | 200 | ACCEPTED! GoData does NOT validate reference data values on API. |
| **Duplicate case** | Same name/dob | 200 | ACCEPTED! GoData creates duplicates (flags them via `duplicateKeys` but does not block). |
| **Invalid token** | `"INVALID_TOKEN"` | TIMEOUT | Server hangs ~30s then closes connection. Does NOT return 401. |
| **Wrong HTTP method** | POST to /count | N/A | Not tested due to timeout cascade |

### Critical Findings
1. **No server-side validation**: GoData API accepts ANY payload, including empty objects and invalid reference values. ALL validation must be client-side.
2. **No duplicate blocking**: Duplicates are created freely. GoData only generates `duplicateKeys` for post-hoc detection.
3. **Invalid token = HANG**: Instead of returning 401, the server hangs until timeout. Our client MUST handle timeouts gracefully.
4. **Connection resets**: After rapid sequential requests, the server occasionally resets connections (RemoteDisconnected). Need retry logic with backoff.

---

## TEST 8: Our GoDataClient

| Method | Result |
|--------|--------|
| `health()` | Returns 401 on `/system-settings/version` (endpoint blocked) |
| `test_connection()` | OK -- authenticates and confirms 1 outbreak |
| `get_outbreaks()` | OK -- returns 1 outbreak |
| `get_cases(limit=10)` | OK -- returns 5 cases |
| `get_cases_count()` | OK -- returns 5 |
| `find_case_by_visual_id("SR-0001")` | OK -- finds case correctly |
| `get_lab_results(case_id)` | OK -- returns 0 for case without labs |
| `create_case(payload)` (dry_run) | OK -- returns DRYRUN placeholder |
| `get_reference_data(category)` | OK -- returns genders, lab results, etc. |
| `get_locations()` | OK -- returns 803 locations (municipalities of Guatemala) |

### Field Map Output (map_record_to_godata)
Produces 14 top-level keys with 23 questionnaireAnswers variables. Maps correctly to GoData Guatemala format.

---

## Contacts Workflow

**Endpoint**: `GET /api/outbreaks/{id}/contacts`
**Status**: 200 OK -- currently 0 contacts in outbreak.

Contact creation endpoint exists at `POST /api/outbreaks/{id}/contacts` but was not tested with actual creation (not needed for current workflow).

---

## Reference Data Available

| Category | Count |
|----------|-------|
| Diseases | 13 |
| Sample Types | 17 |
| Lab Test Types | 15 |
| Pregnancy Status | 9 |
| Occupations | 24 |
| Genders | 2 |
| Case Classifications | 7 (4 active) |
| Lab Test Results | 8 (7 active) |
| Locations | 803 (all Guatemala municipalities) |

---

## Delete Behavior

**Endpoint**: `DELETE /api/outbreaks/{id}/cases/{caseId}`
**Status**: 204 No Content

- Delete returns 204 (success, no body)
- Appears to be HARD delete (cases disappear from listings)
- Second delete attempt returns 404

---

## Recommendations for Production Integration

1. **Always set `visualId` explicitly** -- the API does not auto-generate it from the mask
2. **Validate ALL fields client-side** before POSTing -- the API accepts anything
3. **Handle token expiry proactively** -- 600s TTL means re-auth every ~9 minutes
4. **Add retry with backoff** -- server resets connections under rapid requests
5. **Set timeout to 60s** -- invalid tokens cause 30s+ hangs
6. **Check for duplicates before creating** -- use `find_case_by_visual_id()` first
7. **health() is broken** -- `/system-settings/version` returns 401. Use `test_connection()` instead to verify connectivity
8. **Track visualId counter** -- since API doesn't auto-increment, we need to query existing cases and calculate next SR-XXXX

---

## Cleanup Confirmation

All 4 test cases created during testing were deleted:
- 1dee8900 (main test case with lab results)
- f61b70de (empty payload test)
- 8ebe614d (invalid gender test)
- 80d2c137 (duplicate test)

Final state: 5 active cases (SR-0001 through SR-0005), same as before testing.
