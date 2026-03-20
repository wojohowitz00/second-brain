#!/usr/bin/env python3
"""
Vault scanner for discovering Obsidian vault structure.

Scans a PARA-organized vault to discover:
- Domain folders (Personal, CCBH, Just Value)
- PARA subfolders (1_Projects, 2_Areas, 3_Resources, 4_Archive)
- Subject folders within each PARA section

Used to build vocabulary for LLM classification.
"""

import json
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterator, List, Optional

# Configure module logger
logger = logging.getLogger(__name__)

# Default vault location
VAULT_ROOT = Path.home() / "PARA"

# State directory for cache
STATE_DIR = Path(__file__).parent / ".state"
CACHE_FILE = STATE_DIR / "vault_cache.json"

# Cache configuration
DEFAULT_TTL_HOURS = 6
CACHE_VERSION = 1


class VaultScanner:
    """
    Scans an Obsidian vault to discover its three-level structure.
    
    Structure: domain -> PARA type -> subject
    
    Features:
    - Three-level structure discovery
    - TTL-based caching
    - Vocabulary extraction for LLM prompts
    
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
    
    def __init__(self, vault_path: Path = VAULT_ROOT, ttl_hours: int = DEFAULT_TTL_HOURS):
        """
        Initialize scanner with vault path.
        
        Args:
            vault_path: Path to vault root directory
            ttl_hours: Cache time-to-live in hours
        """
        self.vault_path = vault_path
        self.ttl_hours = ttl_hours
    
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

    # -------------------------------------------------------------------------
    # Cache methods
    # -------------------------------------------------------------------------
    
    def _load_cache(self) -> Optional[Dict]:
        """
        Load cache if valid and not expired.
        
        Returns:
            Cached structure dict, or None if cache is invalid/expired
        """
        try:
            if not CACHE_FILE.exists():
                return None
            
            cache_data = json.loads(CACHE_FILE.read_text())
            
            # Validate required fields
            if "cached_at" not in cache_data or "structure" not in cache_data:
                logger.warning("Cache missing required fields, ignoring")
                return None
            
            # Check TTL
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            ttl_hours = cache_data.get("ttl_hours", DEFAULT_TTL_HOURS)
            expires_at = cached_at + timedelta(hours=ttl_hours)
            
            if datetime.now() >= expires_at:
                logger.info("Cache expired, will rescan")
                return None
            
            return cache_data["structure"]
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Cache corrupted or invalid: {e}")
            return None
    
    def _save_cache(self, structure: Dict) -> None:
        """
        Save structure to cache file.
        
        Uses atomic write (temp file + rename) for safety.
        
        Args:
            structure: Vault structure dict to cache
        """
        # Ensure state dir exists
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        cache_data = {
            "structure": structure,
            "cached_at": datetime.now().isoformat(),
            "ttl_hours": self.ttl_hours,
            "version": CACHE_VERSION
        }
        
        # Atomic write: write to temp file, then rename
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                dir=CACHE_FILE.parent,
                suffix=".json",
                delete=False
            ) as f:
                json.dump(cache_data, f, indent=2)
                temp_path = Path(f.name)
            
            temp_path.rename(CACHE_FILE)
            
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get_structure(self, force_refresh: bool = False) -> Dict[str, Dict[str, List[str]]]:
        """
        Get vault structure, using cache if valid.
        
        Args:
            force_refresh: If True, bypass cache and rescan
            
        Returns:
            Nested dict of vault structure
        """
        if not force_refresh:
            cached = self._load_cache()
            if cached is not None:
                return cached
        
        # Scan and cache
        structure = self.scan()
        self._save_cache(structure)
        return structure
    
    def manual_rescan(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Force a fresh scan, bypassing and updating cache.
        
        Returns:
            Fresh vault structure
        """
        return self.get_structure(force_refresh=True)

    # -------------------------------------------------------------------------
    # Vocabulary methods
    # -------------------------------------------------------------------------
    
    def get_vocabulary(self) -> Dict[str, List[str]]:
        """
        Extract vocabulary for LLM classification prompts.
        
        Returns:
            Dict with flat, sorted lists:
            {
                "domains": ["CCBH", "Just Value", "Personal"],
                "para_types": ["1_Projects", "2_Areas", ...],
                "subjects": ["admin", "apps", ...]
            }
        """
        structure = self.get_structure()
        
        domains = set()
        para_types = set()
        subjects = set()
        
        for domain_name, para_dict in structure.items():
            domains.add(domain_name)
            for para_name, subject_list in para_dict.items():
                para_types.add(para_name)
                subjects.update(subject_list)
        
        return {
            "domains": sorted(domains),
            "para_types": sorted(para_types),
            "subjects": sorted(subjects)
        }


# -----------------------------------------------------------------------------
# Convenience functions
# -----------------------------------------------------------------------------

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


def get_vault_structure(force_refresh: bool = False) -> Dict[str, Dict[str, List[str]]]:
    """
    Get vault structure with caching.
    
    Args:
        force_refresh: If True, bypass cache
        
    Returns:
        Vault structure dict
    """
    scanner = VaultScanner()
    return scanner.get_structure(force_refresh=force_refresh)


def rescan_vault() -> Dict[str, Dict[str, List[str]]]:
    """
    Force rescan of vault.
    
    Returns:
        Fresh vault structure
    """
    scanner = VaultScanner()
    return scanner.manual_rescan()


def get_vocabulary() -> Dict[str, List[str]]:
    """
    Get vocabulary for LLM classification.
    
    Returns:
        Dict with domains, para_types, subjects lists
    """
    scanner = VaultScanner()
    return scanner.get_vocabulary()

