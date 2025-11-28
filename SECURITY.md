# Política de Seguridad y Privacidad - Entropy Password Generator

## 🔒 Medidas de Seguridad Implementadas

### 1. **Headers de Seguridad HTTP**
- **X-Frame-Options: DENY** - Previene ataques de clickjacking
- **X-Content-Type-Options: nosniff** - Previene MIME sniffing
- **X-XSS-Protection** - Protección contra Cross-Site Scripting
- **Content-Security-Policy** - Controla qué recursos pueden cargarse
- **Referrer-Policy** - Controla información enviada en headers
- **Permissions-Policy** - Restringe acceso a APIs sensibles (solo cámara)

### 2. **Rate Limiting**
- Máximo 10 solicitudes por IP cada 60 segundos
- Previene abuso y ataques de denegación de servicio
- Protege recursos del servidor

### 3. **Validación de Entrada**
- Validación estricta de parámetros
- Límites claros (4-30 caracteres)
- Sanitización de datos de entrada
- Mensajes de error controlados sin exponer detalles internos

### 4. **Privacidad del Usuario**
- **NO se almacenan contraseñas generadas**
- **NO se guardan imágenes de la cámara**
- **NO se recopilan datos personales**
- Todo el procesamiento es en tiempo real y se descarta inmediatamente
- Los logs solo registran eventos técnicos, no datos sensibles

### 5. **HTTPS en Producción**
- Se recomienda usar Cloudflare o certificados SSL/TLS
- Render proporciona HTTPS automáticamente
- Todo el tráfico debe ser encriptado

### 6. **Acceso a Cámara**
- Solo se usa cuando el usuario solicita generar una contraseña
- Requiere permiso explícito del navegador
- Los frames capturados se procesan y eliminan inmediatamente
- No se almacenan en disco ni base de datos

## 🛡️ Recomendaciones de Uso Seguro

### Para Usuarios:
1. **Verifica la URL** - Asegúrate de estar en el sitio oficial
2. **Usa HTTPS** - Verifica el candado en la barra de direcciones
3. **Permisos de cámara** - El sitio solo necesita acceso temporal
4. **No compartas contraseñas** - Las contraseñas son únicas y privadas

### Para Administradores:
1. **Mantén dependencias actualizadas** - Revisa vulnerabilidades regularmente
2. **Monitorea logs** - Revisa el archivo `logs/entropy_password.log`
3. **Configura firewall** - Limita puertos y accesos
4. **Usa Cloudflare** - Añade capa extra de protección DDoS

## 📊 Qué se Registra en Logs

Los logs (`logs/entropy_password.log`) solo contienen:
- Timestamp de eventos
- Apertura/cierre de cámara
- Número de frames capturados
- Errores técnicos (sin datos sensibles)

**NO se registra:**
- Contraseñas generadas
- Direcciones IP de usuarios
- Datos de imágenes de la cámara
- Información personal

## 🔐 Generación de Contraseñas

### Proceso Seguro:
1. Captura frames temporales de la cámara del usuario
2. Extrae datos RGB de píxeles
3. Combina con timestamp y datos aleatorios
4. Genera hash SHA-512
5. Usa el hash como fuente de entropía
6. **Descarta todos los datos inmediatamente**

### Por qué es seguro:
- Entropía real del mundo físico (cámara)
- Imposible predecir o reproducir
- No hay almacenamiento de datos intermedios
- Cada contraseña es única por naturaleza

## 🚨 Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad, por favor:
1. NO la publiques públicamente
2. Contacta al equipo de desarrollo directamente
3. Proporciona detalles técnicos y pasos para reproducir
4. Esperaremos responder en 48 horas

## 📝 Última Actualización

Documento actualizado: Noviembre 2025
Versión de la aplicación: 1.11
