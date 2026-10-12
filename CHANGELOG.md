# Registro de Cambios (Changelog)

Todas las modificaciones importantes de **Organizador Inteligente de Archivos** son documentadas en este archivo.

## [1.1.0] - 2026-10-12 - Estandarización Profesional, Tipado Estricto y Sincronización de Categorías
### Cambios y Mejoras
- **Configuración Estandarizada (`pyproject.toml`):** Se incorporó `pyproject.toml` con configuración unificada para `pytest`, `ruff` y `mypy` (Python 3.10+), además de `tests/__init__.py` y actualización de `.gitignore` para excluir cachés de herramientas (`.ruff_cache/`, `.mypy_cache/`, `*.db`).
- **Sincronización de Categorías por Defecto (`organizer/config.py`):** Se alineó `DEFAULT_CONFIG` con `config.example.json` y `README.md`, incorporando `.log` en `Documentos`, `.mrpack` en `Comprimidos` y la categoría `"Juegos y Mods": [".jar"]`.
- **Tipado Estático Moderno (`mypy` y `ruff`):** Se modernizaron las anotaciones de tipos (`str | None`, `Path | None`, `dict[str, Any]`) en `main.py` y en todos los módulos de `organizer/`, logrando `0` errores en `ruff check` y `mypy`.
- **Ampliación de Suite de Pruebas (`tests/`):** Se añadieron pruebas unitarias en `tests/test_config.py` y pruebas integrales en `tests/test_engine.py` (`6 passed`), verificando enrutamiento por palabras clave con tildes y límites de palabra (`\b`), deduplicación `SHA-256`, resolución de colisiones en extensiones compuestas (`.tar.gz`) y reversión segura (`Undo`).

## [1.0.2] - 2026-10-01 - Saneamiento de Cachés y Codificación
### Correcciones
- Se añadió `.pytest_cache/` a `.gitignore` y se normalizó la codificación del repositorio en UTF-8 limpio.

## [1.0.1] - 2026-09-30 - Suite de Pruebas Unitarias, Deduplicación SHA-256 y Automatización
### Cambios y Mejoras
- **Detección de Duplicados (`duplicate_action`):** Comparación en dos fases (tamaño en bytes + hash `SHA-256` en bloques de 64 KB) para eliminar duplicados exactos en descargas o conservarlos con sufijo numérico.
- **Enrutamiento Inteligente Mejorado (`organizer/engine.py`):** Normalización Unicode (`NFD`) para ignorar tildes/diacríticos y uso de expresiones regulares con límites de palabra (`\b`) en palabras clave cortas (`<= 3` caracteres).
- **Gestión de Historial y Privacidad:** Truncado automático de entradas antiguas en `.organizer_history.json`, exclusión de `config.json` personal y `sandbox_test_out/` en `.gitignore`, y copia automática desde `config.example.json`.
- **Documentación y Pruebas Iniciales:** Adición de guía paso a paso para automatización con el Programador de Tareas de Windows (*Task Scheduler*) y creación de la suite inicial de `pytest`.

## [1.0.0] - 2026-09-30 - Lanzamiento Inicial
### Añadido
- Lanzamiento inicial de **Smart File Organizer** con interfaz interactiva en consola, modo desatendido (`--run -y`), simulación segura (`--dry-run`), reversión de movimientos (`--undo`) y generador de entorno de pruebas (`--sandbox`).
