"""
Motor de escaneo, cálculo de rutas, resolución de colisiones y ejecución.
"""

import hashlib
import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional
from organizer.config import ConfigManager
from organizer.history import HistoryManager


@dataclass
class FilePlan:
    source: Path
    destination: Path
    category: str
    is_duplicate: bool
    status: str = "PENDING"


def compute_file_hash(path: Path, block_size: int = 65536) -> str:
    """Calcula el hash SHA-256 de un archivo para detección exacta de duplicados."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(block_size), b""):
                hasher.update(block)
        return hasher.hexdigest()
    except Exception:
        return ""


def get_unique_destination(dest_dir: Path, original_filename: str) -> Path:
    """Genera un nombre de archivo único si ya existe uno en destino, respetando extensiones múltiples como .tar.gz."""
    dest_path = dest_dir / original_filename
    if not dest_path.exists():
        return dest_path

    # Separar en el primer punto para preservar ".tar.gz", ".min.js", etc.
    if "." in original_filename and not original_filename.startswith("."):
        parts = original_filename.split(".", 1)
        stem, suffix = parts[0], "." + parts[1]
    else:
        stem, suffix = original_filename, ""

    counter = 1
    while dest_path.exists():
        new_name = f"{stem} ({counter}){suffix}"
        dest_path = dest_dir / new_name
        counter += 1

    return dest_path


class OrganizerEngine:
    def __init__(self, source_dir: Path, target_dir: Path, config: ConfigManager, mode: str = "by_category"):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.config = config
        self.mode = mode
        # Guardaremos el historial en la carpeta destino para que no se borre si limpiamos descargas
        self.history_mgr = HistoryManager(target_dir)

    def _determine_target_subfolder(self, file_path: Path) -> Tuple[Path, str]:
        """Calcula la subcarpeta destino y la categoría según el modo configurado."""
        # 1. Intentar clasificar por palabra clave (Keyword)
        category = self.config.get_category_by_keyword(file_path.name)
        
        # 2. Fallback a clasificación por extensión
        if not category:
            category = self.config.get_category_for_ext(file_path.suffix)

        mtime = file_path.stat().st_mtime
        time_struct = time.localtime(mtime)

        if self.mode == "by_date":
            year = time.strftime("%Y", time_struct)
            month = time.strftime("%m-%B", time_struct)
            return self.target_dir / year / month, category
        elif self.mode == "by_category_and_date":
            year_month = time.strftime("%Y-%m", time_struct)
            return self.target_dir / category / year_month, category
        else:
            # Modo por defecto: by_category
            return self.target_dir / category, category

    def plan(self) -> List[FilePlan]:
        """Escanea la carpeta de origen y genera el plan de movimientos."""
        plans: List[FilePlan] = []
        if not self.source_dir.exists() or not self.source_dir.is_dir():
            return plans

        # Obtener solo los archivos sueltos en el directorio objetivo
        for item in self.source_dir.iterdir():
            if not item.is_file():
                continue

            if self.config.is_ignored(item.name, item.suffix):
                continue

            target_folder, category = self._determine_target_subfolder(item)

            # Comprobar colisión
            potential_dest = target_folder / item.name
            is_dup = False
            if potential_dest.exists():
                src_hash = compute_file_hash(item)
                dst_hash = compute_file_hash(potential_dest)
                if src_hash and dst_hash and src_hash == dst_hash:
                    is_dup = True

            final_dest = get_unique_destination(target_folder, item.name)

            plans.append(FilePlan(
                source=item,
                destination=final_dest,
                category=category,
                is_duplicate=is_dup
            ))

        return plans

    def execute(self, plans: List[FilePlan]) -> Tuple[int, int, str]:
        """
        Ejecuta el plan de movimientos y registra la sesión para poder hacer Undo.
        Retorna (exitosos, errores, session_id).
        """
        success_count = 0
        error_count = 0
        movements: List[Tuple[Path, Path]] = []

        for p in plans:
            try:
                # Asegurar que el directorio destino existe
                p.destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Mover el archivo
                shutil.move(str(p.source), str(p.destination))
                movements.append((p.source, p.destination))
                p.status = "SUCCESS"
                success_count += 1
            except Exception as e:
                p.status = f"ERROR: {e}"
                error_count += 1

        session_id = self.history_mgr.record_session(movements)
        return success_count, error_count, session_id
