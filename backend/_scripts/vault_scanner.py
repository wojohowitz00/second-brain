#!/usr/bin/env python3
"""
Vault scanner for discovering Obsidian vault structure.

Scans a PARA-organized vault to discover:
- Domain folders (Personal, CCBH, Just Value)
- PARA subfolders (1_Projects, 2_Areas, 3_Resources, 4_Archive)
- Subject folders within each PARA section

Used to build vocabulary for LLM classification.
"""

import logging
from pathlib import Path
from typing import Dict, Iterator, List

# Configure module logger
logger = logging.getLogger(__name__)

# Default vault location
VAULT_ROOT = Path.home() / "PARA"


class VaultScanner:
    """
    Scans an Obsidian vault to discover its three-level structure.
    
    Structure: domain -> PARA type -> subject
    
    Example output:
        {
            "Personal": {
                "1_Projects": ["apps", "writing"],
                "2_Areas": ["health", "finance"]
            },
            "CCBH": {
                "2_Areas": ["clients"]
            }
        }
    """
    
    def __init__(self, vault_path: Path = VAULT_ROOT):
        """
        Initialize scanner with vault path.
        
        Args:
            vault_path: Path to vault root directory
        """
        self.vault_path = vault_path
    
    def scan(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Scan vault and return three-level structure.
        
        Returns:
            Nested dict: domain -> PARA type -> list of subjects
            
        Raises:
            FileNotFoundError: If vault_path doesn't exist
        """
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault path does not exist: {self.vault_path}")
        
        result: Dict[str, Dict[str, List[str]]] = {}
        
        # Level 1: Domains
        for domain_path in self._safe_iterdir(self.vault_path):
            if not domain_path.is_dir():
                continue
            
            domain_name = domain_path.name
            result[domain_name] = {}
            
            # Level 2: PARA folders
            for para_path in self._safe_iterdir(domain_path):
                if not para_path.is_dir():
                    continue
                
                para_name = para_path.name
                result[domain_name][para_name] = []
                
                # Level 3: Subject folders
                subjects = []
                for subject_path in self._safe_iterdir(para_path):
                    if not subject_path.is_dir():
                        continue
                    subjects.append(subject_path.name)
                
                # Sort subjects alphabetically
                result[domain_name][para_name] = sorted(subjects)
        
        return result
    
    def _safe_iterdir(self, path: Path) -> Iterator[Path]:
        """
        Safely iterate over directory contents.
        
        Filters out:
        - Hidden files/folders (starting with .)
        - Symlinks (to avoid loops)
        
        Handles:
        - PermissionError (logs warning, continues)
        
        Args:
            path: Directory to iterate
            
        Yields:
            Non-hidden, non-symlink Path objects
        """
        try:
            for entry in path.iterdir():
                # Skip hidden files/folders
                if entry.name.startswith("."):
                    continue
                
                # Skip symlinks
                if entry.is_symlink():
                    continue
                
                yield entry
                
        except PermissionError as e:
            logger.warning(f"Permission denied accessing {path}: {e}")


def scan_vault_structure(vault_path: Path = VAULT_ROOT) -> Dict[str, Dict[str, List[str]]]:
    """
    Convenience function to scan vault structure.
    
    Args:
        vault_path: Path to vault root (defaults to ~/PARA)
        
    Returns:
        Nested dict of vault structure
    """
    scanner = VaultScanner(vault_path=vault_path)
    return scanner.scan()
