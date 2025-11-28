import time
import hashlib
import os
from collections import defaultdict
from flask import Flask, request, jsonify, make_response
from functools import wraps

app = Flask(__name__, static_folder="public", static_url_path="")

# Definir grupos de caracteres directamente
DEFAULT_GROUPS = ("upper", "lower", "digits", "symbols")

# Logger simple
class SimpleLogger:
    def write(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} {message}")

def get_logger():
    return SimpleLogger()

# Rate limiting simple (en memoria)
rate_limit_data = defaultdict(list)
MAX_REQUESTS = 10  # máximo de requests
TIME_WINDOW = 60  # en 60 segundos

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        now = time.time()
        
        # Limpiar requests antiguos
        rate_limit_data[ip] = [req_time for req_time in rate_limit_data[ip] 
                               if now - req_time < TIME_WINDOW]
        
        # Verificar límite
        if len(rate_limit_data[ip]) >= MAX_REQUESTS:
            return jsonify({
                "error": "Demasiadas solicitudes. Por favor, espera un momento."
            }), 429
        
        rate_limit_data[ip].append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_security_headers(response):
    """Agregar headers de seguridad a todas las respuestas"""
    # Prevenir clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    # Prevenir MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # Content Security Policy
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "img-src 'self' data: blob:; "
        "media-src 'self' blob:; "
        "connect-src 'self'"
    )
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    # Permissions Policy
    response.headers['Permissions-Policy'] = 'camera=(self)'
    
    return response

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/generator.html")
def generator_page():
    return app.send_static_file("generator.html")

@app.route("/privacy.html")
def privacy_page():
    return app.send_static_file("privacy.html")

@app.route("/api/password", methods=["POST"])
@rate_limit
def api_password():
    """Nuevo endpoint que recibe datos de imagen desde el navegador"""
    import hashlib
    import random
    import os
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        length = data.get("length", 16)
        image_data = data.get("imageData", [])  # Array de píxeles RGB
        
        # Validación
        if not isinstance(length, int) or length < 4 or length > 30:
            return jsonify({"error": "La longitud debe estar entre 4 y 30"}), 400
        
        if not image_data or len(image_data) < 100:
            return jsonify({"error": "Datos de imagen insuficientes"}), 400
        
        # Construir entrada para el hash usando los datos de la imagen
        digest_input = bytearray()
        
        # Agregar datos de píxeles
        for pixel_value in image_data[:5000]:  # Limitar a 5000 valores
            digest_input.append(int(pixel_value) & 0xFF)
        
        # Agregar timestamp
        digest_input.extend(int(time.time() * 1000000).to_bytes(8, "little"))
        
        # Agregar entropía adicional del sistema
        digest_input.extend(os.urandom(32))
        
        # Generar hash SHA-512
        digest = hashlib.sha512(digest_input).digest()
        
        # Construir conjunto de caracteres
        charset = ""
        group_map = {
            "upper": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "lower": "abcdefghijklmnopqrstuvwxyz",
            "digits": "0123456789",
            "symbols": "!@#$%&*?-_+=[]{}ñ"
        }
        
        for group in DEFAULT_GROUPS:
            charset += group_map.get(group, "")
        
        # Generar contraseña usando el hash como fuente de entropía
        password_chars = []
        idx = 0
        
        # Asegurar al menos un carácter de cada grupo
        for group in DEFAULT_GROUPS:
            group_chars = group_map.get(group, "")
            if group_chars:
                byte = digest[idx % len(digest)]
                idx += 1
                password_chars.append(group_chars[byte % len(group_chars)])
        
        # Rellenar hasta la longitud deseada
        while len(password_chars) < length:
            byte = digest[idx % len(digest)]
            idx += 1
            password_chars.append(charset[byte % len(charset)])
        
        # Mezclar la contraseña usando el hash
        for i in range(len(password_chars) - 1, 0, -1):
            j = digest[idx % len(digest)] % (i + 1)
            idx += 1
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
        
        password = "".join(password_chars[:length])
        
        logger = get_logger()
        logger.write(f"PASSWORD generated successfully, length={length}, image_data_points={len(image_data)}")
        
        return jsonify({
            "password": password,
            "length": len(password)
        })
        
    except Exception as exc:
        logger = get_logger()
        logger.write(f"ERROR generating password: {str(exc)}")
        return jsonify({
            "error": "Error al generar la contraseña"
        }), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)