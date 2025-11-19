# user-port-finder

Find available ports in your user-specific range - avoiding conflicts in multi-user development environments.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Problem

In shared development environments (servers, cloud instances, dev containers), multiple users need to run services on different ports. Manual port management leads to:

- **Port conflicts** when multiple users pick the same port
- **Privileged port issues** (ports < 1024 require root)
- **Well-known port collisions** (MySQL 3306, PostgreSQL 5432, Redis 6379, etc.)
- **Manual coordination** overhead ("who's using port 8080?")

## Solution

`user-port-finder` automatically allocates a **deterministic 1000-port range** to each user based on their username hash. No coordination needed, no conflicts, no root required.

### Features

- **Deterministic allocation**: Same username always gets the same port range
- **Collision-free**: Each user gets a unique 1000-port range (10000-60000)
- **Smart avoidance**: Skips 63+ well-known ports (databases, web servers, message queues)
- **No privileges needed**: Operates entirely in unprivileged port space (≥1024)
- **Multiple output formats**: text, JSON, YAML, TOML, environment variables
- **IPv4 and IPv6 support**: Find ports that work with both protocols
- **Type-safe**: Full Python type hints with dataclasses
- **CLI and library**: Use as command-line tool or Python library

## Installation

```bash
# Basic installation
pip install user-port-finder

# With YAML support
pip install user-port-finder[yaml]

# With TOML support
pip install user-port-finder[toml]

# With all optional dependencies
pip install user-port-finder[all]
```

## Quick Start

### Command Line

```bash
# Find one free port in your range
user-port-finder
# Output: 42157

# Find multiple ports
user-port-finder --count 3
# Output:
# 42157
# 42891
# 42034

# See your allocated port range
user-port-finder --show-range
# Output:
# User: john
# Port Range: 42000-42999
# Total Ports: 1000

# Verbose output with statistics
user-port-finder --verbose
# Output:
# Port: 42157
# User: john
# Range: 42000-42999
# Attempts: 3
# Reserved ports avoided: 1

# Output as JSON
user-port-finder --format json
# Output: {"port": 42157, "user": "john", "range_start": 42000, ...}

# Output as environment variable
user-port-finder --format env
# Output: PORT=42157

user-port-finder --format env --env-var MY_API_PORT
# Output: MY_API_PORT=42157

# Check if a specific port is in your range
user-port-finder --check 42500
# Output: Port 42500 in range 42000-42999: YES

# List all free ports in your range
user-port-finder --list-free

# List all used ports in your range
user-port-finder --list-used
```

### Python Library

```python
from user_port_finder import find_free_port, get_user_port_range

# Find a free port
port_info = find_free_port()
print(f"Use port: {port_info.port}")
print(f"Your range: {port_info.range_start}-{port_info.range_end}")

# Get your port range
port_range = get_user_port_range()
print(f"User: {port_range.user}")
print(f"Range: {port_range.start}-{port_range.end}")

# Find multiple ports
from user_port_finder import find_multiple_ports

ports = find_multiple_ports(count=3)
for p in ports:
    print(f"Port {p.port} (attempt #{p.attempts})")

# Check if port is in your range
from user_port_finder import validate_port_in_range

if validate_port_in_range(42500):
    print("Port 42500 is in your range!")

# Find IPv6-compatible port
port_info = find_free_port(ipv6=True)
```

## Real-World Examples

### Start a development server

```bash
# In your startup script
export API_PORT=$(user-port-finder)
python -m http.server $API_PORT
```

### Docker Compose with dynamic ports

```bash
# Generate .env file
user-port-finder --count 3 --format env > .env
# Creates:
# PORT_1=42157
# PORT_2=42891
# PORT_3=42034
```

### Multi-service development

```python
#!/usr/bin/env python3
from user_port_finder import find_multiple_ports

# Allocate ports for all services
services = ["api", "database", "redis", "frontend"]
ports = find_multiple_ports(count=len(services))

# Generate config
for service, port_info in zip(services, ports):
    print(f"{service.upper()}_PORT={port_info.port}")
```

Output:
```
API_PORT=42157
DATABASE_PORT=42891
REDIS_PORT=42034
FRONTEND_PORT=42456
```

### Integration with existing tools

```bash
# Use with curl
curl http://localhost:$(user-port-finder --quiet)

# Use with database connection
export DB_PORT=$(user-port-finder)
psql -h localhost -p $DB_PORT -U myuser

# Use with Node.js
PORT=$(user-port-finder) npm start

# Use with Python Flask
export FLASK_RUN_PORT=$(user-port-finder)
flask run
```

## How It Works

### Port Range Allocation

1. **Hash username**: Creates MD5 hash of your username
2. **Deterministic mapping**: Maps hash to a base port (10000-60000)
3. **Round to range**: Rounds to nearest 1000-port boundary
4. **Consistent results**: Same username = same range every time

Example:
- User `alice` → hash `6384e2b2184bcbf58eccf10ca7a6563c` → range `24000-24999`
- User `bob` → hash `9f9d51bc70ef21ca5c14f307980a29d8` → range `37000-37999`

### Port Selection

When finding a free port:

1. Generate random port within your 1000-port range
2. Skip if port is in the reserved list (63+ well-known ports)
3. Test if port is available via socket bind
4. Return first available port with metadata

### Reserved Ports

The tool automatically avoids 63+ well-known ports including:

**Databases**: MySQL (3306), PostgreSQL (5432), Redis (6379), MongoDB (27017), SQL Server (1433)

**Web**: HTTP (80, 443), common dev ports (3000, 4200, 5000, 8000, 8080, 8888)

**Message Queues**: RabbitMQ (5672), Kafka (9092), ZooKeeper (2181)

**Search**: Elasticsearch (9200), Kibana (5601), Solr (8983)

**System**: SSH (22), FTP (21), SMTP (25), DNS (53)

**Development**: Node debugger (9229), Java debugger (5005), LiveReload (35729)

**Monitoring**: Prometheus (9090), Grafana Loki (3100), Jaeger (6831)

[Full list in constants.py](src/user_port_finder/constants.py)

## API Reference

### Core Functions

#### `find_free_port()`

Find a free port in your allocated range.

```python
def find_free_port(
    max_attempts: int = 50,
    username: Optional[str] = None,
    min_port: Optional[int] = None,
    max_port: Optional[int] = None,
    ipv6: bool = False,
) -> Optional[PortInfo]:
```

**Returns**: `PortInfo` with port number, user, range, and statistics

#### `get_user_port_range()`

Get your allocated port range.

```python
def get_user_port_range(
    username: Optional[str] = None,
    min_port: int = 10000,
    max_port: int = 60000,
) -> PortRange:
```

**Returns**: `PortRange` with start, end, and username

#### `find_multiple_ports()`

Find multiple free ports.

```python
def find_multiple_ports(
    count: int,
    max_attempts: int = 100,
    username: Optional[str] = None,
    min_port: Optional[int] = None,
    max_port: Optional[int] = None,
    ipv6: bool = False,
) -> List[PortInfo]:
```

**Returns**: List of `PortInfo` objects (may be less than `count` if not enough free ports)

### Data Classes

#### `PortInfo`

```python
@dataclass
class PortInfo:
    port: int                      # The allocated port number
    user: str                      # Username
    range_start: int               # Start of user's range
    range_end: int                 # End of user's range
    attempts: int                  # Number of attempts to find port
    reserved_ports_avoided: int    # Number of reserved ports skipped
```

#### `PortRange`

```python
@dataclass
class PortRange:
    start: int    # Start of range
    end: int      # End of range
    user: str     # Username
```

## Configuration

### Environment Variables

```bash
# Override port range
export UPF_MIN_PORT=20000
export UPF_MAX_PORT=40000
```

### Custom Configuration (Python)

```python
from user_port_finder import find_free_port

# Use custom port range
port_info = find_free_port(min_port=20000, max_port=40000)

# Find port for different user
port_info = find_free_port(username="jenkins")

# Increase attempts for congested systems
port_info = find_free_port(max_attempts=100)
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/SHAILY24/user-port-finder.git
cd user-port-finder

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=user_port_finder --cov-report=html

# Type checking
mypy src/user_port_finder

# Code formatting
black src/ tests/
ruff check src/ tests/
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_core.py

# Specific test
pytest tests/test_core.py::TestFindFreePort::test_find_free_port_returns_port_info

# With verbose output
pytest -v

# With coverage
pytest --cov=user_port_finder --cov-report=term-missing
```

## Use Cases

### Shared Development Servers

Multiple developers SSH into the same server and need to run services:

```bash
# Developer 1 (alice)
user-port-finder --show-range
# Range: 24000-24999

export API_PORT=$(user-port-finder)
python manage.py runserver 0.0.0.0:$API_PORT

# Developer 2 (bob)
user-port-finder --show-range
# Range: 37000-37999 (different!)

export API_PORT=$(user-port-finder)
python manage.py runserver 0.0.0.0:$API_PORT
```

No coordination needed - they automatically get different ranges.

### CI/CD Pipelines

Avoid port conflicts in parallel CI jobs:

```yaml
# .github/workflows/test.yml
- name: Run integration tests
  run: |
    export DB_PORT=$(user-port-finder)
    export API_PORT=$(user-port-finder)
    docker-compose up -d
    pytest tests/integration/
```

### Container Development

Dynamic port allocation for dev containers:

```json
// .devcontainer/devcontainer.json
{
  "postCreateCommand": "user-port-finder --count 3 --format env > .env",
  "forwardPorts": [3000, 5432, 6379]
}
```

### Jupyter Notebooks

Auto-allocate ports for Jupyter in shared environments:

```bash
jupyter notebook --port=$(user-port-finder)
```

## Comparison to Alternatives

| Tool | Approach | Pros | Cons |
|------|----------|------|------|
| **user-port-finder** | Deterministic user ranges | No coordination needed, consistent, fast | Requires username-based allocation |
| `socket.bind(0)` | OS assigns random port | Simple, guaranteed free | Non-deterministic, can't pre-allocate |
| Manual assignment | Hard-code ports | Full control | Conflicts, coordination overhead |
| Port pooling service | Centralized allocation | Flexible | Requires running service, network dependency |

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for your changes
4. Ensure tests pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Author

**Shaily Sharma**
- Email: shailysharmawork@gmail.com
- GitHub: [@SHAILY24](https://github.com/SHAILY24)
- Portfolio: [https://portfolio.shaily.dev](https://portfolio.shaily.dev)

## Related Projects

- [port-for](https://github.com/kmike/port-for) - Find free TCP ports
- [get-port](https://github.com/sindresorhus/get-port) - Get available port (Node.js)
- [portpicker](https://github.com/google/python-portpicker) - Google's port picker

## Changelog

### 0.1.0 (2025-11-19)

- Initial release
- Deterministic user-based port ranges
- CLI with multiple output formats
- Python library API
- IPv4/IPv6 support
- Reserved port avoidance
- Comprehensive test suite
