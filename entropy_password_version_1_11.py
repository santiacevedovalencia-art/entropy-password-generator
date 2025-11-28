"""Versión 1.11 del generador de contraseñas usando datos reales de la webcam."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import string
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple
import math
import importlib
import subprocess
import threading


def _lazy_import(module_name: str, package_name: Optional[str] = None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        pkg = package_name or module_name
        print(f"[entropy-1.11] Instalando dependencia requerida: {pkg} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return importlib.import_module(module_name)


np = _lazy_import("numpy")
cv2 = _lazy_import("cv2", "opencv-python")


class CameraOpenError(RuntimeError):
    """Señala fallos al inicializar la cámara."""


class SimpleLogger:
    def __init__(self, base_path: str = "logs", filename: str = "entropy_password.log") -> None:
        os.makedirs(base_path, exist_ok=True)
        self.path = os.path.join(base_path, filename)
        self._lock = threading.Lock()

    def write(self, message: str) -> None:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} {message}\n"
        with self._lock:
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(line)


def get_logger() -> SimpleLogger:
    return SimpleLogger()


class CameraOpener:
    def __init__(self, logger: SimpleLogger) -> None:
        self.logger = logger
        self.cv2 = cv2

    def open_camera(
        self,
        *,
        preferred_index: int = 0,
        try_all: bool = True,
        max_index: int = 5,
        retries: int = 5,
        delay: float = 0.5,
        diag: bool = False,
    ):
        indices: List[int] = [preferred_index]
        if try_all:
            indices.extend([i for i in range(max_index + 1) if i != preferred_index])

        last_error: Optional[str] = None
        for index in indices:
            for attempt in range(1, max(1, retries) + 1):
                cap = cv2.VideoCapture(index, cv2.CAP_ANY)
                if cap is not None and cap.isOpened():
                    backend = -1.0
                    if hasattr(cv2, "CAP_PROP_BACKEND"):
                        backend = cap.get(cv2.CAP_PROP_BACKEND)
                    self.logger.write(
                        f"CAMERA opened index={index} backend={backend} attempt={attempt}"
                    )
                    return cap, index, backend
                if cap is not None:
                    cap.release()
                last_error = f"index={index} attempt={attempt}"
                self.logger.write(f"CAMERA open-failed {last_error}")
                if diag:
                    print(f"[entropy-1.11][diag] Falló la cámara {last_error}")
                if delay > 0:
                    time.sleep(delay)

        error_msg = "No se pudo abrir ninguna cámara disponible"
        if last_error:
            error_msg += f" (último intento: {last_error})"
        raise CameraOpenError(error_msg)

    def read_frame(self, cap, *, timeout: float):
        deadline = time.time() + max(0.1, timeout)
        while time.time() <= deadline:
            ok, frame = cap.read()
            if ok and frame is not None:
                return True, frame
            time.sleep(0.05)
        return False, None

    def _release(self, cap) -> None:
        if cap is None:
            return
        try:
            cap.release()
        except Exception:
            pass


DEFAULT_GROUPS = ("upper", "lower", "digits", "symbols")
CHAR_GROUPS: Dict[str, str] = {
    "upper": string.ascii_uppercase,
    "lower": string.ascii_lowercase,
    "digits": string.digits,
    "symbols": "!@#$%&*?-_+=[]{}ñ",
}


@dataclass
class FrameData:
    flat: List[int]
    used_camera: bool
    resolution: Tuple[int, int]
    timestamp: float
    grid_shape: Tuple[int, int]
    avg_brightness: float


def parse_groups(raw: str) -> List[str]:
    if not raw:
        return []
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


def build_charset(groups: Sequence[str], extra_chars: str) -> Tuple[str, Dict[str, str]]:
    selected: Dict[str, str] = {}
    for group in groups:
        if group not in CHAR_GROUPS:
            raise ValueError(f"Grupo desconocido: {group}")
        selected[group] = CHAR_GROUPS[group]
    charset = "".join(selected.values()) + (extra_chars or "")
    if not charset:
        raise ValueError("No hay caracteres disponibles tras aplicar los filtros")
    return charset, selected


def grid_from_bgr_array(bgr: Any, cols: int, rows: int) -> Any:
    if bgr.ndim != 3 or bgr.shape[2] != 3:
        raise ValueError("Se esperaba un frame BGR de 3 canales")
    h, w, _ = bgr.shape
    cols = max(1, cols)
    rows = max(1, rows)
    cell_w = w // cols
    cell_h = h // rows
    if cell_w == 0 or cell_h == 0:
        raise ValueError("La grilla es demasiado fina para el tamaño del frame")
    grid = np.zeros((rows, cols, 3), dtype=np.uint8)
    for r in range(rows):
        for c in range(cols):
            x0 = c * cell_w
            y0 = r * cell_h
            x1 = w if c == cols - 1 else x0 + cell_w
            y1 = h if r == rows - 1 else y0 + cell_h
            block = bgr[y0:y1, x0:x1]
            if block.size == 0:
                continue
            mean = block.reshape(-1, 3).mean(axis=0)
            # convertir BGR -> RGB y truncar
            b, g, rch = mean
            grid[r, c] = [int(rch) & 0xFF, int(g) & 0xFF, int(b) & 0xFF]
    return grid


def flatten_grid(grid: Any) -> List[int]:
    return grid.astype(int).reshape(-1).tolist()


def generate_password(
    frames: Sequence[FrameData],
    *,
    length: int,
    allowed_groups: Sequence[str],
    required_groups: Optional[Sequence[str]] = None,
    extra_chars: str = "",
) -> str:
    if not (10 <= length <= 30):
        raise ValueError("La longitud debe estar entre 10 y 30")
    charset, group_map = build_charset(allowed_groups, extra_chars)
    required = list(required_groups) if required_groups else list(allowed_groups)
    required = [grp for grp in required if grp in group_map]
    if not required:
        required = [next(iter(group_map))]

    digest_input = bytearray()
    for frame in frames:
        digest_input.extend(len(frame.flat).to_bytes(2, "little"))
        for value in frame.flat:
            digest_input.append(value & 0xFF)
        digest_input.extend(int(frame.timestamp * 1000).to_bytes(8, "little", signed=False))
        digest_input.extend(int(frame.used_camera).to_bytes(1, "little"))
        digest_input.extend(int(frame.grid_shape[0]).to_bytes(1, "little"))
        digest_input.extend(int(frame.grid_shape[1]).to_bytes(1, "little"))
        brightness_int = max(0, min(65535, int(frame.avg_brightness * 10)))
        digest_input.extend(brightness_int.to_bytes(2, "little"))
    digest_input.extend(os.urandom(16))

    digest = hashlib.sha512(digest_input).digest()
    idx = 0

    def pick(source: str) -> str:
        nonlocal idx
        byte = digest[idx % len(digest)]
        idx += 1
        return source[byte % len(source)]

    password_chars: List[str] = []
    for group in required:
        password_chars.append(pick(group_map[group]))

    while len(password_chars) < length:
        password_chars.append(pick(charset))

    for i in range(len(password_chars) - 1, 0, -1):
        j = digest[idx % len(digest)] % (i + 1)
        idx += 1
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars[:length])


def capture_frames(
    opener: CameraOpener,
    *,
    frames: int,
    interval: float,
    timeout: float,
    preview: bool,
    grid_min: int,
    grid_max: int,
    open_kwargs: Optional[Dict[str, object]] = None,
) -> List[FrameData]:
    open_kwargs = open_kwargs or {}
    cap, index, backend = opener.open_camera(**open_kwargs)
    opener.logger.write(f"SESSION camera-opened index={index} backend={backend}")
    collected: List[FrameData] = []
    cv2 = opener.cv2
    window = "entropy password 1.11"
    grid_min = max(2, grid_min)
    grid_max = max(grid_min, grid_max)

    if preview and cv2 is not None:
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    try:
        for i in range(frames):
            ok, frame = opener.read_frame(cap, timeout=timeout)
            if not ok or frame is None:
                raise RuntimeError("No se pudo leer un frame de la cámara real")

            grid_rows = random.randint(grid_min, grid_max)
            grid_cols = random.randint(grid_min, grid_max)

            preview_frame = frame
            if preview and cv2 is not None:
                preview_frame = frame.copy()
                overlay_grid(cv2, preview_frame, grid_rows, grid_cols)
                try:
                    cv2.imshow(window, preview_frame)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        print("[entropy-1.11] Preview cerrado por el usuario")
                        break
                except Exception:
                    pass

            grid = grid_from_bgr_array(frame, cols=grid_cols, rows=grid_rows)
            flat = flatten_grid(grid)
            resolution = (frame.shape[1], frame.shape[0])
            luminance = (
                0.299 * frame[:, :, 2] + 0.587 * frame[:, :, 1] + 0.114 * frame[:, :, 0]
            ).mean()

            opener.logger.write(
                f"FRAME index={i} grid_rows={grid_rows} grid_cols={grid_cols} brightness={luminance:.2f}"
            )

            collected.append(
                FrameData(
                    flat=flat,
                    used_camera=True,
                    resolution=resolution,
                    timestamp=time.time(),
                    grid_shape=(grid_rows, grid_cols),
                    avg_brightness=float(luminance),
                )
            )

            print(
                f"[entropy-1.11] Frame {i + 1}/{frames} capturado (grid {grid_rows}x{grid_cols},"
                f" brillo promedio {luminance:.1f})."
            )

            if i < frames - 1:
                time.sleep(max(0.0, interval))
    finally:
        opener._release(cap)
        if preview and cv2 is not None:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

    if not collected:
        raise RuntimeError("No se obtuvo ningún frame para generar la contraseña")

    return collected


def overlay_grid(cv2_module, frame: Any, rows: int, cols: int) -> None:
    """Dibuja una cuadrícula con estadísticas de color por celda."""

    if rows <= 0 or cols <= 0:
        return

    height, width = frame.shape[:2]
    cell_h = max(1, height // rows)
    cell_w = max(1, width // cols)

    for r in range(rows):
        for c in range(cols):
            x0 = c * cell_w
            y0 = r * cell_h
            x1 = width if c == cols - 1 else x0 + cell_w
            y1 = height if r == rows - 1 else y0 + cell_h

            block = frame[y0:y1, x0:x1]
            if block.size == 0:
                continue

            avg = block.reshape(-1, 3).mean(axis=0)
            b, g, r_val = avg
            brightness = 0.299 * r_val + 0.587 * g + 0.114 * b

            cv2_module.rectangle(frame, (x0, y0), (x1, y1), (0, 255, 0), 1)
            text = f"R:{int(r_val):03d} G:{int(g):03d} B:{int(b):03d}"
            cv2_module.putText(
                frame,
                text,
                (x0 + 5, y0 + 18),
                cv2_module.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 255),
                1,
                cv2_module.LINE_AA,
            )
            cv2_module.putText(
                frame,
                f"Brillo:{int(brightness):03d}",
                (x0 + 5, y0 + 36),
                cv2_module.FONT_HERSHEY_SIMPLEX,
                0.4,
                (255, 255, 0),
                1,
                cv2_module.LINE_AA,
            )


def write_json(path: str, frames: Sequence[FrameData], password: str) -> None:
    payload = {
        "generated_at": int(time.time()),
        "password_length": len(password),
        "frames": [
            {
                "flat": frame.flat,
                "used_camera": frame.used_camera,
                "resolution": frame.resolution,
                "timestamp": frame.timestamp,
                "grid_shape": frame.grid_shape,
                "avg_brightness": frame.avg_brightness,
            }
            for frame in frames
        ],
    }
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def prompt_open_camera() -> bool:
    """Pregunta al usuario si desea abrir la cámara."""

    if not sys.stdin.isatty():  # entorno no interactivo -> continuar
        return True

    while True:
        respuesta = input("¿Deseas abrir la cámara ahora? [S/n]: ").strip().lower()
        if respuesta in ("", "s", "si", "sí", "y", "yes"):
            return True
        if respuesta in ("n", "no"):
            return False
        print("Por favor responde con 's' o 'n'.")


def prompt_password_length(min_length: int, max_length: int) -> int:
    """Solicita una longitud de contraseña dentro de un rango."""

    if not sys.stdin.isatty():
        return min(max(min_length, 10), max_length)

    prompt = f"¿Cuántos caracteres quieres para tu contraseña? ({min_length}-{max_length}): "
    while True:
        raw = input(prompt).strip()
        if not raw:
            print(f"Usaremos la longitud mínima ({min_length}).")
            return min_length
        try:
            value = int(raw)
        except ValueError:
            print("Ingresa un número entero válido.")
            continue
        if min_length <= value <= max_length:
            return value
        print(f"Ingresa un valor entre {min_length} y {max_length}.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="entropy-password-1.11",
        description="Genera contraseñas usando la webcam como fuente de entropía",
    )
    parser.add_argument("--interval", type=float, default=0.35, help="Segundos de espera entre frames capturados")
    parser.add_argument("--timeout", type=float, default=2.0, help="Tiempo máximo para esperar cada frame")
    parser.add_argument(
        "--no-preview",
        action="store_true",
        help="No abrir la ventana de cámara durante la captura",
    )
    parser.add_argument(
        "--grid-min",
        type=int,
        default=8,
        help="Tamaño mínimo de la cuadrícula dinámica (mínimo 2)",
    )
    parser.add_argument(
        "--grid-max",
        type=int,
        default=12,
        help="Tamaño máximo de la cuadrícula dinámica",
    )
    parser.add_argument("--out-json", default=None, help="Ruta para escribir el JSON de respaldo")
    parser.add_argument("--diag", action="store_true", help="Modo diagnóstico para ver errores detallados")
    parser.add_argument(
        "--preferred-index", type=int, default=0, help="Índice primario de cámara antes de probar otros"
    )
    parser.add_argument("--max-index", type=int, default=5, help="Último índice a explorar si se activa --try-all")
    parser.add_argument("--retries", type=int, default=5, help="Reintentos por backend al abrir la cámara")
    parser.add_argument("--delay", type=float, default=0.5, help="Retraso entre intentos al abrir la cámara")
    parser.add_argument("--no-try-all", action="store_true", help="No intentar otros índices de cámara")
    parser.add_argument(
        "--launch-viewer",
        action="store_true",
        help="Abrir una ventana del viewer al finalizar la captura",
    )
    parser.add_argument(
        "--viewer-full-screen",
        action="store_true",
        help="Si se lanza el viewer, intentar mostrarlo a pantalla completa",
    )
    parser.add_argument(
        "--viewer-press-any-key",
        action="store_true",
        help="Si se lanza el viewer, pedir confirmación con una tecla antes de abrir la cámara",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not prompt_open_camera():
        print("[entropy-1.11] Operación cancelada por el usuario.")
        return 1

    password_length = prompt_password_length(10, 30)
    frames_to_capture = max(1, math.ceil(password_length / 5))

    grid_min = max(2, args.grid_min)
    grid_max = max(grid_min, args.grid_max)
    preview_enabled = not args.no_preview

    print(
        f"[entropy-1.11] Capturaremos {frames_to_capture} frame(s) con cuadrículas aleatorias entre"
        f" {grid_min}x{grid_min} y {grid_max}x{grid_max}."
    )
    print("[entropy-1.11] Proporción de captura: 1 frame por cada 5 caracteres solicitados.")
    if preview_enabled:
        print("[entropy-1.11] Se abrirá una ventana; presiona 'q' si deseas cancelar la captura.")

    logger = get_logger()
    opener = CameraOpener(logger=logger)

    try:
        frame_data = capture_frames(
            opener=opener,
            frames=frames_to_capture,
            interval=max(0.0, args.interval),
            timeout=max(0.1, args.timeout),
            preview=preview_enabled,
            grid_min=grid_min,
            grid_max=grid_max,
            open_kwargs={
                "preferred_index": args.preferred_index,
                "try_all": not args.no_try_all,
                "max_index": args.max_index,
                "retries": args.retries,
                "delay": args.delay,
                "diag": args.diag,
            },
        )
    except Exception as exc:
        print(f"[entropy-1.11][ERROR] {exc}")
        print(f"[entropy-1.11][INFO] Detalles en {logger.path}")
        if isinstance(exc, CameraOpenError):
            return 2
        return 3

    password = generate_password(
        frame_data,
        length=password_length,
        allowed_groups=DEFAULT_GROUPS,
        required_groups=None,
        extra_chars="",
    )

    print("\n=== Entropy Password Version 1.11 ===")
    print(f"Password generada ({len(password)}): {password}")
    print("[entropy-1.11] Contraseña derivada únicamente de los promedios RGB y brillo capturados.")

    if args.out_json:
        try:
            write_json(args.out_json, frame_data, password)
            print(f"[entropy-1.11] Respaldo JSON guardado en {args.out_json}")
        except Exception as exc:
            print(f"[entropy-1.11][WARN] No se pudo escribir JSON: {exc}")

    return 0
if __name__ == "__main__":
    sys.exit(main())
