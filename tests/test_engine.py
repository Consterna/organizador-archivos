import pytest
from pathlib import Path
from organizer.engine import OrganizerEngine, compute_file_hash, get_unique_destination
from organizer.config import ConfigManager

def test_compute_file_hash(tmp_path):
    # Test file hash
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    
    hash1 = compute_file_hash(test_file)
    assert hash1 is not None
    
    # Same content should have same hash
    test_file2 = tmp_path / "test2.txt"
    test_file2.write_text("Hello World")
    hash2 = compute_file_hash(test_file2)
    
    assert hash1 == hash2
    
    # Different content -> different hash
    test_file3 = tmp_path / "test3.txt"
    test_file3.write_text("Hello")
    hash3 = compute_file_hash(test_file3)
    assert hash1 != hash3

def test_unique_destination(tmp_path):
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
