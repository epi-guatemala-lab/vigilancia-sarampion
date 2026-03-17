# Configuración de Google Sheets

## Opción A: Google Sheets API con Service Account

### Paso 1: Crear proyecto en Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Clic en **"Crear Proyecto"**
3. Nombre: `vigilancia-sarampion-igss`
4. Clic en **"Crear"**

### Paso 2: Habilitar la Google Sheets API
1. En el menú lateral: **APIs y Servicios > Biblioteca**
2. Busca **"Google Sheets API"**
3. Clic en **"Habilitar"**

### Paso 3: Crear Service Account
1. Ve a **APIs y Servicios > Credenciales**
2. Clic en **"Crear credenciales" > "Cuenta de servicio"**
3. Nombre: `formulario-sarampion`
4. Clic en **"Crear y continuar"**
5. Rol: **Editor** (o "Editor de proyecto")
6. Clic en **"Listo"**

### Paso 4: Obtener clave de la Service Account
1. En la lista de cuentas de servicio, clic en la que acabas de crear
2. Pestaña **"Claves"**
3. **"Agregar clave" > "Crear clave nueva"**
4. Formato: **JSON**
5. Se descargará un archivo `.json` — guárdalo de forma segura

### Paso 5: Compartir el Google Sheet
1. Abre tu Google Sheet de vigilancia
2. Clic en **"Compartir"**
3. Agrega el email de la Service Account (tiene formato: `nombre@proyecto.iam.gserviceaccount.com`)
4. Asigna permisos de **"Editor"**

### Paso 6: Obtener el Spreadsheet ID
- La URL de tu Sheet tiene este formato: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- Copia el `SPREADSHEET_ID`

### Paso 7: Configurar variables de entorno
Crea un archivo `.env` basado en `.env.example`:
```
VITE_SHEETS_METHOD=api
VITE_GOOGLE_SHEETS_ID=tu_spreadsheet_id
VITE_GOOGLE_API_KEY=tu_api_key
VITE_GOOGLE_SERVICE_ACCOUNT_EMAIL=tu_email@proyecto.iam.gserviceaccount.com
VITE_GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

---

## Opción B: Google Apps Script (Recomendada - Más Simple)

### Paso 1: Abrir el editor de Apps Script
1. Abre tu Google Sheet
2. Menú: **Extensiones > Apps Script**

### Paso 2: Pegar el código
Borra el contenido y pega esto:

```javascript
function doPost(e) {
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('SOSPECHOSOS');
    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    }

    var data = JSON.parse(e.postData.contents);

    // Obtener headers de la primera fila
    var headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];

    // Si no hay headers, crear la fila de headers
    if (!headers[0]) {
      headers = Object.keys(data);
      sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    }

    // Mapear datos a las columnas correctas
    var row = headers.map(function(header) {
      return data[header] || '';
    });

    // Si hay campos en los datos que no están en headers, agregarlos
    var newHeaders = [];
    Object.keys(data).forEach(function(key) {
      if (headers.indexOf(key) === -1) {
        newHeaders.push(key);
        row.push(data[key] || '');
      }
    });

    if (newHeaders.length > 0) {
      var lastCol = sheet.getLastColumn();
      sheet.getRange(1, lastCol + 1, 1, newHeaders.length).setValues([newHeaders]);
    }

    sheet.appendRow(row);

    return ContentService
      .createTextOutput(JSON.stringify({ success: true, message: 'Datos guardados correctamente' }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ success: false, error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService
    .createTextOutput(JSON.stringify({ status: 'ok', message: 'Endpoint de vigilancia sarampión IGSS activo' }))
    .setMimeType(ContentService.MimeType.JSON);
}
```

### Paso 3: Deployar como Web App
1. Clic en **"Implementar" > "Nueva implementación"**
2. Tipo: **"Aplicación web"**
3. Ejecutar como: **"Yo" (tu cuenta)**
4. Acceso: **"Cualquier persona"**
5. Clic en **"Implementar"**
6. Autoriza los permisos cuando lo solicite
7. **Copia la URL** del deployment

### Paso 4: Configurar la variable de entorno
```
VITE_SHEETS_METHOD=script
VITE_APPS_SCRIPT_URL=https://script.google.com/macros/s/TU_DEPLOYMENT_ID/exec
```

### Probar el endpoint
Puedes probar con curl:
```bash
curl -X POST "TU_URL" \
  -H "Content-Type: application/json" \
  -d '{"registro_id":"TEST001","nombre_apellido":"Prueba"}'
```
