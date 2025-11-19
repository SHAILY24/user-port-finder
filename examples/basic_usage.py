#!/usr/bin/env python3
"""
Basic usage examples for user-port-finder.
"""

from user_port_finder import find_free_port, get_user_port_range, find_multiple_ports


def example_1_find_single_port():
    """Find a single free port."""
    print("Example 1: Find a single free port")
    print("-" * 50)

    port_info = find_free_port()
    if port_info:
        print(f"✓ Found free port: {port_info.port}")
        print(f"  User: {port_info.user}")
        print(f"  Range: {port_info.range_start}-{port_info.range_end}")
        print(f"  Attempts: {port_info.attempts}")
        print(f"  Reserved ports avoided: {port_info.reserved_ports_avoided}")
    else:
        print("✗ Could not find free port")

    print()


def example_2_get_port_range():
    """Get your allocated port range."""
    print("Example 2: Get your allocated port range")
    print("-" * 50)

    port_range = get_user_port_range()
    print(f"User: {port_range.user}")
    print(f"Port range: {port_range.start}-{port_range.end}")
    print(f"Total ports: {port_range.end - port_range.start + 1}")

    print()


def example_3_find_multiple_ports():
    """Find multiple free ports."""
    print("Example 3: Find multiple free ports")
    print("-" * 50)

    ports = find_multiple_ports(count=5)
    print(f"Found {len(ports)} free ports:")
    for i, port_info in enumerate(ports, 1):
        print(f"  {i}. Port {port_info.port} (found after {port_info.attempts} attempts)")

    print()


def example_4_service_config():
    """Generate service configuration."""
    print("Example 4: Generate service configuration")
    print("-" * 50)

    services = ["api", "database", "redis", "frontend", "websocket"]
    ports = find_multiple_ports(count=len(services))

    print("Service configuration:")
    for service, port_info in zip(services, ports):
        print(f"{service.upper()}_PORT={port_info.port}")

    print()


def example_5_docker_compose_env():
    """Generate .env file for Docker Compose."""
    print("Example 5: Generate Docker Compose .env file")
    print("-" * 50)

    services = {
        "WEB_PORT": "Web server",
        "API_PORT": "API server",
        "DB_PORT": "PostgreSQL database",
        "REDIS_PORT": "Redis cache",
        "METRICS_PORT": "Prometheus metrics",
    }

    ports = find_multiple_ports(count=len(services))

    print("# Generated .env file for Docker Compose")
    print(f"# User: {ports[0].user if ports else 'unknown'}")
    print()
    for (var_name, description), port_info in zip(services.items(), ports):
        print(f"# {description}")
        print(f"{var_name}={port_info.port}")
        print()


if __name__ == "__main__":
    example_1_find_single_port()
    example_2_get_port_range()
    example_3_find_multiple_ports()
    example_4_service_config()
    example_5_docker_compose_env()
