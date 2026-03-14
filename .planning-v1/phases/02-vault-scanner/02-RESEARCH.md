# Phase 2: Vault Scanner - Research

**Researched:** 2026-01-31
**Domain:** File system scanning, persistent caching, vocabulary extraction
**Confidence:** HIGH

## Summary

Phase 2 requires building a vault scanner that dynamically discovers the three-level hierarchy (domain → PARA → subject) from the Obsidian vault at `/Users/richardyu/PARA`. The scanner must cache this structure with a configurable TTL (default 6 hours) and expose it as a vocabulary for later classification phases. A manual rescan trigger is needed as prep for future menu bar integration.

The standard approach uses Python's built-in `pathlib` with `Path.iterdir()` for controlled traversal (avoiding recursive glob patterns that could scan too deep), combined with a simple JSON-based cache with TTL tracking. The existing codebase already demonstrates atomic JSON operations with file locking in `state.py`, providing a proven pattern to follow.

**Primary recommendation:** Use pathlib for scanning (matches existing code style), store cache as JSON in `.state/` directory (consistent with current state management), implement TTL using datetime comparisons (avoid external cache libraries for this simple use case), and provide manual rescan via a simple Python function that clears cache (defer CLI wrapper to Phase 7 menu bar work).

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pathlib | stdlib (Python 3.9+) | File system traversal | Modern, type-safe, already used in codebase |
| json | stdlib | Cache persistence | Lightweight, human-readable, matches existing state.py pattern |
| datetime | stdlib | TTL calculation | No dependency needed for simple time-based expiry |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| fcntl | stdlib (POSIX) | File locking for atomic writes | Already used in state.py - reuse pattern |
| typing | stdlib | Type hints for vocabulary structure | Improves IDE support and validation |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pathlib | os.scandir() | 2-20x faster but less readable; overkill for ~10-50 folders |
| JSON cache | diskcache library | More features (LRU, automatic cleanup) but adds dependency; unnecessary for simple TTL |
| JSON cache | shelve | Binary format harder to debug; JSON is human-readable for troubleshooting |
| Manual TTL | cachetools library | In-memory only, loses cache on restart; we need persistence |

**Installation:**
```bash
# No additional dependencies required - all stdlib
```

## Architecture Patterns

### Recommended Project Structure
```
backend/_scripts/
├── vault_scanner.py     # Main scanner module
├── state.py             # Existing state management (reuse patterns)
└── .state/
    ├── vault_cache.json # Cache file (new)
    └── [existing state files]
```

### Pattern 1: Controlled Three-Level Traversal

**What:** Explicitly scan three levels without using recursive patterns that might scan too deep.

**When to use:** When directory depth is known and fixed (domain → PARA → subject).

**Example:**
```python
from pathlib import Path
from typing import Dict, List

def scan_vault_structure(vault_path: Path) -> Dict[str, Dict[str, List[str]]]:
    """
    Scan vault for domain → PARA → subject hierarchy.

    Returns:
        {
            "Personal": {
                "1_Projects": ["apps", "writing", "reference"],
                "2_Areas": ["health", "finance"],
                ...
            },
            "CCBH": {...},
            "Just-Value": {...}
        }
    """
    structure = {}

    # Level 1: Domain folders
    for domain_path in vault_path.iterdir():
        if not domain_path.is_dir() or domain_path.name.startswith('.'):
            continue

        domain_name = domain_path.name
        structure[domain_name] = {}

        # Level 2: PARA folders (1_Projects, 2_Areas, etc.)
        for para_path in domain_path.iterdir():
            if not para_path.is_dir() or para_path.name.startswith('.'):
                continue

            para_name = para_path.name
            subjects = []

            # Level 3: Subject folders
            for subject_path in para_path.iterdir():
                if not subject_path.is_dir() or subject_path.name.startswith('.'):
                    continue
                subjects.append(subject_path.name)

            structure[domain_name][para_name] = sorted(subjects)

    return structure
```

### Pattern 2: TTL-Based Cache with Metadata

**What:** Store cached data alongside timestamp and TTL configuration.

**When to use:** When cache needs to expire after a fixed duration and be manually refreshable.

**Example:**
```python
# Source: Adapted from existing state.py patterns
from datetime import datetime, timedelta
from pathlib import Path
import json

CACHE_FILE = Path(__file__).parent / ".state" / "vault_cache.json"
DEFAULT_TTL_HOURS = 6

def load_cached_structure(ttl_hours: int = DEFAULT_TTL_HOURS) -> dict | None:
    """
    Load cached vault structure if still valid.

    Returns None if cache doesn't exist or has expired.
    """
    if not CACHE_FILE.exists():
        return None

    with open(CACHE_FILE, 'r') as f:
        cache_data = json.load(f)

    cached_at = datetime.fromisoformat(cache_data['cached_at'])
    age = datetime.now() - cached_at

    if age > timedelta(hours=ttl_hours):
        return None  # Expired

    return cache_data['structure']

def save_cached_structure(structure: dict):
    """Save vault structure with timestamp."""
    cache_data = {
        'structure': structure,
        'cached_at': datetime.now().isoformat(),
        'version': 1  # For future schema changes
    }

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f, indent=2)
```

### Pattern 3: Cache-Or-Scan Pattern

**What:** Try cache first, fall back to fresh scan if cache is invalid.

**When to use:** Main entry point for getting vault structure.

**Example:**
```python
def get_vault_structure(vault_path: Path, ttl_hours: int = DEFAULT_TTL_HOURS, force_refresh: bool = False) -> dict:
    """
    Get vault structure from cache or fresh scan.

    Args:
        vault_path: Path to vault root
        ttl_hours: Cache TTL in hours
        force_refresh: If True, bypass cache and rescan

    Returns:
        Vault structure dictionary
    """
    if not force_refresh:
        cached = load_cached_structure(ttl_hours)
        if cached is not None:
            return cached

    # Cache miss or forced refresh - scan filesystem
    structure = scan_vault_structure(vault_path)
    save_cached_structure(structure)
    return structure
```

### Anti-Patterns to Avoid

- **Using `rglob('**/*')`:** Recursively scans entire tree including deep subject subfolders, temporary files, and hidden directories. Use controlled `iterdir()` loops instead.
- **No error handling for missing directories:** Vault might not exist or permissions could deny access. Wrap filesystem operations in try/except with clear error messages.
- **Storing absolute paths in cache:** Cache becomes invalid if vault moves. Store relative structure (domain/PARA/subject names only).
- **No cache versioning:** Future schema changes will break old cache files. Include version field in cache JSON.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Atomic JSON writes | Manual file writes with locks | Reuse `state.py` patterns | Already handles locking, temp file, atomic rename |
| CLI argument parsing | Manual sys.argv parsing | argparse (stdlib) | Handles --help, type validation, subcommands automatically |
| File watching for auto-rescan | Custom polling loop | Defer to Phase 7 | File watching adds complexity; manual trigger sufficient for Phase 2 |
| Cache invalidation on vault changes | Filesystem watchers | Manual trigger + TTL | TTL provides eventual consistency; manual trigger handles immediate needs |

**Key insight:** The existing `state.py` module already demonstrates atomic JSON operations with file locking. Reuse this pattern rather than rebuilding it or adding a cache library.

## Common Pitfalls

### Pitfall 1: Symlink Loops and Permission Errors

**What goes wrong:** Scanner follows symlinks creating infinite loops, or crashes on permission-denied directories (like `.Trash`).

**Why it happens:** File systems can contain symlinks pointing to parent directories, or user doesn't have read access to all folders.

**How to avoid:**
- Use `Path.is_dir(follow_symlinks=False)` to check without following symlinks
- Use `Path.resolve()` to detect if path points outside vault
- Wrap `iterdir()` in try/except to handle PermissionError gracefully

**Warning signs:** Scanner hangs indefinitely, or crashes with "Permission denied" errors.

**Source:** [The trouble with symbolic links](https://lwn.net/Articles/899543/), [Symlink Security Vulnerabilities](https://www.cyberark.com/resources/threat-research-blog/follow-the-link-exploiting-symbolic-links-with-ease)

### Pitfall 2: Stale Cache After Vault Structure Changes

**What goes wrong:** User creates new domain or PARA folder, but scanner returns stale cached data for hours.

**Why it happens:** TTL-based caches don't detect filesystem changes between expirations.

**How to avoid:**
- Provide clear manual rescan function (VAULT-05 requirement)
- Set conservative TTL (6 hours balances freshness vs. performance)
- Document that new folders won't appear until next scan or manual refresh

**Warning signs:** User reports missing folders that exist in Finder.

**Source:** [Cache Invalidation vs. Expiration: Best Practices](https://daily.dev/blog/cache-invalidation-vs-expiration-best-practices), [Django + Redis Caching: Patterns, Pitfalls, and Real-World Lessons](https://dev.to/topunix/django-redis-caching-patterns-pitfalls-and-real-world-lessons-m7o)

### Pitfall 3: Hidden Files and System Folders

**What goes wrong:** Scanner includes `.DS_Store`, `.git`, or other hidden files/folders in vocabulary.

**Why it happens:** `iterdir()` returns all entries including hidden ones.

**How to avoid:**
- Filter out entries starting with `.` at each level
- Consider filtering `__pycache__`, `node_modules` if vault contains code
- Skip non-directory entries (files at domain/PARA levels)

**Warning signs:** Cache contains unexpected entries like `.Trash`, `.TemporaryItems`.

### Pitfall 4: Case Sensitivity Variations

**What goes wrong:** macOS file system is case-insensitive but case-preserving, causing confusion when comparing folder names.

**Why it happens:** "Personal" and "personal" are the same folder on macOS but different strings in Python.

**How to avoid:**
- Store exact case from filesystem (use `Path.name` as-is)
- Document that vocabulary is case-sensitive for classification matching
- Consider normalizing during classification (Phase 4 concern)

**Warning signs:** Classification can't find "personal" when vault has "Personal".

## Code Examples

Verified patterns from official sources and existing codebase:

### Atomic JSON Write with Locking (Reuse Pattern)

```python
# Source: backend/_scripts/state.py (existing code)
import fcntl
from pathlib import Path

def _atomic_json_write(filepath: Path, data: dict):
    """Write JSON file with locking."""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file first, then rename (atomic on POSIX)
    temp_path = filepath.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2, default=str)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    temp_path.rename(filepath)
```

### Safe Directory Traversal with Error Handling

```python
# Source: Adapted from https://realpython.com/get-all-files-in-directory-python/
from pathlib import Path
from typing import Iterator

def safe_iterdir(path: Path) -> Iterator[Path]:
    """
    Iterate directory entries with error handling.

    Skips:
    - Hidden files/folders (starting with .)
    - Permission errors
    - Symlinks
    """
    try:
        for entry in path.iterdir():
            # Skip hidden entries
            if entry.name.startswith('.'):
                continue

            # Skip symlinks to avoid loops
            if entry.is_symlink():
                continue

            # Only yield directories
            if entry.is_dir():
                yield entry

    except PermissionError:
        # Log but don't crash - user might not have access
        print(f"Warning: Permission denied for {path}")
    except OSError as e:
        # Handle other filesystem errors gracefully
        print(f"Warning: Error reading {path}: {e}")
```

### Complete Vault Scanner Module

```python
# Source: Synthesized from research and existing patterns
"""
Vault scanner for discovering domain → PARA → subject hierarchy.

Scans ~/PARA for three-level folder structure:
- Domain: Personal, CCBH, Just-Value
- PARA: 1_Projects, 2_Areas, 3_Resources, 4_Archive
- Subject: Individual project/area/resource folders
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import json
import fcntl

# Configuration
VAULT_ROOT = Path.home() / "PARA"
CACHE_FILE = Path(__file__).parent / ".state" / "vault_cache.json"
DEFAULT_TTL_HOURS = 6

class VaultScanner:
    """Discovers and caches vault structure."""

    def __init__(self, vault_path: Path = VAULT_ROOT, ttl_hours: int = DEFAULT_TTL_HOURS):
        self.vault_path = vault_path
        self.ttl_hours = ttl_hours

    def get_structure(self, force_refresh: bool = False) -> Dict[str, Dict[str, List[str]]]:
        """
        Get vault structure from cache or fresh scan.

        Args:
            force_refresh: If True, bypass cache and rescan

        Returns:
            {
                "Personal": {
                    "1_Projects": ["apps", "writing"],
                    "2_Areas": ["health"],
                    ...
                },
                ...
            }
        """
        if not force_refresh:
            cached = self._load_cache()
            if cached is not None:
                return cached

        # Scan filesystem
        structure = self._scan()
        self._save_cache(structure)
        return structure

    def manual_rescan(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Force a fresh scan, bypassing cache.

        Returns:
            Updated vault structure
        """
        return self.get_structure(force_refresh=True)

    def _scan(self) -> Dict[str, Dict[str, List[str]]]:
        """Scan vault for three-level hierarchy."""
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {self.vault_path}")

        structure = {}

        # Level 1: Domains
        for domain_path in self._safe_iterdir(self.vault_path):
            domain_name = domain_path.name
            structure[domain_name] = {}

            # Level 2: PARA folders
            for para_path in self._safe_iterdir(domain_path):
                para_name = para_path.name
                subjects = []

                # Level 3: Subjects
                for subject_path in self._safe_iterdir(para_path):
                    subjects.append(subject_path.name)

                structure[domain_name][para_name] = sorted(subjects)

        return structure

    def _safe_iterdir(self, path: Path):
        """Iterate directory, skipping hidden files and handling errors."""
        try:
            for entry in path.iterdir():
                if entry.name.startswith('.'):
                    continue
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    yield entry
        except PermissionError:
            print(f"Warning: Permission denied for {path}")
        except OSError as e:
            print(f"Warning: Error reading {path}: {e}")

    def _load_cache(self) -> Optional[Dict]:
        """Load cache if valid, None if expired or missing."""
        if not CACHE_FILE.exists():
            return None

        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)

            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            age = datetime.now() - cached_at

            if age > timedelta(hours=self.ttl_hours):
                return None

            return cache_data['structure']
        except (json.JSONDecodeError, KeyError, ValueError):
            # Corrupted cache - ignore it
            return None

    def _save_cache(self, structure: Dict):
        """Save cache with timestamp and version."""
        cache_data = {
            'structure': structure,
            'cached_at': datetime.now().isoformat(),
            'ttl_hours': self.ttl_hours,
            'version': 1
        }

        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

        # Atomic write with locking (reuse state.py pattern)
        temp_path = CACHE_FILE.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(cache_data, f, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        temp_path.rename(CACHE_FILE)

# Convenience functions for importing
def get_vault_structure(force_refresh: bool = False) -> Dict:
    """Get current vault structure (cached or fresh)."""
    scanner = VaultScanner()
    return scanner.get_structure(force_refresh)

def rescan_vault() -> Dict:
    """Force immediate vault rescan."""
    scanner = VaultScanner()
    return scanner.manual_rescan()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| os.walk() for all traversal | pathlib.iterdir() for controlled depth | Python 3.4+ (2014) | More readable, type-safe, better error messages |
| Binary serialization for cache | JSON for human-readable cache | N/A | Easier debugging, version control friendly |
| In-memory cache only | Persistent cache with TTL | N/A | Survives restarts, reduces filesystem load |
| Manual file locking | fcntl for atomic writes | POSIX standard | Prevents race conditions in concurrent access |

**Deprecated/outdated:**
- **os.walk()**: Still works but overkill for controlled depth traversal; pathlib is more readable
- **Binary serialization**: Harder to debug than JSON for configuration/cache files
- **Global cache without TTL**: Leads to indefinitely stale data; always include expiration

## Open Questions

1. **Should scanner validate PARA folder naming?**
   - What we know: Vault has `1_Projects`, `2_Areas`, `4_Archive` (no `3_Resources` in Personal)
   - What's unclear: Should scanner enforce naming convention (1-4 prefix) or accept any subfolder?
   - Recommendation: Accept any subfolder name for flexibility. Document that non-standard names will be included in vocabulary.

2. **How to handle empty PARA folders (no subjects)?**
   - What we know: CCBH domain only has `2_Areas`, other PARA folders might not exist
   - What's unclear: Include empty PARA folders in structure or omit them?
   - Recommendation: Include with empty list `[]` - shows folder exists but has no subjects yet. Useful for classification to know valid PARA targets.

3. **Should TTL be configurable via environment variable?**
   - What we know: Requirement says "configurable TTL (default 6 hours)"
   - What's unclear: Runtime config via env var, or code constant?
   - Recommendation: Start with code constant in Phase 2. Add env var in Phase 8 (First-Run Wizard) when gathering all user preferences.

## Sources

### Primary (HIGH confidence)
- Python pathlib documentation - Standard library for path operations
- Existing `backend/_scripts/state.py` - Atomic JSON write patterns with fcntl
- Existing `backend/_scripts/schema.py` - Validation patterns
- [PEP 471 – os.scandir()](https://peps.python.org/pep-0471/) - Efficient directory iteration
- [Real Python: Get All Files in Directory](https://realpython.com/get-all-files-in-directory-python/) - Modern traversal patterns

### Secondary (MEDIUM confidence)
- [Python Directory Tree Generator](https://realpython.com/directory-tree-generator-python/) - Verified by Real Python
- [JSON vs YAML vs TOML Configuration](https://dev.to/jsontoall_tools/json-vs-yaml-vs-toml-which-configuration-format-should-you-use-in-2026-1hlb) - 2026 format comparison
- [Click vs argparse](https://www.pythonsnacks.com/p/click-vs-argparse-python) - CLI framework comparison

### Tertiary (LOW confidence)
- [Cache Invalidation Best Practices](https://daily.dev/blog/cache-invalidation-vs-expiration-best-practices) - General caching guidance
- [The trouble with symbolic links](https://lwn.net/Articles/899543/) - Symlink security concerns
- [Django + Redis Caching Pitfalls](https://dev.to/topunix/django-redis-caching-patterns-pitfalls-and-real-world-lessons-m7o) - Cache staleness patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib, verified against existing codebase patterns
- Architecture: HIGH - Patterns match existing state.py and schema.py approaches
- Pitfalls: MEDIUM - Symlink/permission issues verified, cache staleness is general knowledge

**Research date:** 2026-01-31
**Valid until:** 2026-03-02 (30 days - stable stdlib features, filesystem patterns don't change rapidly)
