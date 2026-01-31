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
