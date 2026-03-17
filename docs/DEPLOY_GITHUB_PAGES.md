# Deploy en GitHub Pages

## Paso 1: Crear repositorio en GitHub
1. Ve a [github.com/new](https://github.com/new)
2. Nombre del repositorio: `vigilancia-sarampion` (o el nombre que desees)
3. Público o Privado (Pages funciona con ambos en cuentas Pro/Org)
4. NO inicializar con README (ya lo tienes)
5. Clic en **"Create repository"**

## Paso 2: Subir el código
```bash
cd claude
git init
git add .
git commit -m "Formulario de vigilancia epidemiológica - Sarampión IGSS"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/vigilancia-sarampion.git
git push -u origin main
```

## Paso 3: Configurar GitHub Secrets
1. En el repositorio, ve a **Settings > Secrets and variables > Actions**
2. Agrega estos secretos:

| Secret | Valor |
|--------|-------|
| `SHEETS_METHOD` | `script` (o `api`) |
| `APPS_SCRIPT_URL` | URL de tu Apps Script deployment |
| `GOOGLE_SHEETS_ID` | ID de tu spreadsheet (si usas API) |
| `GOOGLE_API_KEY` | API key (si usas API) |
| `GOOGLE_SERVICE_ACCOUNT_EMAIL` | Email de la Service Account (si usas API) |
| `BASE_PATH` | `/vigilancia-sarampion/` |

## Paso 4: Habilitar GitHub Pages
1. Ve a **Settings > Pages**
2. Source: **GitHub Actions**
3. El workflow se ejecutará automáticamente en cada push a `main`

## Paso 5: Verificar el deploy
- Tu sitio estará disponible en: `https://TU_USUARIO.github.io/vigilancia-sarampion/`
- El primer deploy puede tardar 2-3 minutos
- Verifica en la pestaña **Actions** que el workflow se ejecutó correctamente

## Dominio personalizado (Opcional)
1. En **Settings > Pages > Custom domain**
2. Ingresa tu dominio: `sarampion.igss.gob.gt` (ejemplo)
3. Agrega un registro CNAME en tu DNS apuntando a `TU_USUARIO.github.io`

## Actualizar la aplicación
Cualquier push a la rama `main` desplegará automáticamente:
```bash
git add .
git commit -m "Actualización del formulario"
git push
```

## Solución de problemas

### El sitio muestra página en blanco
- Verifica que `VITE_BASE_PATH` coincida con el nombre del repositorio
- Revisa la consola del navegador para errores

### Los datos no se envían
- Verifica que los secrets estén configurados correctamente
- Prueba el endpoint de Apps Script directamente
- Revisa la consola del navegador para errores de red
