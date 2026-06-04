"""Local dev server — wraps the Vercel handler for `next dev` proxying."""
from http.server import HTTPServer
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from estimate import handler

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    httpd = HTTPServer(("127.0.0.1", port), handler)
    print(f"Python API running on http://127.0.0.1:{port}", flush=True)
    httpd.serve_forever()
