"""
Módulo de gestión de configuración y reglas de clasificación.
"""

import json
from pathlib import Path
from typing import Dict, List, Any

DEFAULT_CONFIG: Dict[str, Any] = {
    "categories": {
        "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico", ".tiff"],
        "Documentos": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt", ".csv", ".odt", ".epub", ".md"],
        "Audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"],
        "Videos": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm"],
        "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
        "Instaladores": [".exe", ".msi", ".iso"],
        "Codigo": [".py", ".js", ".ts", ".html", ".css", ".json", ".xml", ".sql", ".cpp", ".c", ".java", ".rs", ".go"]
    },
    "keyword_rules": {
        "La Universidad": ["tarea", "tp", "examen", "apuntes", "clase", "universidad", "mate", "fisica", "quimica", "programacion"],
        "Creador de Contenido": ["youtube", "tiktok", "reel", "miniatura", "overlay", "stream", "video_edit", "intro"],
        "Facturas": ["factura", "recibo", "pago", "invoice", "boleta", "comprobante"]
    },
    "default_category": "Otros",
    "ignored_names": [
        ".organizer_history.json",
        "config.json",
        "desktop.ini",
        "Thumbs.db",
        ".DS_Store"
    ],
    "ignored_extensions": [
        ".tmp",
        ".crdownload",
        ".part"
    ],
    "duplicate_action": "rename"
}


class ConfigManager:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.data = self.load()
        self.ext_to_category = self._build_lookup()

    def load(self) -> Dict[str, Any]:
        import shutil
        example_path = self.config_path.parent / "config.example.json"
        
        # Si no existe config.json, copiar el ejemplo si está disponible
        if not self.config_path.exists() and example_path.exists():
            try:
                shutil.copy(example_path, self.config_path)
            except Exception:
                pass

        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        self.ext_to_category = self._build_lookup()

    def _build_lookup(self) -> Dict[str, str]:
        lookup = {}
        for category, extensions in self.data.get("categories", {}).items():
            for ext in extensions:
                lookup[ext.lower()] = category
        return lookup

    def get_category_for_ext(self, ext: str) -> str:
        return self.ext_to_category.get(ext.lower(), self.data.get("default_category", "Otros"))

    def is_ignored(self, filename: str, ext: str) -> bool:
        if filename in self.data.get("ignored_names", []):
            return True
        if ext.lower() in self.data.get("ignored_extensions", []):
            return True
        return False

    def get_category_by_keyword(self, filename: str) -> str:
        """
        Busca si el nombre del archivo contiene alguna palabra clave configurada.
        Usa expresiones regulares para palabras cortas y evitar que "ia" coincida con "historia".
        Ignora tildes y mayúsculas para mayor precisión.
        """
        import re
        import unicodedata
        
        def remove_accents(text: str) -> str:
            return "".join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))

        # Normalizamos filename (minúsculas y sin tildes)
        lower_name = remove_accents(filename.lower())
        keyword_rules = self.data.get("keyword_rules", {})
        
        for category, keywords in keyword_rules.items():
            for kw in keywords:
                # Normalizamos keyword (minúsculas y sin tildes)
                kw_lower = remove_accents(kw.lower())
                
                # Para palabras cortas (<= 3 letras), obligamos a que sean palabras completas
                if len(kw_lower) <= 3:
                    pattern = r'\b' + re.escape(kw_lower) + r'\b'
                    if re.search(pattern, lower_name, flags=re.UNICODE):
                        return category
                else:
                    # Para palabras largas, permitimos coincidencia parcial
                    if kw_lower in lower_name:
                        return category
        return None
