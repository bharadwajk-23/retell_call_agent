#!/usr/bin/env python3
"""Minimal static file server for the built frontend (frontend/dist).

Used for bare-metal deployments where Docker/nginx aren't in play (see
start_frontend.sh). Falls back to index.html for any path that isn't a real
file on disk, so the SPA still loads correctly on a hard refresh — the same
behavior as the `try_files ... /index.html` rule in nginx.conf.

Stdlib only — no pip dependencies required to run this.
"""
import http.server
import os
import socketserver
import sys

DIST_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

# Port is given directly as the first CLI arg (see start_frontend.sh); falls
# back to FRONTEND_PORT/8005 if run standalone without one.
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("FRONTEND_PORT", "8005"))


class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIST_DIR, **kwargs)

    def send_head(self):
        requested = self.translate_path(self.path)
        if not os.path.isfile(requested):
            self.path = "/index.html"
        return super().send_head()

    def log_message(self, format, *args):  # noqa: A002 - matches base signature
        print(f"[frontend] {self.address_string()} - {format % args}")


def main():
    if not os.path.isdir(DIST_DIR):
        raise SystemExit(f"'{DIST_DIR}' not found. Run ./initialize.sh to build the frontend first.")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), SPARequestHandler) as httpd:
        print(f"Serving {DIST_DIR} on http://0.0.0.0:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
