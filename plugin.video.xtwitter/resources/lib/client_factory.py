# -*- coding: utf-8 -*-
from __future__ import annotations

from settings import auto_qid, cookie, qid_overrides
from xapi import XClient


def client():
    return XClient(cookie(), auto_qid=auto_qid(), qid_overrides=qid_overrides())
