#!/usr/bin/env python3
from __future__ import annotations

import audit_canonical_content_runtime as audit

_RealRequest = audit.Request


def _safe_request(url, headers=None, *args, **kwargs):
    safe_headers = dict(headers or {})
    safe_headers["User-Agent"] = "Nase Kadan canonical audit/1.1"
    return _RealRequest(url, headers=safe_headers, *args, **kwargs)


audit.Request = _safe_request

if __name__ == "__main__":
    raise SystemExit(audit.main())
