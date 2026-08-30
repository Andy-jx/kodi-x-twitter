# -*- coding: utf-8 -*-
from __future__ import annotations

from client_factory import client
from settings import refresh_before_play
from xapi import extract_video_items


def resolve(tweet_id, media_index=0, fallback_url=""):
    tid = str(tweet_id or "")
    index = max(0, int(media_index or 0))
    if not tid or not refresh_before_play():
        return fallback_url
    try:
        data = client().tweet_detail(tid)
        items = extract_video_items(data)
        if items:
            if index < len(items):
                return items[index].get("url") or fallback_url
            return items[0].get("url") or fallback_url
    except Exception:
        pass
    return fallback_url
