# -*- coding: utf-8 -*-
from __future__ import annotations

from plugin import get_params


def run():
    p = get_params()
    action = p.get("action") or "home"
    cursor = p.get("cursor") or ""

    if action == "home":
        from browse import home
        return home()
    if action == "feed":
        from browse import show_feed
        refresh = str(p.get("refresh") or "").lower() in ("1", "true", "yes")
        return show_feed(p.get("kind") or "for_you", cursor=cursor, refresh=refresh)
    if action == "my_videos":
        from browse import show_my_videos
        return show_my_videos(cursor=cursor)
    if action == "likes":
        from browse import show_likes
        return show_likes(cursor=cursor)
    if action == "author":
        from browse import show_author
        refresh = str(p.get("refresh") or "").lower() in ("1", "true", "yes")
        return show_author(
            p.get("handle") or "",
            p.get("user_id") or "",
            p.get("tweet_id") or "",
            cursor=cursor,
            refresh=refresh,
        )
    if action == "favorite_add":
        from favorites import add_favorite_action
        return add_favorite_action(p.get("tweet_id") or "", p.get("media_index") or 0)
    if action == "favorite_remove":
        from favorites import remove_favorite_action
        return remove_favorite_action(p.get("tweet_id") or "", p.get("media_index") or 0)
    if action == "bookmarks":
        from browse import show_bookmarks
        return show_bookmarks(cursor=cursor)
    if action == "search":
        from browse import search_videos
        return search_videos(query=p.get("query") or "", cursor=cursor)
    if action == "open_url":
        from browse import open_x_url
        return open_x_url(p.get("url") or "")
    if action == "history":
        from history import show_history
        return show_history()
    if action == "clear_history":
        from history import clear_history_action
        return clear_history_action()
    if action == "diagnostics":
        from diagnostics import show_diagnostics
        return show_diagnostics()
    if action == "clear_cache":
        from diagnostics import clear_cache_action
        return clear_cache_action()
    if action == "settings":
        import xbmcaddon
        xbmcaddon.Addon().openSettings()
        return None
    if action == "login":
        from account import login
        return login()
    if action == "account":
        from account import show_account
        return show_account()
    if action == "logout":
        from account import logout
        return logout()
    if action == "play":
        from player import play
        return play(p)

    from browse import home
    return home()
