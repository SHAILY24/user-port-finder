"""
user-port-finder: Find available ports in your user-specific range.

A Python utility that deterministically allocates port ranges to users based on
their username, avoiding privileged and well-known ports. Perfect for development
environments where multiple users need to run services without port conflicts.
"""

from .core import (
    PortInfo,
    PortRange,
    get_user_port_range,
    is_port_free,
    find_free_port,
    find_multiple_ports,
    validate_port_in_range,
    list_ports_in_range,
)
from .constants import (
    RESERVED_PORTS,
    DEFAULT_MIN_PORT,
    DEFAULT_MAX_PORT,
    USER_RANGE_SIZE,
    PRIVILEGED_PORT_THRESHOLD,
    OUTPUT_FORMATS,
)

__version__ = "0.1.0"
__all__ = [
    # Core functionality
    "PortInfo",
    "PortRange",
    "get_user_port_range",
    "is_port_free",
    "find_free_port",
    "find_multiple_ports",
    "validate_port_in_range",
    "list_ports_in_range",
    # Constants
    "RESERVED_PORTS",
    "DEFAULT_MIN_PORT",
    "DEFAULT_MAX_PORT",
    "USER_RANGE_SIZE",
    "PRIVILEGED_PORT_THRESHOLD",
    "OUTPUT_FORMATS",
]
