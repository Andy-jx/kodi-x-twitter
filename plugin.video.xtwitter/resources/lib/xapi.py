# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from auth import cookie_to_header, auth_parts, user_id_from_cookie

WEB_BEARER = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
WEB_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
CATALOG_URL = "https://raw.githubusercontent.com/fa0311/twitter-openapi/refs/heads/main/src/config/placeholder.json"

# Current fallbacks as of 2026-08. Runtime catalog refresh is preferred because X rotates query IDs.
FALLBACK_QIDS = {
    "HomeTimeline": "7zlnp2TxC044W4C1ZUJMHw",
    "HomeLatestTimeline": "0dateTVgvXjpkf7kyBZy0g",
    "UserTweets": "36rb3Xj3iJ64Q-9wKDjCcQ",
    "Likes": "rk2aeVVvKsyUdG3jf5uiLw",
    "Bookmarks": "XD0ViOeSOW4YoeNTGjVaYw",
    "SearchTimeline": "Yw6L66Pw54NHKuq4Dp7b4Q",
    "TweetResultByRestId": "tCVRZ3WCvoj0BVO7BKnL-Q",
    "UserByRestId": "XIpMDIi_YoVzXeoON-cfAQ",
    "UserByScreenName": "IGgvgiOx4QZndDHuD3x9TQ",
}

COMMON_FEATURES = {
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "tweetypie_unmention_optimization_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}


class XAPIError(RuntimeError):
    pass


class XClient(object):
    def __init__(self, cookie, timeout=25, auto_qid=True, qid_overrides=None):
        self.cookie = cookie_to_header(cookie)
        self.auth_token, self.ct0 = auth_parts(self.cookie)
        self.timeout = timeout
        self.auto_qid = bool(auto_qid)
        self.qid_overrides = qid_overrides or {}
        self._catalog = None
        if not self.auth_token or not self.ct0:
            raise XAPIError("Cookie 缺少 auth_token 或 ct0")

    def _headers(self, extra=None):
        headers = {
            "Authorization": "Bearer " + WEB_BEARER,
            "Cookie": self.cookie,
            "x-csrf-token": self.ct0,
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": WEB_UA,
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "zh-cn",
            "Referer": "https://x.com/",
            "Origin": "https://x.com",
        }
        if extra:
            headers.update(extra)
        return headers

    def _decode_json(self, body):
        if not body:
            return {}
        data = json.loads(body.decode("utf-8", "replace"))
        errors = data.get("errors") if isinstance(data, dict) else None
        if errors:
            msg = "; ".join(str(x.get("message") or x) for x in errors[:3])
            raise XAPIError(msg)
        return data

    def _http_error(self, e):
        try:
            detail = e.read().decode("utf-8", "replace")[:500]
        except Exception:
            detail = ""
        suffix = ("：" + detail) if detail else ""
        if e.code in (401, 403):
            return XAPIError("X 登录失效或接口拒绝访问（HTTP %d）%s" % (e.code, suffix))
        if e.code == 429:
            return XAPIError("X 请求过快，已触发限流（HTTP 429），稍后再试")
        return XAPIError("X 接口错误 HTTP %d%s" % (e.code, suffix))

    def _json_get(self, url, headers=None):
        req = Request(url, headers=headers or self._headers(), method="GET")
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return self._decode_json(resp.read())
        except HTTPError as e:
            raise self._http_error(e)
        except URLError as e:
            raise XAPIError("网络错误：%s" % e)
        except ValueError as e:
            raise XAPIError("X 返回的数据不是有效 JSON：%s" % e)

    def _json_post(self, url, payload, headers=None):
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        req = Request(url, data=body, headers=headers or self._headers(), method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as resp:
                return self._decode_json(resp.read())
        except HTTPError as e:
            raise self._http_error(e)
        except URLError as e:
            raise XAPIError("网络错误：%s" % e)
        except ValueError as e:
            raise XAPIError("X 返回的数据不是有效 JSON：%s" % e)

    def _load_catalog(self):
        if self._catalog is not None:
            return self._catalog
        self._catalog = {}
        if not self.auto_qid:
            return self._catalog
        try:
            req = Request(CATALOG_URL, headers={"User-Agent": WEB_UA, "Accept": "application/json"})
            with urlopen(req, timeout=min(self.timeout, 12)) as resp:
                data = json.loads(resp.read().decode("utf-8", "replace"))
            if isinstance(data, dict):
                self._catalog = data
        except Exception:
            self._catalog = {}
        return self._catalog

    def _operation(self, op, qid=None, method=None):
        override = str(self.qid_overrides.get(op) or "").strip()
        entry = self._load_catalog().get(op, {}) if self.auto_qid else {}
        # Explicit user override wins; otherwise prefer refreshed catalog.
        chosen_qid = override or str(entry.get("queryId") or qid or FALLBACK_QIDS.get(op) or "")
        chosen_method = str(entry.get("@method") or method or "GET").upper()
        features = entry.get("features") if isinstance(entry.get("features"), dict) else COMMON_FEATURES
        field_toggles = entry.get("fieldToggles") if isinstance(entry.get("fieldToggles"), dict) else None
        if not chosen_qid:
            raise XAPIError("缺少 %s Query ID" % op)
        return chosen_qid, chosen_method, features, field_toggles

    def _graphql(self, op, variables, qid=None, method=None, allow_alt=False):
        query_id, preferred, features, field_toggles = self._operation(op, qid=qid, method=method)
        methods = [preferred]
        if allow_alt:
            alt = "POST" if preferred == "GET" else "GET"
            methods.append(alt)
        last = None
        for verb in methods:
            try:
                base = "https://x.com/i/api/graphql/%s/%s" % (query_id, op)
                if verb == "POST":
                    payload = {"variables": variables, "features": features}
                    if field_toggles:
                        payload["fieldToggles"] = field_toggles
                    return self._json_post(base, payload)
                params = {
                    "variables": json.dumps(variables, ensure_ascii=False, separators=(",", ":")),
                    "features": json.dumps(features, ensure_ascii=False, separators=(",", ":")),
                }
                if field_toggles:
                    params["fieldToggles"] = json.dumps(field_toggles, ensure_ascii=False, separators=(",", ":"))
                return self._json_get(base + "?" + urlencode(params))
            except XAPIError as exc:
                last = exc
        raise last or XAPIError("X GraphQL 请求失败：%s" % op)

    def user_by_rest_id(self, user_id):
        variables = {
            "userId": str(user_id),
            "withSafetyModeUserFields": True,
        }
        return self._graphql("UserByRestId", variables, method="GET", allow_alt=True)

    def user_by_screen_name(self, screen_name):
        handle = str(screen_name or "").strip().lstrip("@")
        if not handle:
            raise XAPIError("缺少作者用户名")
        variables = {"screen_name": handle}
        return self._graphql("UserByScreenName", variables, method="GET", allow_alt=True)

    def verify(self):
        """Verify the browser-cookie session without the retired v1.1 endpoint.

        X's web session cookies are not OAuth 1.0 credentials.  In 2026 the
        legacy ``account/verify_credentials.json`` endpoint can return HTTP
        404 even when auth_token/ct0 are valid.  The browser itself uses the
        web GraphQL API, so we validate the same session against GraphQL.

        If a full browser Cookie was pasted and contains ``twid``, resolve the
        current profile too.  With only auth_token + ct0 we can still verify
        the session and use timelines/bookmarks/search; current-user pages
        that need a numeric user id will ask for a full Cookie.
        """
        uid = user_id_from_cookie(self.cookie)
        last = None

        if uid:
            try:
                raw = self.user_by_rest_id(uid)
                info = extract_user_info(raw, expected_id=uid)
                if info.get("id"):
                    info["verified_by"] = "graphql_profile"
                    return info
            except XAPIError as exc:
                last = exc

        # HomeTimeline is a good authenticated-session probe and does not
        # require knowing the current user's id.  A valid session returns a
        # timeline dict; expired/revoked cookies normally fail with 401/403.
        try:
            raw = self.home_timeline(count=1, latest=False)
            if isinstance(raw, dict):
                return {
                    "handle": "",
                    "id": uid,
                    "name": "X 账号",
                    "verified_by": "home_timeline",
                }
        except XAPIError as exc:
            last = exc

        # Some accounts can have HomeTimeline temporarily unavailable while
        # Bookmarks still works, so use it as a second authenticated probe.
        try:
            raw = self.bookmarks(count=1)
            if isinstance(raw, dict):
                return {
                    "handle": "",
                    "id": uid,
                    "name": "X 账号",
                    "verified_by": "bookmarks",
                }
        except XAPIError as exc:
            last = exc

        raise last or XAPIError("无法确认 X 登录状态")

    def home_timeline(self, count=20, latest=False, cursor=""):
        op = "HomeLatestTimeline" if latest else "HomeTimeline"
        variables = {
            "count": int(count),
            "includePromotedContent": True,
            "latestControlAvailable": True,
            "seenTweetIds": [],
            "withCommunity": True,
        }
        if not latest:
            variables["requestContext"] = "launch"
        if cursor:
            variables["cursor"] = str(cursor)
        return self._graphql(op, variables, method="POST", allow_alt=True)

    def user_timeline(self, user_id, count=20, cursor=""):
        variables = {
            "userId": str(user_id),
            "count": int(count),
            "includePromotedContent": True,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
        }
        if cursor:
            variables["cursor"] = str(cursor)
        return self._graphql("UserTweets", variables, method="GET", allow_alt=True)

    def likes(self, user_id, count=20, cursor=""):
        variables = {
            "userId": str(user_id),
            "count": int(count),
            "includePromotedContent": False,
            "withClientEventToken": False,
            "withBirdwatchNotes": False,
            "withVoice": True,
        }
        if cursor:
            variables["cursor"] = str(cursor)
        return self._graphql("Likes", variables, method="GET", allow_alt=True)

    def bookmarks(self, count=20, cursor=""):
        variables = {"count": int(count), "includePromotedContent": True}
        if cursor:
            variables["cursor"] = str(cursor)
        return self._graphql("Bookmarks", variables, method="GET", allow_alt=True)

    def search_timeline(self, query, count=20, cursor="", latest=True):
        variables = {
            "rawQuery": str(query),
            "count": int(count),
            "querySource": "typed_query",
            "product": "Latest" if latest else "Top",
        }
        if cursor:
            variables["cursor"] = str(cursor)
        # X has alternated SearchTimeline between GET and POST. Try refreshed catalog first, then the other method.
        return self._graphql("SearchTimeline", variables, method="POST", allow_alt=True)

    def tweet_detail(self, tweet_id):
        variables = {
            "tweetId": str(tweet_id),
            "withCommunity": False,
            "includePromotedContent": False,
            "withVoice": False,
        }
        return self._graphql("TweetResultByRestId", variables, method="GET", allow_alt=True)


def _walk(obj):
    yield obj
    if isinstance(obj, dict):
        for v in obj.values():
            for x in _walk(v):
                yield x
    elif isinstance(obj, list):
        for v in obj:
            for x in _walk(v):
                yield x


def _unwrap_tweet_result(result):
    cur = result if isinstance(result, dict) else {}
    if cur.get("__typename") == "TweetWithVisibilityResults" and isinstance(cur.get("tweet"), dict):
        cur = cur["tweet"]
    return cur


def _unwrap_user_result(result):
    cur = result if isinstance(result, dict) else {}
    # GraphQL occasionally wraps user results in an unavailable/tombstone
    # object.  Walk one level for the common wrappers while keeping this
    # parser tolerant of schema changes.
    for key in ("user", "result"):
        child = cur.get(key) if isinstance(cur, dict) else None
        if isinstance(child, dict) and (child.get("rest_id") or child.get("legacy")):
            cur = child
    return cur


def extract_user_info(data, expected_id=""):
    candidates = []
    for node in _walk(data):
        if not isinstance(node, dict):
            continue
        legacy = node.get("legacy")
        uid = str(node.get("rest_id") or "")
        if not isinstance(legacy, dict) or not uid:
            continue
        handle = str(legacy.get("screen_name") or "")
        name = str(legacy.get("name") or handle or "X 账号")
        if handle:
            candidates.append({"handle": handle, "id": uid, "name": name})
    if expected_id:
        for info in candidates:
            if info.get("id") == str(expected_id):
                return info
    return candidates[0] if candidates else {"handle": "", "id": str(expected_id or ""), "name": "X 账号"}


def collect_tweet_results(data):
    out = []
    seen = set()
    for node in _walk(data):
        if not isinstance(node, dict):
            continue
        tr = node.get("tweet_results")
        if not isinstance(tr, dict):
            continue
        result = _unwrap_tweet_result(tr.get("result"))
        tid = str(result.get("rest_id") or "")
        if tid and tid not in seen:
            seen.add(tid)
            out.append(result)
    try:
        result = _unwrap_tweet_result(data.get("data", {}).get("tweetResult", {}).get("result", {}))
        tid = str(result.get("rest_id") or "")
        if tid and tid not in seen:
            seen.add(tid)
            out.append(result)
    except Exception:
        pass
    return out


def collect_tweet_ids(data):
    return [str(x.get("rest_id")) for x in collect_tweet_results(data) if x.get("rest_id")]


def find_bottom_cursor(data):
    # Current web timelines expose bottom cursors as TimelineTimelineCursor nodes.
    fallback = ""
    for node in _walk(data):
        if not isinstance(node, dict):
            continue
        value = node.get("value")
        if not isinstance(value, str) or not value:
            continue
        ctype = str(node.get("cursorType") or node.get("cursor_type") or "").lower()
        if ctype == "bottom":
            return value
        entry_id = str(node.get("entryId") or node.get("entry_id") or "").lower()
        if "cursor-bottom" in entry_id:
            fallback = value
    return fallback


def _first_text(result):
    paths = [("note_tweet", "note_tweet_results", "result", "text"), ("details", "full_text"), ("legacy", "full_text")]
    for path in paths:
        cur = result
        ok = True
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                ok = False
                break
            cur = cur[key]
        if ok and isinstance(cur, str) and cur.strip():
            return cur.strip()
    return ""


def _author_meta(result):
    # Prefer the tweet author's embedded user_results node.  It contains
    # rest_id + legacy.screen_name on current X GraphQL responses.
    for node in _walk(result.get("core", {})):
        if not isinstance(node, dict):
            continue
        legacy = node.get("legacy")
        if isinstance(legacy, dict) and legacy.get("screen_name"):
            handle = str(legacy.get("screen_name") or "").lstrip("@")
            return {
                "handle": handle,
                "id": str(node.get("rest_id") or ""),
                "name": str(legacy.get("name") or handle or "X"),
            }
    # Fallback for alternate/flattened result shapes.
    for node in _walk(result.get("core", {})):
        if not isinstance(node, dict):
            continue
        handle = str(node.get("screen_name") or "").lstrip("@")
        if handle:
            return {"handle": handle, "id": str(node.get("rest_id") or ""), "name": str(node.get("name") or handle)}
    return {"handle": "", "id": "", "name": "X"}


def _first_author(result):
    meta = _author_meta(result)
    return ("@" + meta["handle"]) if meta.get("handle") else (meta.get("name") or "X")


def _variant_score(v):
    url = str(v.get("url") or "")
    if not url:
        return (-1, -1)
    ctype = str(v.get("content_type") or v.get("contentType") or "")
    bitrate = v.get("bitrate") or v.get("bit_rate") or 0
    try:
        bitrate = int(bitrate)
    except Exception:
        bitrate = 0
    is_mp4 = int("mp4" in ctype.lower() or ".mp4" in url.lower())
    return (is_mp4, bitrate)


def _thumb_from_media(media):
    return str(media.get("media_url_https") or media.get("media_url") or media.get("preview_image_url") or "")


def extract_video_items_from_result(result):
    result = _unwrap_tweet_result(result)
    tweet_id = str(result.get("rest_id") or "")
    text = _first_text(result)
    author_meta = _author_meta(result)
    author = ("@" + author_meta["handle"]) if author_meta.get("handle") else (author_meta.get("name") or "X")
    items = []
    seen_urls = set()
    for node in _walk(result):
        if not isinstance(node, dict):
            continue
        vi = node.get("video_info") or node.get("videoInfo")
        if not isinstance(vi, dict):
            continue
        variants = vi.get("variants") or []
        if not isinstance(variants, list):
            continue
        valid = [v for v in variants if isinstance(v, dict) and v.get("url")]
        if not valid:
            continue
        valid.sort(key=_variant_score, reverse=True)
        mp4s = [v for v in valid if _variant_score(v)[0] == 1]
        chosen = sorted(mp4s, key=_variant_score, reverse=True)[0] if mp4s else valid[0]
        url = str(chosen.get("url") or "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        thumb = _thumb_from_media(node)
        label_text = re.sub(r"\s+", " ", text).strip()
        if len(label_text) > 72:
            label_text = label_text[:69] + "..."
        label = (author + " · " + label_text).strip(" ·") if label_text else (author + " · X 视频")
        items.append({
            "tweet_id": tweet_id,
            "url": url,
            "thumb": thumb,
            "label": label,
            "plot": text,
            "author": author,
            "author_handle": author_meta.get("handle") or "",
            "author_id": author_meta.get("id") or "",
        })
    return items


def extract_video_items(data):
    items = []
    seen = set()
    for result in collect_tweet_results(data):
        for item in extract_video_items_from_result(result):
            key = item.get("url") or (item.get("tweet_id"), item.get("label"))
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
    return items


def enrich_missing_videos(client, data, max_detail=12, want=20):
    items = extract_video_items(data)
    if len(items) >= min(4, want):
        return items[:want]
    seen_urls = set(i.get("url") for i in items)
    for tid in collect_tweet_ids(data)[:max_detail]:
        if len(items) >= want:
            break
        try:
            detail = client.tweet_detail(tid)
            for i in extract_video_items(detail):
                if i.get("url") in seen_urls:
                    continue
                seen_urls.add(i.get("url"))
                items.append(i)
            time.sleep(0.12)
        except Exception:
            continue
    return items[:want]
