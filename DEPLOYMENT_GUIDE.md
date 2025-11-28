# Guía Rápida de Deployment - Entropy Password Generator

## 🎯 Paso 1: Instalar Git (5 minutos)

1. Descarga Git desde: https://git-scm.com/download/win
2. Ejecuta el instalador con opciones por defecto
3. Reinicia VS Code después de instalar

## 🎯 Paso 2: Crear Repositorio en GitHub (5 minutos)

1. Ve a https://github.com y crea cuenta (si no tienes)
2. Click en "+" arriba a la derecha → "New repository"
3. Nombre: `entropy-password-generator`
4. Descripción: "Generador de contraseñas seguras usando entropía de cámara"
5. Público o Privado (tu elección)
6. NO marques "Initialize with README"
7. Click "Create repository"

## 🎯 Paso 3: Subir tu código a GitHub

Abre PowerShell en VS Code (en la carpeta del proyecto) y ejecuta:

```powershell
# Inicializar Git
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Initial commit - Entropy Password Generator"

# Conectar con GitHub (reemplaza TU_USUARIO y TU_REPO con los tuyos)
git remote add origin https://github.com/TU_USUARIO/entropy-password-generator.git

# Subir el código
git branch -M main
git push -u origin main
```

Si Git te pide credenciales:
- Usuario: tu username de GitHub
- Contraseña: usa un Personal Access Token (no tu contraseña real)
  - Genera token en: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token
  - Marca: "repo" (full control)
  - Copia el token y úsalo como contraseña

## 🎯 Paso 4: Deployar en Render (5 minutos)

1. Ve a https://render.com y crea cuenta (usa tu cuenta de GitHub)

2. Click en "New +" → "Web Service"

3. Conecta tu repositorio:
   - Si usas GitHub: Connect account → Selecciona tu repo
   - O usa "Public Git repository" y pega la URL

4. Configuración:
   ```
   Name: entropy-password-generator
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   Plan: Free
   ```

5. Click "Create Web Service"

6. Espera 5-10 minutos mientras Render instala y despliega

## 🎯 Paso 5: Probar tu sitio

1. Render te dará una URL tipo: `https://entropy-password-generator.onrender.com`
2. Abre esa URL en tu navegador
3. Prueba el generador de contraseñas
4. Verifica que la cámara funciona

## 🎯 Paso 6 (Opcional): Agregar Cloudflare

1. Crea cuenta en https://cloudflare.com
2. Add Site → Ingresa tu dominio (si tienes uno)
3. Si no tienes dominio, puedes:
   - Comprar uno en Namecheap, GoDaddy, etc.
   - O usar la URL de Render directamente

## ✅ Checklist de Verificación

Después de deployar, verifica:
- [ ] La página carga correctamente
- [ ] Los estilos se ven bien
- [ ] El generador funciona
- [ ] La cámara se puede activar (da permisos en el navegador)
- [ ] Las contraseñas se generan y copian
- [ ] La página de privacidad funciona

## 🐛 Solución de Problemas Comunes

### Error: "Application failed to respond"
- Revisa los logs en Render Dashboard
- Verifica que app.py esté en la raíz del proyecto
- Asegúrate que requirements.txt está presente

### Error: "No module named 'cv2'"
- El deployment está instalando opencv-python-headless
- Espera a que termine la instalación completa

### Cámara no funciona
- Asegúrate de estar usando HTTPS (Render lo provee automáticamente)
- Da permisos de cámara en tu navegador
- Algunos navegadores bloquean cámara en sitios no verificados

### El sitio "duerme" después de 15 minutos
- Normal en el plan gratuito de Render
- Primera carga toma ~30-60 segundos
- Considera plan de pago si necesitas estar siempre activo

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Render Dashboard
2. Busca el error específico en Google
3. Revisa la documentación de Render: https://render.com/docs

## 🎉 ¡Felicidades!

Si llegaste hasta aquí, tu página está en internet y funcionando.
Comparte tu URL con quien quieras: `https://tu-app.onrender.com`
