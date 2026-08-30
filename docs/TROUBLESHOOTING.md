# Troubleshooting

## Login says success but For You fails

A common cause is an incomplete or mismatched `ct0`. Some requests may still appear authenticated while timeline POST requests fail.

Re-enter `auth_token` and `ct0` from the same browser session and make sure neither value is truncated.

## HTTP 401 / code 32

This means the X Web endpoint rejected authentication for that request. Check cookie completeness first before reinstalling the add-on.

## Author page fails

v1.0.6 prefers an X search query using `from:<handle>` for author videos and retains fallback behavior. X Web internal endpoints can change without notice.

## Playback fails after a video was listed

Media URLs can expire. The add-on attempts to re-resolve the media URL immediately before playback.

## Getting `kodi.log` on Android

Typical Kodi log path:

```text
/sdcard/Android/data/org.xbmc.kodi/files/.kodi/temp/kodi.log
```

Example:

```bat
adb pull "/sdcard/Android/data/org.xbmc.kodi/files/.kodi/temp/kodi.log" ".\kodi.log"
```

Before posting logs publicly, remove cookies, tokens and private account information.
