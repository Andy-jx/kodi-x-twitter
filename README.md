# X for Kodi

> An unofficial Kodi add-on for browsing and playing X/Twitter videos on TV.

[![Kodi](https://img.shields.io/badge/Kodi-21%2B-17B2E7?logo=kodi&logoColor=white)](https://kodi.tv/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Validate](https://github.com/hjx885210-lang/kodi-x-twitter/actions/workflows/validate.yml/badge.svg)](https://github.com/hjx885210-lang/kodi-x-twitter/actions/workflows/validate.yml)

**X for Kodi** is a TV-first Kodi video add-on for X/Twitter. It focuses on a simple remote-control experience rather than reproducing the full X web client.

**中文说明：** 这是一个面向电视、大屏和遥控器场景的非官方 X/Twitter Kodi 视频插件。

## Download

### Stable: v1.0.6

**[Download the latest stable ZIP from GitHub Releases](https://github.com/hjx885210-lang/kodi-x-twitter/releases/tag/v1.0.6)**

Release assets include:

- `plugin.video.xtwitter-1.0.6.zip` — the exact previously tested stable package
- `SHA256SUMS.txt` — checksum for verification

The `v1.0.6` tag preserves the exact tested stable source. The default `main` branch keeps that stable codebase plus repository/documentation maintenance.

## Stable features

- Cookie login (`auth_token` + `ct0`)
- For You timeline video browsing
- Following timeline video browsing
- Manual refresh for For You / Following pages
- X video search
- Author video pages
- Manual refresh on author pages
- Local Favorites stored by the Kodi add-on
- Long-press: add/remove Local Favorites
- Long-press: open author page
- Pagination
- Fresh media URL resolving before playback
- Highest-bitrate directly playable MP4 selection
- Original landscape / portrait aspect ratio preserved
- Android / Kodi remote-control friendly UI

The codebase also contains history, bookmark and diagnostics utilities. Features that depend on unstable private X Web endpoints may change without notice and are not treated as stable guarantees.

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

Video context menu:

```text
Long press video
├─ Add to Local Favorites / Remove from Local Favorites
└─ Open author page
```

## Install

1. Install Kodi 21 or newer.
2. Download the stable ZIP above.
3. Kodi → **Add-ons** → **Install from zip file**.
4. Select `plugin.video.xtwitter-1.0.6.zip`.
5. Open **X (Twitter)**.
6. Paste your own X cookie in the login screen.

Minimum cookie fields:

```text
auth_token=XXX;ct0=XXX
```

Use the ASCII semicolon `;` as the separator.

Detailed instructions: [`docs/INSTALL.md`](docs/INSTALL.md)

## Security

**Never post your real X cookie, `auth_token`, or `ct0` in Issues, screenshots, logs, chats, or public repositories.** Treat them like passwords.

This repository does not include any user credentials. Local Favorites are stored in Kodi's local add-on data.

See [`SECURITY.md`](SECURITY.md).

## Privacy-friendly project presentation

Public project pages intentionally do **not** include private recommendation feeds, adult/sensitive media, real account cookies, or private account information. Screenshots are optional and should only show clean Kodi UI or error messages with sensitive data removed.

## Source layout

```text
plugin.video.xtwitter/       Kodi add-on source
├─ addon.py
├─ addon.xml
└─ resources/
    ├─ lib/
    ├─ language/
    └─ settings.xml

docs/                        Installation and troubleshooting
.github/                     CI and Issue templates
GitHub Releases              Stable install ZIP + SHA256 checksum
```

The `plugin.video.xtwitter/` directory contains the stable source line. The exact tested ZIP is published as the `v1.0.6` GitHub Release asset, and the `v1.0.6` tag preserves the corresponding release source.

## Troubleshooting

If a timeline fails to load, first verify that the same cookie still works in the browser and that `auth_token` and `ct0` were entered completely. A malformed or truncated `ct0` can cause authenticated X Web requests to fail even when some read-only requests still appear to work.

More: [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)

## Development

Every push and pull request runs a lightweight validation workflow:

- Python syntax compilation
- `addon.xml` XML parsing
- source tree checks
- Kodi ZIP packaging check

See [`.github/workflows/validate.yml`](.github/workflows/validate.yml).

## Contributing

Bug reports and compatibility feedback are welcome. Please remove all credentials and private feed content before posting.

See [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md).

## License

MIT License. See [`LICENSE`](LICENSE).

## Disclaimer

This is an unofficial community project and is not affiliated with, endorsed by, or sponsored by X Corp., Twitter, or the Kodi Foundation.

Users are responsible for complying with applicable law, X's terms and Kodi's usage rules. This project provides client-side code only and does not host or distribute third-party media.
