# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmc
import xbmcgui
import xbmcplugin

from auth import valid_cookie
from client_factory import client
from plugin import HANDLE, add_label, add_video, finish, notify
from settings import cookie
from storage import favorite_add as store_add, favorite_remove as store_remove, favorites_load
from xapi import extract_video_items


def _index_items(items):
    per_tweet = {}
    out = []
    for item in items or []:
        row = dict(item)
        tid = str(row.get("tweet_id") or "")
        if "media_index" not in row:
            row["media_index"] = per_tweet.get(tid, 0)
        per_tweet[tid] = int(row.get("media_index") or 0) + 1
        out.append(row)
    return out


def show_favorites():
    xbmcplugin.setPluginCategory(HANDLE, "我喜欢的视频")
    rows = favorites_load()
    if not rows:
        add_label("还没有收藏视频", "在推荐/关注/作者主页里长按视频，选择“加入我喜欢”。")
    else:
        for item in rows:
            add_video(item)
    finish(cache=False)


def add_favorite_action(tweet_id, media_index=0):
    tid = str(tweet_id or "")
    try:
        idx = max(0, int(media_index or 0))
    except Exception:
        idx = 0
    if not tid:
        notify("缺少帖子 ID", xbmcgui.NOTIFICATION_ERROR)
        return
    if not valid_cookie(cookie()):
        notify("请先登录 X", xbmcgui.NOTIFICATION_ERROR)
        return
    try:
        raw = client().tweet_detail(tid)
        items = _index_items(extract_video_items(raw))
        if not items:
            raise RuntimeError("没有找到可收藏的视频")
        item = items[idx] if idx < len(items) else items[0]
        store_add(item)
        notify("已加入我喜欢")
        xbmc.executebuiltin("Container.Refresh")
    except Exception as exc:
        notify("收藏失败：%s" % exc, xbmcgui.NOTIFICATION_ERROR)


def remove_favorite_action(tweet_id, media_index=0):
    try:
        idx = max(0, int(media_index or 0))
    except Exception:
        idx = 0
    if store_remove(tweet_id, idx):
        notify("已移出我喜欢")
        xbmc.executebuiltin("Container.Refresh")
    else:
        notify("这条视频不在我喜欢中")
