"""
Output formatters for port information.
"""

import json
from typing import List, Dict, Any
from .core import PortInfo, PortRange


def format_port_info_text(port_info: PortInfo, verbose: bool = False) -> str:
    """Format PortInfo as human-readable text."""
    if verbose:
        return (
            f"Port: {port_info.port}\n"
            f"User: {port_info.user}\n"
            f"Range: {port_info.range_start}-{port_info.range_end}\n"
            f"Attempts: {port_info.attempts}\n"
            f"Reserved ports avoided: {port_info.reserved_ports_avoided}"
        )
    return str(port_info.port)


def format_port_range_text(port_range: PortRange) -> str:
    """Format PortRange as human-readable text."""
    return (
        f"User: {port_range.user}\n"
        f"Port Range: {port_range.start}-{port_range.end}\n"
        f"Total Ports: {port_range.end - port_range.start + 1}"
    )


def port_info_to_dict(port_info: PortInfo) -> Dict[str, Any]:
    """Convert PortInfo to dictionary."""
    return {
        "port": port_info.port,
        "user": port_info.user,
        "range_start": port_info.range_start,
        "range_end": port_info.range_end,
        "attempts": port_info.attempts,
        "reserved_ports_avoided": port_info.reserved_ports_avoided,
    }


def port_range_to_dict(port_range: PortRange) -> Dict[str, Any]:
    """Convert PortRange to dictionary."""
    return {
        "user": port_range.user,
        "start": port_range.start,
        "end": port_range.end,
        "total_ports": port_range.end - port_range.start + 1,
    }


def format_json(data: Any, pretty: bool = True) -> str:
    """Format data as JSON."""
    indent = 2 if pretty else None
    return json.dumps(data, indent=indent)


def format_yaml(data: Any) -> str:
    """Format data as YAML."""
    try:
        import yaml
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    except ImportError:
        raise ImportError(
            "PyYAML is required for YAML output. "
            "Install with: pip install 'user-port-finder[yaml]'"
        )


def format_toml(data: Any) -> str:
    """Format data as TOML."""
    try:
        import tomli_w
        return tomli_w.dumps(data)
    except ImportError:
        raise ImportError(
            "tomli-w is required for TOML output. "
            "Install with: pip install 'user-port-finder[toml]'"
        )


def format_env(port_info: PortInfo, var_name: str = "PORT") -> str:
    """Format port as environment variable."""
    return f"{var_name}={port_info.port}"


def format_multiple_ports_env(
    ports: List[PortInfo],
    var_prefix: str = "PORT"
) -> str:
    """Format multiple ports as environment variables."""
    lines = []
    for i, port_info in enumerate(ports, 1):
        lines.append(f"{var_prefix}_{i}={port_info.port}")
    return "\n".join(lines)
