#!/usr/bin/env python3
"""
Example: Using user-port-finder with Flask.

Run this script to start a Flask app on an automatically allocated port.
"""

try:
    from flask import Flask, jsonify
except ImportError:
    print("This example requires Flask. Install it with: pip install flask")
    exit(1)

from user_port_finder import find_free_port, get_user_port_range


app = Flask(__name__)


@app.route("/")
def index():
    """Home route."""
    return jsonify({
        "message": "Hello from Flask!",
        "app": "user-port-finder example",
    })


@app.route("/port-info")
def port_info():
    """Show port allocation info."""
    port_range = get_user_port_range()
    return jsonify({
        "user": port_range.user,
        "port_range": {
            "start": port_range.start,
            "end": port_range.end,
            "total": port_range.end - port_range.start + 1,
        },
        "current_port": app.config.get("PORT", "unknown"),
    })


if __name__ == "__main__":
    # Find a free port
    port_info = find_free_port()

    if port_info is None:
        print("Error: Could not find a free port")
        exit(1)

    print(f"Starting Flask app on port {port_info.port}")
    print(f"User: {port_info.user}")
    print(f"Port range: {port_info.range_start}-{port_info.range_end}")
    print()
    print(f"Visit: http://localhost:{port_info.port}")
    print(f"Port info: http://localhost:{port_info.port}/port-info")
    print()

    app.config["PORT"] = port_info.port
    app.run(host="0.0.0.0", port=port_info.port, debug=True)
