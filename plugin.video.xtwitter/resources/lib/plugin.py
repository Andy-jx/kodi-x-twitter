# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
from urllib.parse import parse_qsl, urlencode

import xbmcgui
import xbmcplugin

from kodi_compat import set_video_info
from storage import favorite_has

HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]


def get_params():
    raw = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2].startswith("?") else ""
    return dict(parse_qsl(raw, keep_blank_values=True))


def plugin_url(**params):
    clean = {k: v for k, v in params.items() if v is not None}
    return BASE_URL + "?" + urlencode(clean)


def finish(succeeded=True, cache=False):
    xbmcplugin.endOfDirectory(HANDLE, succeeded=succeeded, cacheToDisc=cache)


def notify(message, level=xbmcgui.NOTIFICATION_INFO):
    xbmcgui.Dialog().notification("X（Twitter）", message, level, 4500)


def add_folder(label, **params):
    li = xbmcgui.ListItem(label=label)
    li.setArt({"icon": "DefaultFolder.png"})
    xbmcplugin.addDirectoryItem(HANDLE, plugin_url(**params), li, True)


def add_label(label, plot=""):
    li = xbmcgui.ListItem(label=label)
    if plot:
        set_video_info(li, {"title": label, "plot": plot})
    xbmcplugin.addDirectoryItem(HANDLE, "", li, False)


def add_video(item):
    item = item or {}
    label = item.get("label") or "X 视频"
    li = xbmcgui.ListItem(label=label)
    thumb = item.get("thumb") or ""
    if thumb:
        li.setArt({"thumb": thumb, "icon": thumb, "poster": thumb})
    li.setProperty("IsPlayable", "true")
    set_video_info(li, {
        "title": label,
        "plot": item.get("plot") or "",
        "studio": item.get("author") or "X",
        "duration": item.get("duration") or 0,
    })
    tweet_id = item.get("tweet_id") or ""
    media_index = int(item.get("media_index") or 0)
    url = plugin_url(
        action="play",
        tweet_id=tweet_id,
        media_index=media_index,
        url=item.get("url") or "",
        title=label,
        plot=item.get("plot") or "",
        author=item.get("author") or "X",
        thumb=thumb,
    )

    menu = []
    if tweet_id:
        if favorite_has(tweet_id, media_index):
            fav_url = plugin_url(action="favorite_remove", tweet_id=tweet_id, media_index=media_index)
            menu.append(("移出我喜欢", "RunPlugin(%s)" % fav_url))
        else:
            fav_url = plugin_url(action="favorite_add", tweet_id=tweet_id, media_index=media_index)
            menu.append(("加入我喜欢", "RunPlugin(%s)" % fav_url))

    handle = str(item.get("author_handle") or "").strip().lstrip("@")
    author_id = str(item.get("author_id") or "").strip()
    if handle or author_id:
        author_url = plugin_url(action="author", handle=handle, user_id=author_id, tweet_id=tweet_id)
        author_label = "进入作者主页 @%s" % handle if handle else "进入作者主页"
        menu.append((author_label, "Container.Update(%s,replace)" % author_url))

    if menu:
        try:
            li.addContextMenuItems(menu)
        except Exception:
            pass

    xbmcplugin.addDirectoryItem(HANDLE, url, li, False)
