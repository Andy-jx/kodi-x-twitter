# -*- coding: utf-8 -*-
from __future__ import annotations

import hashlib
import json
import os
import time

import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))
CACHE_DIR = os.path.join(PROFILE, "cache")
HISTORY_FILE = os.path.join(PROFILE, "history.json")
FAVORITES_FILE = os.path.join(PROFILE, "favorites.json")


def _ensure(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def _atomic_write(path, data):
    _ensure(os.path.dirname(path))
    temp = path + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(temp, path)


def _read(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def cache_key(namespace, key):
    raw = ("%s|%s" % (namespace, key)).encode("utf-8", "replace")
    return hashlib.sha256(raw).hexdigest()


def cache_get(namespace, key, ttl, allow_stale=False):
    path = os.path.join(CACHE_DIR, cache_key(namespace, key) + ".json")
    data = _read(path, None)
    if not isinstance(data, dict) or "value" not in data:
        return None
    age = max(0, time.time() - float(data.get("ts") or 0))
    if allow_stale or ttl <= 0 or age <= ttl:
        return data.get("value")
    return None


def cache_set(namespace, key, value):
    path = os.path.join(CACHE_DIR, cache_key(namespace, key) + ".json")
    _atomic_write(path, {"ts": time.time(), "value": value})


def clear_cache():
    if not os.path.isdir(CACHE_DIR):
        return 0
    count = 0
    for name in os.listdir(CACHE_DIR):
        path = os.path.join(CACHE_DIR, name)
        try:
            if os.path.isfile(path):
                os.remove(path)
                count += 1
        except Exception:
            pass
    return count


def history_load():
    data = _read(HISTORY_FILE, [])
    return data if isinstance(data, list) else []


def history_add(item, limit=100):
    if not isinstance(item, dict):
        return
    tid = str(item.get("tweet_id") or "")
    if not tid:
        return
    entry = {
        "tweet_id": tid,
        "media_index": int(item.get("media_index") or 0),
        "label": item.get("label") or "X 视频",
        "plot": item.get("plot") or "",
        "author": item.get("author") or "X",
        "thumb": item.get("thumb") or "",
        "url": item.get("url") or "",
        "played_at": int(time.time()),
    }
    rows = [x for x in history_load() if str(x.get("tweet_id") or "") != tid or int(x.get("media_index") or 0) != entry["media_index"]]
    rows.insert(0, entry)
    _atomic_write(HISTORY_FILE, rows[:max(1, int(limit))])


def history_clear():
    try:
        if os.path.isfile(HISTORY_FILE):
            os.remove(HISTORY_FILE)
    except Exception:
        pass



def favorites_load():
    data = _read(FAVORITES_FILE, [])
    return data if isinstance(data, list) else []


def _favorite_key(tweet_id, media_index=0):
    return "%s:%d" % (str(tweet_id or ""), int(media_index or 0))


def favorite_has(tweet_id, media_index=0):
    key = _favorite_key(tweet_id, media_index)
    return any(_favorite_key(x.get("tweet_id"), x.get("media_index")) == key for x in favorites_load() if isinstance(x, dict))


def favorite_add(item, limit=1000):
    if not isinstance(item, dict):
        return False
    tid = str(item.get("tweet_id") or "")
    if not tid:
        return False
    entry = {
        "tweet_id": tid,
        "media_index": int(item.get("media_index") or 0),
        "label": item.get("label") or "X 视频",
        "plot": item.get("plot") or "",
        "author": item.get("author") or "X",
        "author_handle": item.get("author_handle") or "",
        "author_id": str(item.get("author_id") or ""),
        "thumb": item.get("thumb") or "",
        "url": item.get("url") or "",
        "saved_at": int(time.time()),
    }
    key = _favorite_key(entry["tweet_id"], entry["media_index"])
    rows = [x for x in favorites_load() if isinstance(x, dict) and _favorite_key(x.get("tweet_id"), x.get("media_index")) != key]
    rows.insert(0, entry)
    _atomic_write(FAVORITES_FILE, rows[:max(1, int(limit))])
    return True


def favorite_remove(tweet_id, media_index=0):
    key = _favorite_key(tweet_id, media_index)
    old = favorites_load()
    rows = [x for x in old if not (isinstance(x, dict) and _favorite_key(x.get("tweet_id"), x.get("media_index")) == key)]
    if len(rows) == len(old):
        return False
    _atomic_write(FAVORITES_FILE, rows)
    return True


def favorites_clear():
    try:
        if os.path.isfile(FAVORITES_FILE):
            os.remove(FAVORITES_FILE)
    except Exception:
        pass
