import math
import time
from collections import defaultdict
from flask import Flask, request, jsonify, make_response
from functools import wraps

from entropy_password_version_1_11 import (
    CameraOpener,
    get_logger,
    capture_frames,
    generate_password,
    DEFAULT_GROUPS,
)

app = Flask(__name__, static_folder="public", static_url_path="")

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
        "img-src 'self' data:; "
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

@app.route("/api/password", methods=["GET"])
@rate_limit
def api_password():
    raw_length = request.args.get("length", "16")
    
    # Validación de entrada más estricta
    if not raw_length or not raw_length.strip():
        return jsonify({"error": "Parámetro 'length' es requerido"}), 400
    
    try:
        length = int(raw_length)
    except ValueError:
        return jsonify({"error": "length debe ser un número entero válido"}), 400

    if length < 4 or length > 30:
        return jsonify({"error": "La longitud debe estar entre 4 y 30"}), 400

    frames_to_capture = max(1, math.ceil(length / 5))

    logger = get_logger()
    opener = CameraOpener(logger=logger)

    try:
        frame_data = capture_frames(
            opener=opener,
            frames=frames_to_capture,
            interval=0.35,
            timeout=2.0,
            preview=False,
            grid_min=8,
            grid_max=12,
            open_kwargs={
                "preferred_index": 0,
                "try_all": True,
                "max_index": 3,
                "retries": 3,
                "delay": 0.5,
                "diag": False,
            },
        )
    except Exception as exc:
        logger.write(f"ERROR generating password: {str(exc)}")
        # No exponer detalles internos del error al usuario
        return jsonify({
            "error": "No se pudo acceder a la cámara. Verifica los permisos."
        }), 500

    password = generate_password(
        frame_data,
        length=length,
        allowed_groups=DEFAULT_GROUPS,
        required_groups=None,
        extra_chars="",
    )

    return jsonify(
        {
            "password": password,
            "length": len(password),
            "frames_used": len(frame_data),
        }
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)