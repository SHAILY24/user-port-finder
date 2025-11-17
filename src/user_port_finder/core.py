"""
Core logic for finding available ports.
"""

import socket
import random
import getpass
import hashlib
from typing import Optional, Set, Tuple, List
from dataclasses import dataclass

from .constants import (
    RESERVED_PORTS,
    DEFAULT_MIN_PORT,
    DEFAULT_MAX_PORT,
    USER_RANGE_SIZE,
    LOCALHOST_IPV4,
    LOCALHOST_IPV6,
)


@dataclass
class PortInfo:
    """Information about a port allocation."""
    port: int
    user: str
    range_start: int
    range_end: int
    attempts: int = 0
    reserved_ports_avoided: int = 0


@dataclass
class PortRange:
    """Port range for a user."""
    start: int
    end: int
    user: str


def get_user_port_range(
    username: Optional[str] = None,
    min_port: int = DEFAULT_MIN_PORT,
    max_port: int = DEFAULT_MAX_PORT,
) -> PortRange:
    """
    Get the port range for a user based on username hash.

    Args:
        username: Username to get range for. If None, uses current user.
        min_port: Minimum port number in the allocation space
        max_port: Maximum port number in the allocation space

    Returns:
        PortRange: Port range information for the user
    """
    if username is None:
        username = getpass.getuser()

    # Create MD5 hash of username
    hash_object = hashlib.md5(username.encode())
    hash_hex = hash_object.hexdigest()

    # Use first 4 hex digits to determine base port
    available_range = max_port - min_port
    base_port = min_port + (int(hash_hex[:4], 16) % available_range)

    # Round to nearest thousand for start port
    start_port = (base_port // USER_RANGE_SIZE) * USER_RANGE_SIZE
    end_port = start_port + USER_RANGE_SIZE - 1

    # Ensure we don't exceed max_port
    if end_port > max_port:
        start_port = max_port - USER_RANGE_SIZE + 1
        end_port = max_port

    return PortRange(start=start_port, end=end_port, user=username)


def is_port_free(port: int, ipv6: bool = False) -> bool:
    """
    Check if a port is free on localhost.

    Args:
        port: Port number to check
        ipv6: Whether to check IPv6 (default: IPv4)

    Returns:
        bool: True if port is free, False otherwise
    """
    host = LOCALHOST_IPV6 if ipv6 else LOCALHOST_IPV4
    family = socket.AF_INET6 if ipv6 else socket.AF_INET

    try:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.bind((host, port))
            return True
    except OSError:
        return False


def find_free_port(
    max_attempts: int = 50,
    username: Optional[str] = None,
    min_port: Optional[int] = None,
    max_port: Optional[int] = None,
    ipv6: bool = False,
) -> Optional[PortInfo]:
    """
    Find a free port within the user's allocated range.

    Args:
        max_attempts: Maximum number of ports to try
        username: Username to get range for (None = current user)
        min_port: Override minimum port
        max_port: Override maximum port
        ipv6: Whether to find IPv6-compatible port

    Returns:
        Optional[PortInfo]: Port information if found, None otherwise
    """
    # Get user's port range
    port_range = get_user_port_range(
        username=username,
        min_port=min_port or DEFAULT_MIN_PORT,
        max_port=max_port or DEFAULT_MAX_PORT,
    )

    ports_tried: Set[int] = set()
    reserved_avoided = 0
    attempts = 0

    while attempts < max_attempts:
        attempts += 1

        # Generate random port in range
        port = random.randint(port_range.start, port_range.end)

        # Skip if already tried
        if port in ports_tried:
            continue

        ports_tried.add(port)

        # Skip reserved ports
        if port in RESERVED_PORTS:
            reserved_avoided += 1
            continue

        # Check if port is free
        if is_port_free(port, ipv6=ipv6):
            return PortInfo(
                port=port,
                user=port_range.user,
                range_start=port_range.start,
                range_end=port_range.end,
                attempts=attempts,
                reserved_ports_avoided=reserved_avoided,
            )

    return None


def find_multiple_ports(
    count: int,
    max_attempts: int = 100,
    username: Optional[str] = None,
    min_port: Optional[int] = None,
    max_port: Optional[int] = None,
    ipv6: bool = False,
) -> List[PortInfo]:
    """
    Find multiple free ports.

    Args:
        count: Number of ports to find
        max_attempts: Maximum attempts per port
        username: Username to get range for
        min_port: Override minimum port
        max_port: Override maximum port
        ipv6: Whether to find IPv6-compatible ports

    Returns:
        List[PortInfo]: List of found ports (may be less than count)
    """
    ports: List[PortInfo] = []
    used_ports: Set[int] = set()

    for _ in range(count):
        # Find a port
        port_info = find_free_port(
            max_attempts=max_attempts,
            username=username,
            min_port=min_port,
            max_port=max_port,
            ipv6=ipv6,
        )

        if port_info is None:
            break

        # Make sure we don't return duplicates
        if port_info.port not in used_ports:
            ports.append(port_info)
            used_ports.add(port_info.port)

    return ports


def validate_port_in_range(
    port: int,
    username: Optional[str] = None,
    min_port: Optional[int] = None,
    max_port: Optional[int] = None,
) -> bool:
    """
    Check if a port is within the user's allocated range.

    Args:
        port: Port to validate
        username: Username to check against
        min_port: Override minimum port
        max_port: Override maximum port

    Returns:
        bool: True if port is in range, False otherwise
    """
    port_range = get_user_port_range(
        username=username,
        min_port=min_port or DEFAULT_MIN_PORT,
        max_port=max_port or DEFAULT_MAX_PORT,
    )

    return port_range.start <= port <= port_range.end


def list_ports_in_range(
    username: Optional[str] = None,
    only_free: bool = False,
    only_used: bool = False,
    ipv6: bool = False,
) -> List[int]:
    """
    List all ports in the user's range.

    Args:
        username: Username to get range for
        only_free: Only return free ports
        only_used: Only return used ports
        ipv6: Check IPv6 instead of IPv4

    Returns:
        List[int]: List of port numbers
    """
    port_range = get_user_port_range(username=username)
    ports: List[int] = []

    for port in range(port_range.start, port_range.end + 1):
        # Skip reserved ports
        if port in RESERVED_PORTS:
            continue

        is_free = is_port_free(port, ipv6=ipv6)

        if only_free and is_free:
            ports.append(port)
        elif only_used and not is_free:
            ports.append(port)
        elif not only_free and not only_used:
            ports.append(port)

    return ports
