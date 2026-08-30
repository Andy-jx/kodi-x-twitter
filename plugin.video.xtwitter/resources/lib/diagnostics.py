# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmc
import xbmcaddon
import xbmcplugin

from auth import valid_cookie
from client_factory import client
from plugin import HANDLE, add_folder, add_label, finish
from settings import auto_qid, cookie
from storage import clear_cache

ADDON = xbmcaddon.Addon()


def _ok(label, value):
    add_label("✓ %s：%s" % (label, value))


def _bad(label, value):
    add_label("✗ %s：%s" % (label, value))


def show_diagnostics():
    xbmcplugin.setPluginCategory(HANDLE, "插件诊断")
    _ok("插件版本", ADDON.getAddonInfo("version"))
    _ok("Kodi", xbmc.getInfoLabel("System.BuildVersion") or "未知")
    _ok("自动 Query ID", "开启" if auto_qid() else "关闭")
    if valid_cookie(cookie()):
        _ok("Cookie", "已包含 auth_token + ct0")
        try:
            info = client().verify()
            if info.get("handle"):
                _ok("账号登录", "@%s" % info.get("handle"))
            else:
                _ok("账号登录", "Cookie 会话可用")
                _bad("账号 ID", "Cookie 未包含 twid；我的主页/我喜欢可能不可用")
        except Exception as exc:
            _bad("账号登录", str(exc)[:180])
        try:
            raw = client().home_timeline(count=3, latest=False)
            _ok("首页接口", "可访问" if isinstance(raw, dict) else "返回异常")
        except Exception as exc:
            _bad("首页接口", str(exc)[:180])
    else:
        _bad("Cookie", "未登录或缺少 auth_token / ct0")
    add_folder("清空插件缓存", action="clear_cache")
    add_folder("打开插件设置", action="settings")
    finish(cache=False)


def clear_cache_action():
    n = clear_cache()
    from plugin import notify
    notify("已清理 %d 个缓存文件" % n)
    show_diagnostics()
