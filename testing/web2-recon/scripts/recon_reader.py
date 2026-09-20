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


class ReconReader:
    """Reads recon.json from NovaXinWei engagement output."""

    def __init__(self, target: str, engagements_dir: str = None):
        """
        Initialize recon reader.

        Args:
            target: Target domain (e.g., "example.com")
            engagements_dir: Base engagements directory (default: ./engagements)
        """
        self.target = target
        self.engagements_dir = Path(engagements_dir) if engagements_dir else Path("engagements")
        self.recon_path = self.engagements_dir / target / "recon.json"
        self.metadata_path = self.engagements_dir / target / "metadata.json"

    def exists(self) -> bool:
        """Check if recon.json exists for this target."""
        return self.recon_path.exists()

    def load(self) -> Optional[Dict[str, Any]]:
        """
        Load recon.json if it exists.

        Returns:
            Recon data dictionary or None if not found
        """
        if not self.recon_path.exists():
            return None

        try:
            with open(self.recon_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to read {self.recon_path}: {e}")
            return None

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
