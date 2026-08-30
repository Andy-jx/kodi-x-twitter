# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from urllib.parse import unquote


def cookie_to_header(raw):
    raw = (raw or "").strip()
    if not raw:
        return ""

    # Cookie-Editor JSON export
    if raw.startswith("["):
        try:
            arr = json.loads(raw)
            parts = []
            for row in arr:
                if isinstance(row, dict) and row.get("name") and row.get("value") is not None:
                    parts.append("%s=%s" % (row["name"], row["value"]))
            return "; ".join(parts)
        except Exception:
            pass

    # Accept accidental "Cookie:" prefix.
    raw = re.sub(r"^cookie\s*:\s*", "", raw, flags=re.I)
    return raw.replace("\r", "").replace("\n", "; ").strip(" ;")


def cookie_dict(raw):
    header = cookie_to_header(raw)
    out = {}
    for part in header.split(";"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        if k:
            out[k] = v.strip()
    return out


def auth_parts(raw):
    c = cookie_dict(raw)
    return c.get("auth_token", ""), c.get("ct0", "")


def user_id_from_cookie(raw):
    """Return the logged-in numeric user id from X's twid cookie when present.

    Typical values look like ``u%3D123456789`` or ``u=123456789``.  twid is
    not required for the basic authenticated timelines, but it lets us load
    the current user's profile/likes without relying on X's retired v1.1
    verify_credentials endpoint.
    """
    value = cookie_dict(raw).get("twid", "")
    if not value:
        return ""
    value = unquote(str(value)).strip()
    m = re.search(r"(?:^|=)(\d{3,})$", value)
    return m.group(1) if m else ""


def valid_cookie(raw):
    a, c = auth_parts(raw)
    return bool(a and c)
