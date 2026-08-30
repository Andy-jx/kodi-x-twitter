# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmcgui
import xbmcplugin

from plugin import HANDLE, add_folder, add_label, add_video, finish, notify
from settings import history_limit
from storage import history_clear, history_load


def show_history():
    xbmcplugin.setPluginCategory(HANDLE, "观看历史")
    rows = history_load()
    if not rows:
        add_label("还没有观看历史")
    else:
        for row in rows[:history_limit()]:
            add_video(row)
        add_folder("清空观看历史", action="clear_history")
    finish(cache=False)


def clear_history_action():
    if xbmcgui.Dialog().yesno("X（Twitter）", "确定清空观看历史？"):
        history_clear()
        notify("观看历史已清空")
    show_history()
