# -*- coding: utf-8 -*-
from __future__ import annotations

import re

import xbmcgui
import xbmcplugin

from auth import valid_cookie
from client_factory import client
from plugin import HANDLE, add_folder, add_label, add_video, finish, notify
from settings import cache_seconds, cookie, count, stale_fallback
from storage import cache_get, cache_set
from xapi import enrich_missing_videos, extract_user_info, extract_video_items, find_bottom_cursor


def _require_login():
    if valid_cookie(cookie()):
        return True
    notify("请先登录 X", xbmcgui.NOTIFICATION_ERROR)
    home()
    return False


def _cached(namespace, key, loader, force=False):
    ttl = cache_seconds()
    if not force and ttl > 0:
        hit = cache_get(namespace, key, ttl, allow_stale=False)
        if hit is not None:
            return hit
    try:
        value = loader()
        if ttl > 0 and value is not None:
            cache_set(namespace, key, value)
        return value
    except Exception:
        if stale_fallback():
            old = cache_get(namespace, key, ttl, allow_stale=True)
            if old is not None:
                notify("X 接口暂时失败，已显示旧缓存")
                return old
        raise


def _account_info(c, require_id=False):
    info = _cached("account", "me", c.verify)
    if require_id and not str(info.get("id") or ""):
        raise RuntimeError(
            "当前 Cookie 已登录，但缺少 twid，无法确定你的账号 ID。"
            "请在浏览器 x.com 的请求头里复制完整 Cookie 后重新登录。"
        )
    return info


def home():
    xbmcplugin.setPluginCategory(HANDLE, "X（Twitter）")
    if not valid_cookie(cookie()):
        add_folder("先登录 X（粘贴 Cookie）", action="login")
        add_folder("账号 / 登录状态", action="account")
        add_folder("插件诊断", action="diagnostics")
        finish(cache=False)
        return

    add_folder("首页推荐视频（For You）", action="feed", kind="for_you")
    add_folder("关注页视频（Following）", action="feed", kind="following")
    add_folder("我的主页视频（我发布）", action="my_videos")
    add_folder("我喜欢的视频（本地）", action="likes")
    add_folder("我的书签 / 收藏视频", action="bookmarks")
    add_folder("搜索 X 视频", action="search")
    add_folder("打开 X 帖子链接", action="open_url")
    add_folder("观看历史", action="history")
    add_folder("账号与设置", action="account")
    add_folder("插件诊断", action="diagnostics")
    finish(cache=False)


def _render(items, title, next_params=None, refresh_params=None):
    xbmcplugin.setPluginCategory(HANDLE, title)
    if refresh_params:
        add_folder("↻ 刷新本页", **refresh_params)
    if not items:
        add_label("这一页没有找到可播放视频")
    else:
        per_tweet = {}
        for item in items:
            tid = str(item.get("tweet_id") or "")
            if "media_index" not in item:
                item["media_index"] = per_tweet.get(tid, 0)
            per_tweet[tid] = int(item.get("media_index") or 0) + 1
            add_video(item)
    if next_params and next_params.get("cursor"):
        add_folder("下一页 ▶", **next_params)
    finish(cache=False)


def _items(c, raw):
    return enrich_missing_videos(c, raw, max_detail=min(count(), 16), want=count())


def show_feed(kind, cursor="", refresh=False):
    if not _require_login():
        return
    c = client()
    latest = kind == "following"
    key = "%s|%s|%d" % (kind, cursor, count())
    raw = _cached(
        "feed",
        key,
        lambda: c.home_timeline(count=count(), latest=latest, cursor=cursor),
        force=bool(refresh),
    )
    if refresh:
        notify("已刷新关注页" if latest else "已刷新推荐页")
    next_cursor = find_bottom_cursor(raw)
    title = "关注页视频（Following）" if latest else "首页推荐视频（For You）"
    _render(
        _items(c, raw),
        title,
        {"action": "feed", "kind": kind, "cursor": next_cursor},
        {"action": "feed", "kind": kind, "cursor": cursor, "refresh": "1"},
    )


def show_my_videos(cursor=""):
    if not _require_login():
        return
    c = client()
    info = _account_info(c, require_id=True)
    key = "%s|%s|%d" % (info.get("id"), cursor, count())
    raw = _cached("my_videos", key, lambda: c.user_timeline(info.get("id"), count=count(), cursor=cursor))
    next_cursor = find_bottom_cursor(raw)
    _render(
        _items(c, raw),
        "@%s · 我的主页视频" % info.get("handle"),
        {"action": "my_videos", "cursor": next_cursor},
    )


def show_likes(cursor=""):
    # “我喜欢”是插件本地收藏，不调用 X 账号 Likes 接口。
    from favorites import show_favorites
    return show_favorites()


def show_author(handle="", user_id="", tweet_id="", cursor="", refresh=False):
    if not _require_login():
        return
    handle = str(handle or "").strip().lstrip("@")
    user_id = str(user_id or "").strip()
    tweet_id = str(tweet_id or "").strip()
    c = client()

    # Primary path: use X search with from:<handle>.  This is intentionally
    # independent from UserByScreenName/UserTweets because those profile
    # operations rotate more often than SearchTimeline.  We already have the
    # author's handle in feed/following/search list items.
    if handle:
        query = "from:%s" % handle
        key = "%s|%s|%d" % (handle.lower(), cursor, count())
        try:
            raw = _cached(
                "author_search",
                key,
                lambda: c.search_timeline(query, count=count(), cursor=cursor, latest=True),
                force=bool(refresh),
            )
            next_cursor = find_bottom_cursor(raw)
            items = _items(c, raw)
            if refresh:
                notify("已刷新 @%s" % handle)
            _render(
                items,
                "@%s · 作者视频" % handle,
                {"action": "author", "handle": handle, "user_id": user_id, "tweet_id": tweet_id, "cursor": next_cursor},
                {"action": "author", "handle": handle, "user_id": user_id, "tweet_id": tweet_id, "cursor": cursor, "refresh": "1"},
            )
            return
        except Exception as search_exc:
            # Keep a profile-timeline fallback for accounts whose posts are not
            # returned by search.  Do not fail until both paths have been tried.
            search_error = search_exc
    else:
        search_error = None

    # Fallback: resolve numeric id if needed, then use UserTweets.
    resolved_handle = handle
    if not user_id and handle:
        try:
            profile = _cached("author_profile", handle.lower(), lambda: c.user_by_screen_name(handle))
            info = extract_user_info(profile)
            user_id = str(info.get("id") or "")
            resolved_handle = str(info.get("handle") or handle).lstrip("@")
        except Exception:
            pass

    if not user_id:
        if search_error:
            raise RuntimeError("作者主页加载失败：%s" % search_error)
        raise RuntimeError("无法识别该作者")

    key = "%s|%s|%d" % (user_id, cursor, count())
    raw = _cached(
        "author",
        key,
        lambda: c.user_timeline(user_id, count=count(), cursor=cursor),
        force=bool(refresh),
    )
    next_cursor = find_bottom_cursor(raw)
    title_handle = resolved_handle or handle or user_id
    _render(
        _items(c, raw),
        "@%s · 作者视频" % title_handle,
        {"action": "author", "handle": resolved_handle, "user_id": user_id, "tweet_id": tweet_id, "cursor": next_cursor},
        {"action": "author", "handle": resolved_handle, "user_id": user_id, "tweet_id": tweet_id, "cursor": cursor, "refresh": "1"},
    )

def show_bookmarks(cursor=""):
    if not _require_login():
        return
    c = client()
    key = "%s|%d" % (cursor, count())
    raw = _cached("bookmarks", key, lambda: c.bookmarks(count=count(), cursor=cursor))
    next_cursor = find_bottom_cursor(raw)
    _render(_items(c, raw), "我的书签 / 收藏视频", {"action": "bookmarks", "cursor": next_cursor})


def search_videos(query="", cursor=""):
    if not _require_login():
        return
    query = (query or "").strip()
    if not query:
        query = xbmcgui.Dialog().input("搜索 X 视频", type=xbmcgui.INPUT_ALPHANUM).strip()
    if not query:
        return home()
    c = client()
    key = "%s|%s|%d" % (query, cursor, count())
    raw = _cached("search", key, lambda: c.search_timeline(query, count=count(), cursor=cursor, latest=True))
    next_cursor = find_bottom_cursor(raw)
    _render(
        _items(c, raw),
        "搜索：%s" % query,
        {"action": "search", "query": query, "cursor": next_cursor},
    )


def open_x_url(url=""):
    if not _require_login():
        return
    raw_url = (url or "").strip()
    if not raw_url:
        raw_url = xbmcgui.Dialog().input("粘贴 X 帖子链接", type=xbmcgui.INPUT_ALPHANUM).strip()
    if not raw_url:
        return home()
    match = re.search(r"(?:x|twitter)\.com/[^/]+/status(?:es)?/(\d+)", raw_url, re.I)
    if not match:
        match = re.search(r"/status(?:es)?/(\d+)", raw_url, re.I)
    if not match:
        xbmcgui.Dialog().ok("X（Twitter）", "没有识别到帖子 ID。\n请粘贴类似：https://x.com/用户名/status/123...")
        return home()
    tid = match.group(1)
    c = client()
    data = _cached("tweet", tid, lambda: c.tweet_detail(tid))
    items = extract_video_items(data)
    _render(items, "X 帖子 · %s" % tid)
