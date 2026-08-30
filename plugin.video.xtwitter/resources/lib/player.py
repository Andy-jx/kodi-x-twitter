# -*- coding: utf-8 -*-
from __future__ import annotations

from urllib.parse import quote

import xbmcgui
import xbmcplugin

from kodi_compat import set_video_info
from plugin import HANDLE, notify
from resolver import resolve
from settings import history_enabled, history_limit
from storage import history_add
from xapi import WEB_UA


def _with_public_headers(url):
    if not url:
        return url
    headers = "User-Agent=%s&Referer=%s" % (
        quote(WEB_UA, safe=""),
        quote("https://x.com/", safe=""),
    )
    return url + "|" + headers


def play(params):
    fallback = params.get("url") or ""
    tid = params.get("tweet_id") or ""
    try:
        media_index = int(params.get("media_index") or 0)
    except Exception:
        media_index = 0

    url = resolve(tid, media_index=media_index, fallback_url=fallback)
    if not url:
        notify("视频地址解析失败", xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        return

    title = params.get("title") or "X 视频"
    plot = params.get("plot") or ""
    author = params.get("author") or "X"
    thumb = params.get("thumb") or ""

    if history_enabled() and tid:
        history_add({
            "tweet_id": tid,
            "media_index": media_index,
            "label": title,
            "plot": plot,
            "author": author,
            "thumb": thumb,
            "url": url,
        }, limit=history_limit())

    li = xbmcgui.ListItem(path=_with_public_headers(url))
    if thumb:
        li.setArt({"thumb": thumb, "icon": thumb, "poster": thumb})
    try:
        li.setMimeType("video/mp4")
    except Exception:
        pass
    set_video_info(li, {"title": title, "plot": plot, "studio": author})
    xbmcplugin.setResolvedUrl(HANDLE, True, li)
