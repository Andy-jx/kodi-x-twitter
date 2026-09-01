# X / Twitter Video Add-on for Kodi

> Unofficial Kodi 21+ video add-on for browsing, searching and playing X/Twitter videos on TV.

[![Kodi](https://img.shields.io/badge/Kodi-21%2B-17B2E7?logo=kodi&logoColor=white)](https://kodi.tv/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Validate](https://github.com/Andy-jx/kodi-x-twitter/actions/workflows/validate.yml/badge.svg)](https://github.com/Andy-jx/kodi-x-twitter/actions/workflows/validate.yml)

**X for Kodi** is a remote-control-friendly Kodi video client focused on X/Twitter video browsing. It is intentionally smaller than the web client and does not host third-party media.

**中文说明：** 这是一个面向电视、大屏和遥控器场景的非官方 X/Twitter Kodi 视频插件，重点解决视频浏览、搜索、作者页和播放。

Keywords: `Kodi Twitter addon`, `Kodi X plugin`, `Twitter video Kodi`, `X video Kodi`, `Kodi video plugin`, `Kodi 21 addon`.

## Why this project

The normal X/Twitter website is designed for phones and browsers. This add-on provides a TV-first interface inside Kodi with a simple directory layout, remote-control navigation and fresh media URL resolving before playback.

## Download

### Stable: v1.0.6

**[Download the latest stable ZIP from GitHub Releases](https://github.com/Andy-jx/kodi-x-twitter/releases/tag/v1.0.6)**

Release assets include:

- `plugin.video.xtwitter-1.0.6.zip` — tested stable package
- `SHA256SUMS.txt` — checksum for verification

## Features

- Cookie login using your own X account (`auth_token` + `ct0`)
- For You timeline video browsing
- Following timeline video browsing
- X video search
- Author video pages
- Local Favorites stored only in Kodi add-on data
- Watch history
- Pagination and manual refresh
- Long-press: add/remove Local Favorites
- Long-press: open author page
- Fresh media URL resolving before playback
- Highest-bitrate directly playable MP4 selection
- Portrait and landscape aspect ratio preserved
- Android / TV / remote-control-friendly Kodi UI

Features that depend on private X web endpoints may change when X changes its website APIs.

## Kodi menu

```text
X (Twitter)
├─ For You / 首页推荐
├─ Following / 关注页
├─ Local Favorites / 本地我喜欢
├─ Search X videos / 搜索视频
├─ Author pages / 作者主页
├─ Watch history / 观看历史
├─ Account & Settings / 账号与设置
└─ Diagnostics / 诊断
```

## Install

1. Install Kodi 21 or newer.
2. Download `plugin.video.xtwitter-1.0.6.zip` from Releases.
3. Kodi → **Add-ons** → **Install from zip file**.
4. Select the ZIP and open **X (Twitter)**.
5. Use your own X login cookie when account features are needed.

Minimum cookie fields:

```text
auth_token=XXX;ct0=XXX
```

Detailed guide: [`docs/INSTALL.md`](docs/INSTALL.md)

## Security and privacy

**Never post your real X cookie, `auth_token`, `ct0`, private feed screenshots or account data in Issues, logs or public repositories.** Treat cookies like passwords.

This project does not ship user credentials and does not host X/Twitter media. Local Favorites and history remain in Kodi's local add-on data.

See [`SECURITY.md`](SECURITY.md).

## Public project safety

This repository is intended for normal software development and media-client use. Public screenshots and examples should use ordinary, non-sensitive content only. Do not upload copyrighted media files, private account data, sexually explicit material, illegal content, leaked credentials, license keys or instructions whose primary purpose is bypassing access controls.

## Development

Every push and pull request runs validation for:

- Python syntax
- `addon.xml` parsing
- source-tree checks
- Kodi ZIP packaging

Workflow: [`.github/workflows/validate.yml`](.github/workflows/validate.yml)

## Discoverability

Suggested GitHub Topics for this repository:

`kodi`, `kodi-addon`, `kodi-plugin`, `twitter`, `x-twitter`, `video-plugin`, `python`, `android-tv`, `media-center`

A good project description is:

> Unofficial Kodi 21+ add-on for browsing, searching and playing X/Twitter videos on TV.

These keywords describe the project accurately without promising unsupported features or encouraging policy violations.

## Contributing

Bug reports and compatibility feedback are welcome. Remove all credentials and private feed content before posting.

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT License. See [`LICENSE`](LICENSE).

## Disclaimer

This is an unofficial community project and is not affiliated with, endorsed by, or sponsored by X Corp., Twitter, or the Kodi Foundation.

Users are responsible for complying with applicable law, X's terms and Kodi's usage rules. This project provides client-side code only and does not host or distribute third-party media.
