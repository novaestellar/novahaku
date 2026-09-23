"""
Novahaku Recon Cache Reader

Reads recon.json from NovaXinWei's engagement output.
Compatible with engagements/<target>/recon.json schema v1.0.

Usage:
    from testing.web2_recon.scripts.recon_reader import ReconReader
    reader = ReconReader("example.com")
    recon = reader.load()
    if recon:
        subdomains = reader.get_subdomains()
        endpoints = reader.get_endpoints()
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# Exchange schema version. Mirrors SCHEMA_VERSION in NovaXinWei's
# engine/recon_schema.py, which is the single source of truth for recon.json.
# Bump both together or the reader will reject valid caches.
SCHEMA_VERSION = "1.0"


class ReconReader:
    """Reads recon.json from NovaXinWei engagement output."""

    def __init__(self, target: str, engagements_dir: str = None):
        """
        Initialize recon reader.

        ``target`` must be a single directory name, not a path: it comes from
        recon output (a host name), and without this guard
        engagements_dir/"../other-target"/recon.json resolves outside
        engagements_dir, so one engagement could read another's cache. An
        absolute target would ignore engagements_dir entirely.

        Args:
            target: Target domain (e.g., "example.com")
            engagements_dir: Base engagements directory (default: ./engagements)

        Raises:
            ValueError: target is empty or is not a plain directory name.
        """
        if not target or not target.strip():
            raise ValueError("target must not be empty")
        if os.sep in target or (os.altsep and os.altsep in target) or os.path.isabs(target):
            raise ValueError(f"target must be a plain directory name, got {target!r}")
        if target in (".", "..") or any(c in '<>:"|?*' or ord(c) < 32 for c in target):
            raise ValueError(f"target contains an illegal character: {target!r}")
        self.target = target
        self.engagements_dir = Path(engagements_dir) if engagements_dir else Path("engagements")
        base = self.engagements_dir.resolve()
        self.recon_path = self.engagements_dir / target / "recon.json"
        self.metadata_path = self.engagements_dir / target / "metadata.json"
        # Belt and braces: never hand a path outside the engagements root.
        if not str(self.recon_path.resolve()).startswith(str(base) + os.sep):
            raise ValueError(f"target escapes engagements_dir: {target!r}")

    def exists(self) -> bool:
        """Check if recon.json exists for this target."""
        return self.recon_path.exists()

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load recon.json if it exists.

        Validates the schema version when the field is present. A cache written
        before v1.0 has no version key - that is accepted, because rejecting it
        would break engagements created before the schema was versioned. A
        present-but-wrong version is rejected: the shape cannot be trusted.

        Returns:
            Recon data dictionary or None if not found/invalid
        """
        if not self.recon_path.exists():
            return None

        try:
            with open(self.recon_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError, UnicodeDecodeError, ValueError) as e:
            print(f"Warning: Failed to read {self.recon_path}: {e}")
            return None

        if not isinstance(data, dict):
            return None

        # Catch the wrong file before the version gate: a results.json envelope
        # carries its own payload-kind marker in "version", so blaming the
        # version would describe the wrong problem. Prefer the explicit
        # "schema_version" key when a writer provides it.
        if "results" in data or "engagement" in data:
            print(f"Warning: {self.recon_path} looks like a results.json "
                  f"envelope, not recon.json - ignoring")
            return None

        # Validate every version-bearing key that is present. Preferring
        # schema_version over version let a writer hide a wrong wire version
        # behind a correct-looking one, so a file with version='9.9' and
        # schema_version='1.0' was accepted. A recon payload legitimately carries
        # version='1.0' (the schema itself), so both keys are checked against the
        # same expected value and either being wrong rejects the file.
        for key in ("version", "schema_version"):
            declared = data.get(key)
            if declared is not None and declared != SCHEMA_VERSION:
                print(f"Warning: {self.recon_path} declares {key} {declared!r}, "
                      f"expected {SCHEMA_VERSION!r} - ignoring")
                return None

        return data

    def load_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Load metadata.json if it exists.

        Returns:
            Metadata dictionary or None if not found
        """
        if not self.metadata_path.exists():
            return None

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read {self.metadata_path}: {e}")
            return None

    def get_subdomains(self) -> List[str]:
        """Get subdomains from recon data."""
        data = self.load()
        if data and "recon" in data:
            return data["recon"].get("subdomains", [])
        return []

    def get_ports(self) -> List[int]:
        """Get open ports from recon data."""
        data = self.load()
        if data and "recon" in data:
            return data["recon"].get("ports", [])
        return []

    def get_endpoints(self) -> List[str]:
        """Get discovered endpoints from recon data."""
        data = self.load()
        if data and "recon" in data:
            return data["recon"].get("endpoints", [])
        return []

    def get_tech_stack(self) -> Dict[str, Any]:
        """Get technology stack from recon data."""
        data = self.load()
        if data and "recon" in data:
            return data["recon"].get("tech_stack", {})
        return {}

    def get_waf(self) -> Dict[str, Any]:
        """Get WAF detection results from recon data."""
        data = self.load()
        if data and "recon" in data:
            return data["recon"].get("waf", {})
        return {}

    def get_origin_ip(self) -> Optional[str]:
        """Get origin IP from recon data."""
        data = self.load()
        if data and "recon" in data:
            return data["recon"].get("origin_ip")
        return None

    def summary(self) -> str:
        """Get human-readable summary of recon data."""
        data = self.load()
        if not data:
            return f"No recon data found for {self.target}"

        recon = data.get("recon", {})
        lines = [
            f"=== Recon Summary for {self.target} ===",
            f"Subdomains: {len(recon.get('subdomains', []))}",
            f"Open Ports: {len(recon.get('ports', []))}",
            f"Endpoints: {len(recon.get('endpoints', []))}",
            f"Tech Stack: {list(recon.get('tech_stack', {}).keys())}",
            f"WAF: {recon.get('waf', {}).get('product', 'None')}",
            f"Origin IP: {recon.get('origin_ip', 'Unknown')}",
            f"Source: {data.get('source', 'Unknown')}",
            f"Timestamp: {data.get('timestamp', 'Unknown')}",
        ]

        meta = self.load_metadata()
        if meta and "stats" in meta:
            stats = meta["stats"]
            lines.extend([
                f"Fetches: {stats.get('fetches', 0)}",
                f"Cache Hits: {stats.get('cache_hits', 0)}",
                f"Channels: {stats.get('channels_used', [])}",
            ])

        return "\n".join(lines)


def read_recon(target: str, engagements_dir: str = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to read recon data.

    Args:
        target: Target domain
        engagements_dir: Base engagements directory

    Returns:
        Recon data dictionary or None
    """
    reader = ReconReader(target, engagements_dir)
    return reader.load()


# --- Plan-named API ---------------------------------------------------------
# INTEGRATION_PLAN.md names load_recon() / get_waf_info() / get_tech_stack().
# The class above is the primary interface and stays authoritative; these are
# thin wrappers so the documented names resolve. Nothing was renamed - 1 known
# caller (engage_runner.read_recon) loads ReconReader by path.


def load_recon(target: str, engagements_dir: str = None) -> Optional[Dict[str, Any]]:
    """Load recon data. Alias for read_recon, matching the integration plan."""
    return read_recon(target, engagements_dir)


def get_waf_info(target: str, engagements_dir: str = None) -> Optional[Dict[str, Any]]:
    """Extract WAF detection info. None when absent or cache invalid."""
    data = read_recon(target, engagements_dir)
    if data is None:
        return None
    return data.get("recon", {}).get("waf")


def get_tech_stack(target: str, engagements_dir: str = None) -> Optional[Dict[str, Any]]:
    """Extract tech stack. None when absent or cache invalid."""
    data = read_recon(target, engagements_dir)
    if data is None:
        return None
    return data.get("recon", {}).get("tech_stack", {})
