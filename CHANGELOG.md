# Changelog

All notable stable changes are documented here.

## v1.0.6 — Stable baseline

- Added local add-on Favorites independent from X account Likes.
- Added long-press Add/Remove Local Favorite actions.
- Added long-press author-page navigation.
- Author pages prefer `SearchTimeline` with `from:<handle>` to reduce dependency on unstable `UserByScreenName` / `UserTweets` paths.
- Added manual refresh to For You, Following and author pages.
- Preserved existing playback behavior: fresh resolving before play and highest-bitrate playable MP4 selection.
- Preserved source video orientation/aspect ratio.

### Publication note

This repository publishes v1.0.6 as the stable baseline. Later experimental builds are not automatically considered stable releases.
