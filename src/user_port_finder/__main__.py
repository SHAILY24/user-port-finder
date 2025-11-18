"""
CLI interface for user-port-finder.
"""

import sys
import argparse
from typing import Optional

from . import __version__
from .core import (
    get_user_port_range,
    find_free_port,
    find_multiple_ports,
    validate_port_in_range,
    list_ports_in_range,
)
from .formatters import (
    format_port_info_text,
    format_port_range_text,
    port_info_to_dict,
    port_range_to_dict,
    format_json,
    format_yaml,
    format_toml,
    format_env,
    format_multiple_ports_env,
)
from .constants import OUTPUT_FORMATS


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="user-port-finder",
        description="Find available ports in your user-specific range",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find a single free port
  user-port-finder

  # Find 3 free ports
  user-port-finder --count 3

  # Get your port range
  user-port-finder --show-range

  # Check if port is in your range
  user-port-finder --check 15234

  # List all free ports in your range
  user-port-finder --list-free

  # Output as JSON
  user-port-finder --format json

  # Output as environment variable
  user-port-finder --format env --env-var MY_PORT
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    # Core operations
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        default=1,
        metavar="N",
        help="Number of free ports to find (default: 1)",
    )

    parser.add_argument(
        "--show-range",
        "-r",
        action="store_true",
        help="Show your allocated port range",
    )

    parser.add_argument(
        "--check",
        type=int,
        metavar="PORT",
        help="Check if a specific port is in your range",
    )

    parser.add_argument(
        "--list-free",
        action="store_true",
        help="List all free ports in your range",
    )

    parser.add_argument(
        "--list-used",
        action="store_true",
        help="List all used ports in your range",
    )

    # Configuration
    parser.add_argument(
        "--username",
        "-u",
        metavar="USER",
        help="Username to get range for (default: current user)",
    )

    parser.add_argument(
        "--min-port",
        type=int,
        metavar="PORT",
        help="Override minimum port number",
    )

    parser.add_argument(
        "--max-port",
        type=int,
        metavar="PORT",
        help="Override maximum port number",
    )

    parser.add_argument(
        "--max-attempts",
        type=int,
        default=50,
        metavar="N",
        help="Maximum attempts to find a port (default: 50)",
    )

    parser.add_argument(
        "--ipv6",
        action="store_true",
        help="Find IPv6-compatible ports",
    )

    # Output options
    parser.add_argument(
        "--format",
        "-f",
        choices=list(OUTPUT_FORMATS),
        default="text",
        help="Output format (default: text)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output (show all port info)",
    )

    parser.add_argument(
        "--env-var",
        metavar="NAME",
        default="PORT",
        help="Environment variable name for --format env (default: PORT)",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Only output the port number(s), nothing else",
    )

    return parser


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        # Show port range
        if args.show_range:
            kwargs = {"username": args.username}
            if args.min_port is not None:
                kwargs["min_port"] = args.min_port
            if args.max_port is not None:
                kwargs["max_port"] = args.max_port

            port_range = get_user_port_range(**kwargs)

            if args.format == "json":
                print(format_json(port_range_to_dict(port_range)))
            elif args.format == "yaml":
                print(format_yaml(port_range_to_dict(port_range)))
            elif args.format == "toml":
                print(format_toml(port_range_to_dict(port_range)))
            else:
                print(format_port_range_text(port_range))
            return 0

        # Check if port is in range
        if args.check is not None:
            kwargs = {"port": args.check, "username": args.username}
            if args.min_port is not None:
                kwargs["min_port"] = args.min_port
            if args.max_port is not None:
                kwargs["max_port"] = args.max_port

            in_range = validate_port_in_range(**kwargs)

            if args.format == "json":
                print(format_json({"port": args.check, "in_range": in_range}))
            elif args.quiet:
                return 0 if in_range else 1
            else:
                range_kwargs = {"username": args.username}
                if args.min_port is not None:
                    range_kwargs["min_port"] = args.min_port
                if args.max_port is not None:
                    range_kwargs["max_port"] = args.max_port
                port_range = get_user_port_range(**range_kwargs)
                status = "YES" if in_range else "NO"
                print(f"Port {args.check} in range {port_range.start}-{port_range.end}: {status}")
            return 0 if in_range else 1

        # List free ports
        if args.list_free:
            ports = list_ports_in_range(
                username=args.username,
                only_free=True,
                ipv6=args.ipv6,
            )

            if args.format == "json":
                print(format_json({"free_ports": ports, "count": len(ports)}))
            elif args.quiet:
                for port in ports:
                    print(port)
            else:
                print(f"Free ports ({len(ports)}):")
                for port in ports:
                    print(f"  {port}")
            return 0

        # List used ports
        if args.list_used:
            ports = list_ports_in_range(
                username=args.username,
                only_used=True,
                ipv6=args.ipv6,
            )

            if args.format == "json":
                print(format_json({"used_ports": ports, "count": len(ports)}))
            elif args.quiet:
                for port in ports:
                    print(port)
            else:
                print(f"Used ports ({len(ports)}):")
                for port in ports:
                    print(f"  {port}")
            return 0

        # Find free port(s)
        if args.count == 1:
            kwargs = {
                "max_attempts": args.max_attempts,
                "username": args.username,
                "ipv6": args.ipv6,
            }
            if args.min_port is not None:
                kwargs["min_port"] = args.min_port
            if args.max_port is not None:
                kwargs["max_port"] = args.max_port

            port_info = find_free_port(**kwargs)

            if port_info is None:
                if not args.quiet:
                    print("Error: Could not find a free port", file=sys.stderr)
                return 1

            # Format output
            if args.format == "json":
                print(format_json(port_info_to_dict(port_info)))
            elif args.format == "yaml":
                print(format_yaml(port_info_to_dict(port_info)))
            elif args.format == "toml":
                print(format_toml(port_info_to_dict(port_info)))
            elif args.format == "env":
                print(format_env(port_info, args.env_var))
            else:
                print(format_port_info_text(port_info, verbose=args.verbose))

        else:  # Multiple ports
            kwargs = {
                "count": args.count,
                "max_attempts": args.max_attempts,
                "username": args.username,
                "ipv6": args.ipv6,
            }
            if args.min_port is not None:
                kwargs["min_port"] = args.min_port
            if args.max_port is not None:
                kwargs["max_port"] = args.max_port

            ports = find_multiple_ports(**kwargs)

            if not ports:
                if not args.quiet:
                    print("Error: Could not find any free ports", file=sys.stderr)
                return 1

            if len(ports) < args.count and not args.quiet:
                print(
                    f"Warning: Only found {len(ports)} of {args.count} requested ports",
                    file=sys.stderr,
                )

            # Format output
            if args.format == "json":
                print(format_json([port_info_to_dict(p) for p in ports]))
            elif args.format == "yaml":
                print(format_yaml([port_info_to_dict(p) for p in ports]))
            elif args.format == "toml":
                print(format_toml({"ports": [port_info_to_dict(p) for p in ports]}))
            elif args.format == "env":
                print(format_multiple_ports_env(ports, args.env_var))
            else:
                for port_info in ports:
                    print(format_port_info_text(port_info, verbose=args.verbose))

        return 0

    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            raise
        return 1


if __name__ == "__main__":
    sys.exit(main())
