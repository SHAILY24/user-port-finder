"""
Constants and configurations for user-port-finder.
"""

from typing import Set

# Well-known ports to skip (common applications)
RESERVED_PORTS: Set[int] = {
    # Databases
    3306,   # MySQL
    5432,   # PostgreSQL
    6379,   # Redis
    27017,  # MongoDB
    1433,   # SQL Server
    5984,   # CouchDB
    7000,   # Cassandra
    9042,   # Cassandra CQL

    # Web Services
    80, 443,        # HTTP/HTTPS
    8080, 8443,     # Alt HTTP/HTTPS
    3000,           # React, Node.js
    4200,           # Angular
    5000,           # Flask
    8000,           # Django
    8081,           # Common dev port
    8888,           # Jupyter
    3001,           # Next.js (dev)
    5173,           # Vite

    # Message Queues
    5672,   # RabbitMQ
    15672,  # RabbitMQ Management
    9092,   # Kafka
    2181,   # ZooKeeper
    4369,   # Erlang Port Mapper (RabbitMQ)

    # Search & Analytics
    9200,   # Elasticsearch
    5601,   # Kibana
    8983,   # Solr

    # System Services
    22,     # SSH
    21,     # FTP
    25,     # SMTP
    53,     # DNS
    123,    # NTP
    389,    # LDAP
    636,    # LDAPS

    # Development Tools
    9229,   # Node.js debugger
    5005,   # Java debugger
    3001,   # Webpack dev server
    35729,  # LiveReload

    # Monitoring & Observability
    9090,   # Prometheus
    3100,   # Grafana Loki
    4317,   # OpenTelemetry
    6831,   # Jaeger
}

# Default port range configuration
# Start at 10000 to avoid privileged ports (<1024) and common well-known ports
PRIVILEGED_PORT_THRESHOLD = 1024
DEFAULT_MIN_PORT = 10000
DEFAULT_MAX_PORT = 60000
USER_RANGE_SIZE = 1000

# Supported output formats
OUTPUT_FORMATS = {"text", "json", "yaml", "toml", "env"}

# IPv4 and IPv6 localhost addresses
LOCALHOST_IPV4 = "127.0.0.1"
LOCALHOST_IPV6 = "::1"
