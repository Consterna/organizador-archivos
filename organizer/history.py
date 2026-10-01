"""
Módulo de registro de historial y reversión de operaciones (Undo).
"""

import json
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class HistoryManager:
    HISTORY_FILENAME = ".organizer_history.json"

    def __init__(self, target_dir: Path):
        self.target_dir = target_dir
        self.history_file = target_dir / self.HISTORY_FILENAME

    def _load_history(self) -> List[Dict]:
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _save_history(self, history: List[Dict]):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando historial: {e}")

    def record_session(self, movements: List[Tuple[Path, Path]]) -> str:
        """
        Registra una lista de tuplas (origen, destino) como una sesión de organización.
        """
        if not movements:
            return ""

        history = self._load_history()
        session_id = f"session_{int(time.time())}"
        session_data = {
            "session_id": session_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "movements": [
                {"source": str(src), "destination": str(dst)}
                for src, dst in movements
            ]
        }
        history.append(session_data)
        self._save_history(history)
        return session_id

    def undo_last_session(self) -> Tuple[bool, str, int]:
        """
        Revierte la última sesión registrada en el historial.
        Retorna (éxito, mensaje, cantidad_revertidos).
        """
        history = self._load_history()
        if not history:
            return False, "No hay operaciones registradas para revertir.", 0

        last_session = history.pop()
        movements = last_session.get("movements", [])
        if not movements:
            self._save_history(history)
            return False, "La última sesión no contenía movimientos.", 0

        reverted_count = 0
        errors = []

        # Revertir en orden inverso
        for item in reversed(movements):
            src = Path(item["source"])
            dst = Path(item["destination"])

            if not dst.exists():
                errors.append(f"No se encontró el archivo destino para restaurar: {dst.name}")
                continue

            # Crear carpeta de origen si no existiera
            src.parent.mkdir(parents=True, exist_ok=True)

            try:
                shutil.move(str(dst), str(src))
                reverted_count += 1
                # Limpiar carpeta contenedora si quedó vacía
                try:
                    if dst.parent != self.target_dir and dst.parent.exists() and not any(dst.parent.iterdir()):
                        dst.parent.rmdir()
                except OSError:
                    pass
            except Exception as e:
                errors.append(f"Error moviendo {dst.name} a {src.name}: {e}")

        # Guardar historial actualizado sin la sesión revertida
        self._save_history(history)

        msg = f"Se revirtieron {reverted_count} archivos de la sesión {last_session['session_id']}."
        if errors:
            msg += f" Hubo {len(errors)} advertencias."
        return True, msg, reverted_count
