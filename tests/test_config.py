import json
from pathlib import Path

from organizer.config import ConfigManager


def test_default_config_loading(tmp_path: Path) -> None:
    # Si no hay config.json, debería cargar el default
    config_file = tmp_path / "config.json"
    manager = ConfigManager(config_path=config_file)
    assert manager.data["default_category"] == "Otros"
    assert "Imagenes" in manager.data["categories"]


def test_keyword_matching(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    # Inyectamos una configuración falsa para testear
    fake_config = {
        "keyword_rules": {
            "Consterna/IA": ["ia", "inteligencia"],
            "UNIVERSIDAD/Calculo": ["calculo"],
        }
    }
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(fake_config, f)

    manager = ConfigManager(config_path=config_file)

    # Prueba de palabra corta (debe respetar límites de palabra por la regex \b)
    assert manager.get_category_by_keyword("proyecto de ia.pdf") == "Consterna/IA"
    assert manager.get_category_by_keyword("historia.pdf") is None

    # Prueba con acentos / mayúsculas
    assert manager.get_category_by_keyword("cálculo_avanzado.pdf") == "UNIVERSIDAD/Calculo"
    assert manager.get_category_by_keyword("CÁLCULO_INTEGRAL.docx") == "UNIVERSIDAD/Calculo"


def test_extension_matching(tmp_path: Path) -> None:
    manager = ConfigManager(config_path=tmp_path / "config.json")
    assert manager.get_category_for_ext(".jpg") == "Imagenes"
    assert manager.get_category_for_ext(".JPG") == "Imagenes"  # case insensitive
    assert manager.get_category_for_ext(".unknown") == "Otros"
