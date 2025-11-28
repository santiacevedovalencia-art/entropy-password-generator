# Guía de Deploy Local - Entropy Password Generator

## Requisitos Previos
- Python 3.8 o superior
- Cámara web conectada
- Navegador web moderno

## Pasos para Deploy Local

### 1. Verificar Python
```cmd
python --version
```
Debe mostrar Python 3.8 o superior.

### 2. Instalar Dependencias
```cmd
pip install -r requirements.txt
```

### 3. Ejecutar el Servidor
**Opción A - Script automático:**
```cmd
run_server.bat
```

**Opción B - Manual:**
```cmd
python app.py
```

### 4. Acceder a la Aplicación
Abrir navegador y ir a: `http://localhost:5000`

## Estructura del Proyecto
```
entropy_web/
├── app.py                          # Servidor Flask principal
├── entropy_password_version_1_11.py # Lógica del generador
├── requirements.txt                # Dependencias
├── run_server.bat                 # Script de inicio
├── public/                        # Archivos frontend
│   ├── index.html                 # Página principal
│   ├── generator.html             # Generador completo
│   ├── landing.css               # Estilos página principal
│   ├── landing.js                # JavaScript página principal
│   ├── styles.css                # Estilos generador
│   └── script.js                 # JavaScript generador
└── logs/                         # Archivos de log
```

## Funcionalidades Implementadas

### Página Principal (index.html)
- ✅ Landing page profesional
- ✅ Demo integrado del generador
- ✅ Conexión con API real
- ✅ Botones funcionales
- ✅ Diseño responsive

### Generador Completo (generator.html)
- ✅ Interfaz completa del generador
- ✅ Control de longitud (10-30 caracteres)
- ✅ Conexión con cámara web
- ✅ Generación con entropía real
- ✅ Copia automática al portapapeles

## API Endpoints
- `GET /` - Página principal
- `GET /generator.html` - Generador completo
- `GET /api/password?length=X` - Generar contraseña

## Troubleshooting

### Error de Cámara
Si aparece error de cámara:
1. Verificar que la cámara esté conectada
2. Cerrar otras aplicaciones que usen la cámara
3. Dar permisos de cámara al navegador

### Error de Dependencias
```cmd
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Puerto Ocupado
Si el puerto 5000 está ocupado, modificar en `app.py`:
```python
app.run(host="0.0.0.0", port=5001, debug=True)
```

## Para Presentación en Clase

1. **Preparación:**
   - Ejecutar `run_server.bat`
   - Abrir `http://localhost:5000`
   - Verificar que la cámara funciona

2. **Demo Sugerido:**
   - Mostrar landing page
   - Usar "Demo Rápido" para generar contraseña
   - Ir al generador completo
   - Explicar la tecnología de entropía
   - Mostrar diferentes longitudes

3. **Puntos Clave:**
   - Seguridad basada en entropía de cámara
   - Interfaz moderna y responsive
   - API REST funcional
   - Generación en tiempo real