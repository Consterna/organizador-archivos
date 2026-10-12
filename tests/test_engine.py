from pathlib import Path

from organizer.config import ConfigManager
from organizer.engine import OrganizerEngine, compute_file_hash, get_unique_destination


def test_compute_file_hash(tmp_path: Path) -> None:
    # Test file hash
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World", encoding="utf-8")

    hash1 = compute_file_hash(test_file)
    assert hash1 != ""

    # Same content should have same hash
    test_file2 = tmp_path / "test2.txt"
    test_file2.write_text("Hello World", encoding="utf-8")
    hash2 = compute_file_hash(test_file2)

    assert hash1 == hash2

    # Different content -> different hash
    test_file3 = tmp_path / "test3.txt"
    test_file3.write_text("Hello", encoding="utf-8")
    hash3 = compute_file_hash(test_file3)
    assert hash1 != hash3


def test_unique_destination(tmp_path: Path) -> None:
    # If folder empty, should return original name
    dest = get_unique_destination(tmp_path, "archivo.txt")
    assert dest.name == "archivo.txt"

    # If exists, should add (1)
    (tmp_path / "archivo.txt").touch()
    dest2 = get_unique_destination(tmp_path, "archivo.txt")
    assert dest2.name == "archivo (1).txt"

    # If (1) exists, should add (2)
    (tmp_path / "archivo (1).txt").touch()
    dest3 = get_unique_destination(tmp_path, "archivo.txt")
    assert dest3.name == "archivo (2).txt"

    # Test double extensions like .tar.gz
    (tmp_path / "backup.tar.gz").touch()
    dest4 = get_unique_destination(tmp_path, "backup.tar.gz")
    assert dest4.name == "backup (1).tar.gz"


def test_engine_plan_execute_and_undo(tmp_path: Path) -> None:
    src_dir = tmp_path / "source"
    tgt_dir = tmp_path / "target"
    src_dir.mkdir()
    tgt_dir.mkdir()

    (src_dir / "factura_internet.pdf").write_text("PDF_FACTURA", encoding="utf-8")
    (src_dir / "foto_viaje.jpg").write_text("JPG_DATA", encoding="utf-8")
    (src_dir / "parcial.crdownload").write_text("TEMP", encoding="utf-8")

    config = ConfigManager(config_path=tmp_path / "config.json")
    engine = OrganizerEngine(src_dir, tgt_dir, config, mode="by_category")

    plans = engine.plan()
    assert len(plans) == 2

    succ, err, session_id = engine.execute(plans)
    assert succ == 2
    assert err == 0
    assert session_id.startswith("session_")
    assert (tgt_dir / "Facturas" / "factura_internet.pdf").exists()
    assert (tgt_dir / "Imagenes" / "foto_viaje.jpg").exists()
    assert (src_dir / "parcial.crdownload").exists()

    ok, _msg, count = engine.history_mgr.undo_last_session()
    assert ok is True
    assert count == 2
    assert (src_dir / "factura_internet.pdf").exists()
    assert (src_dir / "foto_viaje.jpg").exists()
