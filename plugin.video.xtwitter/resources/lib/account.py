# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmcaddon
import xbmcgui

from auth import cookie_to_header, valid_cookie
from client_factory import client
from plugin import add_folder, finish, notify
from storage import clear_cache
from xapi import XClient, XAPIError

ADDON = xbmcaddon.Addon()


def login():
    current = ADDON.getSettingString("cookie") or ""
    dlg = xbmcgui.Dialog()
    raw = dlg.input(
        "粘贴 x.com Cookie（必须包含 auth_token 与 ct0）",
        defaultt=current,
        type=xbmcgui.INPUT_ALPHANUM,
    )
    if not raw:
        return
    cookie = cookie_to_header(raw)
    if not valid_cookie(cookie):
        dlg.ok("X 登录", "Cookie 无效：至少需要 auth_token 和 ct0。")
        return
    try:
        info = XClient(cookie).verify()
    except Exception as exc:
        dlg.ok("X 登录失败", str(exc))
        return
    ADDON.setSettingString("cookie", cookie)
    clear_cache()
    handle = info.get("handle") or ""
    if handle:
        notify("已登录 @%s" % handle)
        dlg.ok("X 登录成功", "账号：%s\n@%s" % (info.get("name") or "", handle))
    else:
        notify("X Cookie 登录已验证")
        dlg.ok(
            "X 登录成功",
            "Cookie 会话可用。\n\n推荐、关注、书签、搜索可以直接使用。"
            "\n如果‘我的主页/我喜欢’提示缺少账号 ID，请重新粘贴完整 x.com Cookie（包含 twid）。",
        )


def show_account():
    cookie = ADDON.getSettingString("cookie") or ""
    if not valid_cookie(cookie):
        add_folder("登录 X（粘贴 Cookie）", action="login")
        add_folder("打开插件设置", action="settings")
        add_folder("插件诊断", action="diagnostics")
        finish(cache=False)
        return
    try:
        info = client().verify()
        handle = info.get("handle") or ""
        label = ("已登录：@%s" % handle) if handle else "已登录：Cookie 会话可用"
        add_folder(label, action="home")
        add_folder("我的主页视频", action="my_videos")
        add_folder("我喜欢的视频", action="likes")
        add_folder("我的书签 / 收藏", action="bookmarks")
        add_folder("观看历史", action="history")
        add_folder("插件诊断", action="diagnostics")
        add_folder("打开插件设置", action="settings")
        add_folder("重新粘贴 Cookie", action="login")
        add_folder("退出登录", action="logout")
    except XAPIError as exc:
        add_folder("登录已失效：重新粘贴 Cookie", action="login")
        add_folder("插件诊断", action="diagnostics")
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
    finish(cache=False)


def logout():
    ADDON.setSettingString("cookie", "")
    clear_cache()
    notify("已退出 X 登录，账号缓存已清理")
