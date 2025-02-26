"""
Script to build documentation for the ZeptoMail Python API.
"""

import os
import subprocess
import sys

def build_docs(serve=False, port=None):
    """Build the documentation.
    
    Args:
        serve: Whether to serve the documentation
        port: Custom port to use for serving (default: 8000)
    """
    try:
        if serve:
            print("Building and serving documentation...")
            cmd = ["mkdocs", "serve"]
            if port:
                cmd.extend(["--dev-addr", f"127.0.0.1:{port}"])
            subprocess.run(cmd, check=True)
        else:
            print("Building documentation...")
            subprocess.run(["mkdocs", "build"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error building documentation: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    
    return True


def main():
    """Main function."""
    # Check if the docs directory exists, create it if not
    if not os.path.exists("docs"):
        print("Creating docs directory...")
        os.makedirs("docs", exist_ok=True)
        os.makedirs("docs/api", exist_ok=True)
        os.makedirs("docs/examples", exist_ok=True)

    
    # Parse arguments
    serve = "--serve" in sys.argv
    
    # Check for port argument
    port = None
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                port = int(sys.argv[i + 1])
                print(f"Using custom port: {port}")
            except ValueError:
                print(f"Invalid port number: {sys.argv[i + 1]}")
                return 1
    
    # Build docs
    if build_docs(serve, port):
        if not serve:
            print("Documentation built successfully!")
        return 0
    else:
        print("Failed to build documentation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
