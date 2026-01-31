#!/usr/bin/env python3
"""
Tests for vault_scanner module.

TDD approach: Tests written FIRST, implementation follows.
Tests use tmp_path fixture to avoid accessing real vault.
"""

import pytest
from pathlib import Path


class TestVaultScannerDiscover:
    """Test VaultScanner.scan() discovery behavior."""

    def test_empty_vault_returns_empty_dict(self, tmp_path):
        """Empty vault directory returns empty structure."""
        from vault_scanner import VaultScanner
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert result == {}

    def test_single_domain_no_para_folders(self, tmp_path):
        """Single domain with no PARA subfolders."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal").mkdir()
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert result == {"Personal": {}}

    def test_domain_with_para_no_subjects(self, tmp_path):
        """Domain with PARA folder but no subject folders."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert result == {"Personal": {"1_Projects": []}}

    def test_full_three_level_structure(self, tmp_path):
        """Full domain -> PARA -> subject structure."""
        from vault_scanner import VaultScanner
        
        # Create structure
        (tmp_path / "Personal" / "1_Projects" / "apps").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / "writing").mkdir(parents=True)
        (tmp_path / "Personal" / "2_Areas" / "health").mkdir(parents=True)
        (tmp_path / "CCBH" / "2_Areas" / "clients").mkdir(parents=True)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert "Personal" in result
        assert "CCBH" in result
        assert result["Personal"]["1_Projects"] == ["apps", "writing"]
        assert result["Personal"]["2_Areas"] == ["health"]
        assert result["CCBH"]["2_Areas"] == ["clients"]

    def test_hidden_files_at_domain_level_skipped(self, tmp_path):
        """Hidden files/folders at domain level are skipped."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal").mkdir()
        (tmp_path / ".DS_Store").touch()
        (tmp_path / ".obsidian").mkdir()
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert ".DS_Store" not in result
        assert ".obsidian" not in result
        assert "Personal" in result

    def test_hidden_files_at_para_level_skipped(self, tmp_path):
        """Hidden files/folders at PARA level are skipped."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        (tmp_path / "Personal" / ".DS_Store").touch()
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert ".DS_Store" not in result["Personal"]

    def test_hidden_files_at_subject_level_skipped(self, tmp_path):
        """Hidden files/folders at subject level are skipped."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal" / "1_Projects" / "apps").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / ".hidden").mkdir()
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert ".hidden" not in result["Personal"]["1_Projects"]
        assert result["Personal"]["1_Projects"] == ["apps"]

    def test_symlinks_skipped(self, tmp_path):
        """Symlinks are skipped to avoid loops."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal").mkdir()
        (tmp_path / "link_to_personal").symlink_to(tmp_path / "Personal")
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert "link_to_personal" not in result
        assert "Personal" in result

    def test_permission_denied_skipped_with_warning(self, tmp_path, monkeypatch):
        """Permission denied directories are skipped gracefully."""
        from vault_scanner import VaultScanner
        import os
        
        (tmp_path / "Personal").mkdir()
        (tmp_path / "Restricted").mkdir()
        
        # Make Restricted unreadable
        original_iterdir = Path.iterdir
        
        def mock_iterdir(self):
            if "Restricted" in str(self):
                raise PermissionError("Permission denied")
            return original_iterdir(self)
        
        monkeypatch.setattr(Path, "iterdir", mock_iterdir)
        
        scanner = VaultScanner(vault_path=tmp_path)
        # Should not raise, but skip the restricted folder
        result = scanner.scan()
        
        assert "Personal" in result

    def test_nonexistent_vault_raises_error(self, tmp_path):
        """Non-existent vault path raises FileNotFoundError."""
        from vault_scanner import VaultScanner
        
        fake_path = tmp_path / "does_not_exist"
        
        scanner = VaultScanner(vault_path=fake_path)
        
        with pytest.raises(FileNotFoundError):
            scanner.scan()

    def test_file_at_domain_level_skipped(self, tmp_path):
        """Files at domain level are skipped (only directories)."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal").mkdir()
        (tmp_path / "README.md").touch()
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert "README.md" not in result
        assert "Personal" in result

    def test_mixed_content_only_folders_included(self, tmp_path):
        """Mixed files and folders at each level - only folders included."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal" / "1_Projects" / "apps").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / "note.md").touch()
        (tmp_path / "Personal" / "dashboard.md").touch()
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert result["Personal"]["1_Projects"] == ["apps"]

    def test_subjects_sorted_alphabetically(self, tmp_path):
        """Subject lists are sorted alphabetically."""
        from vault_scanner import VaultScanner
        
        (tmp_path / "Personal" / "1_Projects" / "zebra").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / "apple").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / "mango").mkdir(parents=True)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.scan()
        
        assert result["Personal"]["1_Projects"] == ["apple", "mango", "zebra"]


class TestVaultScannerConvenience:
    """Test module-level convenience functions."""

    def test_scan_vault_structure_function(self, tmp_path, monkeypatch):
        """scan_vault_structure() convenience function works."""
        from vault_scanner import scan_vault_structure
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        
        # Patch VAULT_ROOT to use tmp_path
        import vault_scanner
        monkeypatch.setattr(vault_scanner, "VAULT_ROOT", tmp_path)
        
        result = scan_vault_structure()
        
        assert "Personal" in result


class TestVaultScannerCache:
    """Test VaultScanner caching behavior."""

    def test_no_cache_creates_cache(self, tmp_path, monkeypatch):
        """No cache file exists -> scans and creates cache."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_dir / "vault_cache.json")
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.get_structure()
        
        assert (cache_dir / "vault_cache.json").exists()
        assert "Personal" in result

    def test_valid_cache_returns_without_scanning(self, tmp_path, monkeypatch):
        """Valid cache (< TTL) returns cached structure without scanning."""
        from vault_scanner import VaultScanner
        import vault_scanner
        import json
        from datetime import datetime
        
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        # Write valid cache
        cache_data = {
            "structure": {"CachedDomain": {"1_Projects": ["from-cache"]}},
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": 6,
            "version": 1
        }
        cache_file.write_text(json.dumps(cache_data))
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.get_structure()
        
        # Should return cached data, not scan
        assert "CachedDomain" in result
        assert result["CachedDomain"]["1_Projects"] == ["from-cache"]

    def test_expired_cache_triggers_rescan(self, tmp_path, monkeypatch):
        """Expired cache (> TTL) triggers fresh scan."""
        from vault_scanner import VaultScanner
        import vault_scanner
        import json
        from datetime import datetime, timedelta
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        # Write expired cache (7 hours old)
        old_time = datetime.now() - timedelta(hours=7)
        cache_data = {
            "structure": {"OldDomain": {}},
            "cached_at": old_time.isoformat(),
            "ttl_hours": 6,
            "version": 1
        }
        cache_file.write_text(json.dumps(cache_data))
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.get_structure()
        
        # Should have scanned and found Personal, not OldDomain
        assert "Personal" in result
        assert "OldDomain" not in result

    def test_corrupted_cache_triggers_rescan(self, tmp_path, monkeypatch):
        """Corrupted cache JSON triggers fresh scan."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        # Write corrupted JSON
        cache_file.write_text("{invalid json...")
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.get_structure()
        
        assert "Personal" in result

    def test_cache_missing_timestamp_triggers_rescan(self, tmp_path, monkeypatch):
        """Cache missing timestamp triggers fresh scan."""
        from vault_scanner import VaultScanner
        import vault_scanner
        import json
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        # Write cache without timestamp
        cache_data = {"structure": {"OldDomain": {}}, "version": 1}
        cache_file.write_text(json.dumps(cache_data))
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.get_structure()
        
        assert "Personal" in result

    def test_force_refresh_bypasses_cache(self, tmp_path, monkeypatch):
        """force_refresh=True bypasses cache."""
        from vault_scanner import VaultScanner
        import vault_scanner
        import json
        from datetime import datetime
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        # Write valid cache
        cache_data = {
            "structure": {"CachedDomain": {}},
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": 6,
            "version": 1
        }
        cache_file.write_text(json.dumps(cache_data))
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.get_structure(force_refresh=True)
        
        # Should have scanned and found Personal, not CachedDomain
        assert "Personal" in result

    def test_manual_rescan_bypasses_cache(self, tmp_path, monkeypatch):
        """manual_rescan() bypasses cache."""
        from vault_scanner import VaultScanner
        import vault_scanner
        import json
        from datetime import datetime
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        # Write valid cache
        cache_data = {
            "structure": {"CachedDomain": {}},
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": 6,
            "version": 1
        }
        cache_file.write_text(json.dumps(cache_data))
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        scanner = VaultScanner(vault_path=tmp_path)
        result = scanner.manual_rescan()
        
        assert "Personal" in result

    def test_cache_persists_across_instances(self, tmp_path, monkeypatch):
        """Cache persists across VaultScanner instances."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        cache_file = cache_dir / "vault_cache.json"
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_file)
        
        # First instance creates cache
        scanner1 = VaultScanner(vault_path=tmp_path)
        scanner1.get_structure()
        
        # Second instance should use same cache
        scanner2 = VaultScanner(vault_path=tmp_path)
        result = scanner2.get_structure()
        
        assert "Personal" in result


class TestVaultScannerVocabulary:
    """Test vocabulary extraction."""

    def test_get_vocabulary_returns_flat_lists(self, tmp_path, monkeypatch):
        """get_vocabulary() returns flat lists of domains, para_types, subjects."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects" / "apps").mkdir(parents=True)
        (tmp_path / "Personal" / "2_Areas" / "health").mkdir(parents=True)
        (tmp_path / "CCBH" / "1_Projects" / "clients").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_dir / "vault_cache.json")
        
        scanner = VaultScanner(vault_path=tmp_path)
        vocab = scanner.get_vocabulary()
        
        assert "domains" in vocab
        assert "para_types" in vocab
        assert "subjects" in vocab
        assert isinstance(vocab["domains"], list)

    def test_vocabulary_includes_all_para_types(self, tmp_path, monkeypatch):
        """Vocabulary includes all unique PARA names across domains."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects").mkdir(parents=True)
        (tmp_path / "Personal" / "2_Areas").mkdir(parents=True)
        (tmp_path / "CCBH" / "3_Resources").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_dir / "vault_cache.json")
        
        scanner = VaultScanner(vault_path=tmp_path)
        vocab = scanner.get_vocabulary()
        
        assert "1_Projects" in vocab["para_types"]
        assert "2_Areas" in vocab["para_types"]
        assert "3_Resources" in vocab["para_types"]

    def test_vocabulary_includes_all_subjects(self, tmp_path, monkeypatch):
        """Vocabulary includes all unique subjects across all PARA folders."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects" / "apps").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / "writing").mkdir(parents=True)
        (tmp_path / "CCBH" / "2_Areas" / "clients").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_dir / "vault_cache.json")
        
        scanner = VaultScanner(vault_path=tmp_path)
        vocab = scanner.get_vocabulary()
        
        assert "apps" in vocab["subjects"]
        assert "writing" in vocab["subjects"]
        assert "clients" in vocab["subjects"]

    def test_vocabulary_sorted_alphabetically(self, tmp_path, monkeypatch):
        """Vocabulary lists are sorted alphabetically."""
        from vault_scanner import VaultScanner
        import vault_scanner
        
        (tmp_path / "Personal" / "1_Projects" / "zebra").mkdir(parents=True)
        (tmp_path / "Personal" / "1_Projects" / "apple").mkdir(parents=True)
        (tmp_path / "CCBH" / "1_Projects" / "mango").mkdir(parents=True)
        cache_dir = tmp_path / ".state"
        cache_dir.mkdir()
        
        monkeypatch.setattr(vault_scanner, "CACHE_FILE", cache_dir / "vault_cache.json")
        
        scanner = VaultScanner(vault_path=tmp_path)
        vocab = scanner.get_vocabulary()
        
        assert vocab["domains"] == sorted(vocab["domains"])
        assert vocab["para_types"] == sorted(vocab["para_types"])
        assert vocab["subjects"] == sorted(vocab["subjects"])
