"""Tests for core functionality."""

import pytest
from user_port_finder.core import (
    get_user_port_range,
    is_port_free,
    find_free_port,
    find_multiple_ports,
    validate_port_in_range,
    list_ports_in_range,
    PortInfo,
    PortRange,
)
from user_port_finder.constants import (
    DEFAULT_MIN_PORT,
    DEFAULT_MAX_PORT,
    USER_RANGE_SIZE,
    PRIVILEGED_PORT_THRESHOLD,
)


class TestGetUserPortRange:
    """Tests for get_user_port_range."""

    def test_default_range(self):
        """Test that default range is calculated correctly."""
        port_range = get_user_port_range()
        assert isinstance(port_range, PortRange)
        assert port_range.start >= DEFAULT_MIN_PORT
        assert port_range.end <= DEFAULT_MAX_PORT
        assert port_range.end - port_range.start + 1 == USER_RANGE_SIZE

    def test_deterministic_per_user(self):
        """Test that same username always gets same range."""
        range1 = get_user_port_range(username="testuser")
        range2 = get_user_port_range(username="testuser")
        assert range1.start == range2.start
        assert range1.end == range2.end

    def test_different_users_get_different_ranges(self):
        """Test that different usernames get different ranges."""
        range1 = get_user_port_range(username="alice")
        range2 = get_user_port_range(username="bob")
        # Very unlikely to collide
        assert range1.start != range2.start or range1.end != range2.end

    def test_custom_min_max_ports(self):
        """Test custom port range boundaries."""
        port_range = get_user_port_range(
            username="testuser",
            min_port=20000,
            max_port=30000,
        )
        assert port_range.start >= 20000
        assert port_range.end <= 30000

    def test_range_never_below_privileged_threshold(self):
        """Test that port ranges never include privileged ports."""
        # Try many users to ensure none get privileged ports
        for i in range(100):
            port_range = get_user_port_range(username=f"user{i}")
            assert port_range.start >= PRIVILEGED_PORT_THRESHOLD


class TestIsPortFree:
    """Tests for is_port_free."""

    def test_port_free_check(self):
        """Test that port availability can be checked."""
        # We can't guarantee any specific port is free, but the function should work
        result = is_port_free(12345)
        assert isinstance(result, bool)

    def test_ipv4_and_ipv6(self):
        """Test both IPv4 and IPv6 checks."""
        ipv4_result = is_port_free(12346, ipv6=False)
        ipv6_result = is_port_free(12346, ipv6=True)
        assert isinstance(ipv4_result, bool)
        assert isinstance(ipv6_result, bool)


class TestFindFreePort:
    """Tests for find_free_port."""

    def test_find_free_port_returns_port_info(self):
        """Test that find_free_port returns PortInfo."""
        port_info = find_free_port(username="testuser")
        assert port_info is not None
        assert isinstance(port_info, PortInfo)
        assert isinstance(port_info.port, int)

    def test_port_in_user_range(self):
        """Test that found port is within user's range."""
        username = "testuser"
        port_range = get_user_port_range(username=username)
        port_info = find_free_port(username=username)

        assert port_info is not None
        assert port_range.start <= port_info.port <= port_range.end

    def test_attempts_tracking(self):
        """Test that attempts are tracked."""
        port_info = find_free_port(username="testuser")
        assert port_info is not None
        assert port_info.attempts > 0

    def test_user_information_included(self):
        """Test that user info is included in result."""
        username = "alice"
        port_info = find_free_port(username=username)
        assert port_info is not None
        assert port_info.user == username


class TestFindMultiplePorts:
    """Tests for find_multiple_ports."""

    def test_find_multiple_ports(self):
        """Test finding multiple ports."""
        ports = find_multiple_ports(count=3, username="testuser")
        assert len(ports) <= 3
        assert all(isinstance(p, PortInfo) for p in ports)

    def test_no_duplicate_ports(self):
        """Test that returned ports are unique."""
        ports = find_multiple_ports(count=5, username="testuser")
        port_numbers = [p.port for p in ports]
        assert len(port_numbers) == len(set(port_numbers))

    def test_all_ports_in_range(self):
        """Test that all found ports are in user's range."""
        username = "testuser"
        port_range = get_user_port_range(username=username)
        ports = find_multiple_ports(count=3, username=username)

        for port_info in ports:
            assert port_range.start <= port_info.port <= port_range.end


class TestValidatePortInRange:
    """Tests for validate_port_in_range."""

    def test_port_in_range(self):
        """Test validation of port in range."""
        username = "testuser"
        port_range = get_user_port_range(username=username)
        test_port = port_range.start + 100

        assert validate_port_in_range(test_port, username=username)

    def test_port_out_of_range(self):
        """Test validation of port out of range."""
        username = "testuser"
        port_range = get_user_port_range(username=username)
        test_port = port_range.end + 100

        assert not validate_port_in_range(test_port, username=username)

    def test_boundary_ports(self):
        """Test validation at range boundaries."""
        username = "testuser"
        port_range = get_user_port_range(username=username)

        assert validate_port_in_range(port_range.start, username=username)
        assert validate_port_in_range(port_range.end, username=username)
        assert not validate_port_in_range(port_range.start - 1, username=username)
        assert not validate_port_in_range(port_range.end + 1, username=username)


class TestListPortsInRange:
    """Tests for list_ports_in_range."""

    def test_list_all_ports(self):
        """Test listing all ports in range."""
        username = "testuser"
        port_range = get_user_port_range(username=username)
        ports = list_ports_in_range(username=username)

        assert isinstance(ports, list)
        # Should have many ports (minus reserved ones)
        assert len(ports) > 0
        assert all(isinstance(p, int) for p in ports)

    def test_list_free_ports(self):
        """Test listing only free ports."""
        ports = list_ports_in_range(username="testuser", only_free=True)
        assert isinstance(ports, list)
        assert all(isinstance(p, int) for p in ports)

    def test_list_used_ports(self):
        """Test listing only used ports."""
        ports = list_ports_in_range(username="testuser", only_used=True)
        assert isinstance(ports, list)
        assert all(isinstance(p, int) for p in ports)
