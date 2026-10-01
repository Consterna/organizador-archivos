"""
Generador de archivos de muestra para pruebas seguras en entorno Sandbox.
"""

from pathlib import Path
import time


SAMPLE_FILES = [
    ("reporte_mensual.docx", "Documento de reporte."),
    ("factura_enero.pdf", "%PDF-1.4 Factura simulada."),
    ("lista_precios.xlsx", "Contenido simulado de hoja de cálculo."),
    ("notas_reunion.txt", "Puntos tratados en la reunión de equipo."),
    ("resumen_anual.md", "# Resumen Anual\nDatos del año."),
    ("paisaje_vacaciones.jpg", "JPEG_DUMMY_DATA"),
    ("captura_pantalla.png", "PNG_DUMMY_DATA"),
    ("logo_empresa.svg", "<svg><circle cx='50' cy='50' r='40'/></svg>"),
    ("banner_animado.gif", "GIF89a_DUMMY_DATA"),
    ("cancion_demo.mp3", "ID3_AUDIO_DATA"),
    ("efecto_sonido.wav", "RIFF_WAVE_DATA"),
    ("grabacion_webinar.mp4", "MP4_VIDEO_DATA"),
    ("trailer_video.mkv", "MKV_VIDEO_DATA"),
    ("backup_sistema.zip", "PK_ZIP_ARCHIVE_DATA"),
    ("proyecto_comprimido.rar", "RAR_ARCHIVE_DATA"),
    ("herramientas.7z", "7Z_ARCHIVE_DATA"),
    ("instalador_app.exe", "MZ_EXECUTABLE_DATA"),
    ("setup_libreria.msi", "MSI_INSTALLER_DATA"),
    ("script_analisis.py", "print('Analizando datos...')"),
    ("index.html", "<!DOCTYPE html><html><body>Test</body></html>"),
    ("estilos.css", "body { background-color: #f0f0f0; }"),
    ("api_servidor.js", "console.log('Server running');"),
    ("archivo_desconocido.xyz", "Contenido no reconocido."),
    ("descarga_incompleta.crdownload", "Descarga no terminada que debe ignorarse."),
    ("tarea_matematicas.pdf", "%PDF-1.4 Ejercicios de la universidad."),
    ("factura_luz_agosto.pdf", "%PDF-1.4 Recibo mensual de energía."),
    ("miniatura_youtube_vlog.png", "PNG_DUMMY_DATA_YOUTUBE")
]


def create_sandbox(sandbox_dir: Path) -> int:
    """Crea una carpeta de pruebas con archivos variados."""
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    created = 0

    for filename, content in SAMPLE_FILES:
        target_path = sandbox_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)
        created += 1

    return created
