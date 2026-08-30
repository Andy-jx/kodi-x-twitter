# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmcaddon

ADDON = xbmcaddon.Addon()

QID_SETTINGS = {
    "HomeTimeline": "qid_home",
    "HomeLatestTimeline": "qid_latest",
    "UserTweets": "qid_user",
    "Likes": "qid_likes",
    "Bookmarks": "qid_bookmarks",
    "SearchTimeline": "qid_search",
    "TweetResultByRestId": "qid_tweet",
}


def cookie():
    return ADDON.getSettingString("cookie") or ""


def count():
    try:
        return max(10, min(50, int(ADDON.getSettingInt("count"))))
    except Exception:
        return 20


def auto_qid():
    try:
        return ADDON.getSettingBool("auto_qid")
    except Exception:
        return True


def qid_overrides():
    out = {}
    for op, sid in QID_SETTINGS.items():
        try:
            value = ADDON.getSettingString(sid).strip()
        except Exception:
            value = ""
        if value:
            out[op] = value
    return out


def refresh_before_play():
    try:
        return ADDON.getSettingBool("refresh_before_play")
    except Exception:
        return True


def cache_seconds():
    try:
        return max(0, min(1800, int(ADDON.getSettingInt("cache_seconds"))))
    except Exception:
        return 120


def stale_fallback():
    try:
        return ADDON.getSettingBool("stale_fallback")
    except Exception:
        return True


def history_enabled():
    try:
        return ADDON.getSettingBool("history_enabled")
    except Exception:
        return True


def history_limit():
    try:
        return max(20, min(500, int(ADDON.getSettingInt("history_limit"))))
    except Exception:
        return 100
