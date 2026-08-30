# -*- coding: utf-8 -*-
from __future__ import annotations


def set_video_info(li, info):
    info = info or {}
    try:
        tag = li.getVideoInfoTag()
        if hasattr(tag, "setTitle"):
            tag.setTitle(str(info.get("title") or ""))
        if hasattr(tag, "setPlot"):
            tag.setPlot(str(info.get("plot") or ""))
        if hasattr(tag, "setStudio") and info.get("studio"):
            tag.setStudio(str(info.get("studio")))
        if hasattr(tag, "setMediaType"):
            tag.setMediaType("video")
        if hasattr(tag, "setDuration") and info.get("duration"):
            tag.setDuration(int(info.get("duration") or 0))
        return
    except Exception:
        pass
    try:
        li.setInfo("video", {
            "title": info.get("title") or "",
            "plot": info.get("plot") or "",
            "studio": info.get("studio") or "",
            "duration": info.get("duration") or 0,
        })
    except Exception:
        pass
