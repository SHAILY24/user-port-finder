"""Tests for output formatters."""

import json
import pytest
from user_port_finder.core import PortInfo, PortRange
from user_port_finder.formatters import (
    format_port_info_text,
    format_port_range_text,
    port_info_to_dict,
    port_range_to_dict,
    format_json,
    format_env,
    format_multiple_ports_env,
)


class TestPortInfoFormatters:
    """Tests for PortInfo formatters."""

    @pytest.fixture
    def sample_port_info(self):
        """Sample PortInfo for testing."""
        return PortInfo(
            port=12345,
            user="testuser",
            range_start=12000,
            range_end=12999,
            attempts=5,
            reserved_ports_avoided=2,
        )

    def test_format_port_info_text_simple(self, sample_port_info):
        """Test simple text formatting."""
        result = format_port_info_text(sample_port_info, verbose=False)
        assert result == "12345"

    def test_format_port_info_text_verbose(self, sample_port_info):
        """Test verbose text formatting."""
        result = format_port_info_text(sample_port_info, verbose=True)
        assert "12345" in result
        assert "testuser" in result
        assert "12000-12999" in result

    def test_port_info_to_dict(self, sample_port_info):
        """Test conversion to dictionary."""
        result = port_info_to_dict(sample_port_info)
        assert result["port"] == 12345
        assert result["user"] == "testuser"
        assert result["range_start"] == 12000
        assert result["range_end"] == 12999
        assert result["attempts"] == 5
        assert result["reserved_ports_avoided"] == 2

    def test_format_json(self, sample_port_info):
        """Test JSON formatting."""
        data = port_info_to_dict(sample_port_info)
        result = format_json(data, pretty=True)
        parsed = json.loads(result)
        assert parsed["port"] == 12345

    def test_format_env(self, sample_port_info):
        """Test environment variable formatting."""
        result = format_env(sample_port_info)
        assert result == "PORT=12345"

    def test_format_env_custom_var(self, sample_port_info):
        """Test environment variable with custom name."""
        result = format_env(sample_port_info, var_name="MY_PORT")
        assert result == "MY_PORT=12345"


class TestPortRangeFormatters:
    """Tests for PortRange formatters."""

    @pytest.fixture
    def sample_port_range(self):
        """Sample PortRange for testing."""
        return PortRange(start=12000, end=12999, user="testuser")

    def test_format_port_range_text(self, sample_port_range):
        """Test port range text formatting."""
        result = format_port_range_text(sample_port_range)
        assert "testuser" in result
        assert "12000-12999" in result
        assert "1000" in result  # total ports

    def test_port_range_to_dict(self, sample_port_range):
        """Test conversion to dictionary."""
        result = port_range_to_dict(sample_port_range)
        assert result["user"] == "testuser"
        assert result["start"] == 12000
        assert result["end"] == 12999
        assert result["total_ports"] == 1000


class TestMultiplePortsFormatters:
    """Tests for multiple ports formatting."""

    @pytest.fixture
    def sample_ports(self):
        """Sample list of PortInfo for testing."""
        return [
            PortInfo(12345, "testuser", 12000, 12999, 1, 0),
            PortInfo(12567, "testuser", 12000, 12999, 2, 1),
            PortInfo(12890, "testuser", 12000, 12999, 3, 0),
        ]

    def test_format_multiple_ports_env(self, sample_ports):
        """Test formatting multiple ports as env vars."""
        result = format_multiple_ports_env(sample_ports)
        lines = result.split("\n")
        assert len(lines) == 3
        assert "PORT_1=12345" in lines
        assert "PORT_2=12567" in lines
        assert "PORT_3=12890" in lines

    def test_format_multiple_ports_env_custom_prefix(self, sample_ports):
        """Test custom prefix for multiple ports."""
        result = format_multiple_ports_env(sample_ports, var_prefix="MY_SERVICE")
        assert "MY_SERVICE_1=12345" in result
        assert "MY_SERVICE_2=12567" in result
