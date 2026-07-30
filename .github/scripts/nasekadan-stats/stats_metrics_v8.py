#!/usr/bin/env python3
from __future__ import annotations

from urllib.parse import urlsplit
from typing import Any


def install(base: Any) -> None:
    """Serve the patched dashboard through the real authenticated HTTP handler.

    The legacy handler kept returning its original cached dashboard even after
    render_dashboard had been replaced. This wrapper intercepts authenticated
    GET requests for the dashboard root and writes the current patched body
    directly to the socket.
    """
    if getattr(base, "_authenticated_dashboard_v8_installed", False):
        return

    original = base.Handler.handle_request

    def handle_request_with_current_dashboard(self: Any, allow_body: bool) -> None:
        path = urlsplit(self.path).path or "/"
        is_get = getattr(self, "command", "GET").upper() == "GET"
        dashboard_path = path in {"/", "/statistiky", "/statistiky/"}

        if is_get and dashboard_path and self.session():
            body = base.render_dashboard()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
            self.end_headers()
            if allow_body:
                self.wfile.write(body)
            return

        return original(self, allow_body)

    base.Handler.handle_request = handle_request_with_current_dashboard
    base._authenticated_dashboard_v8_installed = True
