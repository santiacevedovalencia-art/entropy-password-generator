# Entropy Web Demo (frontend + backend Python)

Estructura:

- app.py                         → Servidor Flask (backend web)
- entropy_password_version_1_11.py → Lógica de generación de contraseñas usando la webcam
- public/
    - index.html                 → Landing de marketing de Entropy
    - generator.html             → UI del generador de contraseñas
    - landing.css                → Estilos de la landing
    - styles.css                 → Estilos de la página del generador
    - script.js                  → Lógica del generador (slider, toggles, llamada a /api/password)
    - landing.js                 → Lógica básica de los modales de login/signup

## Cómo ejecutar

1. Instalar dependencias (desde esta carpeta):

   pip install flask numpy opencv-python

2. Ejecutar el servidor:

   python app.py

3. Abrir en el navegador:

   - http://localhost:5000/            → Landing
   - http://localhost:5000/generator.html → Generador (usa la cámara para generar la contraseña)

El botón "Copiar" en generator.html llama a /api/password con la longitud seleccionada
(entre 10 y 30 caracteres), genera la contraseña usando la webcam y la muestra en pantalla
además de copiarla al portapapeles.