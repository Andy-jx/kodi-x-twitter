# Installation

## Requirements

- Kodi 21 or newer
- Python 3 Kodi runtime
- An X account with a currently valid browser session

## Install the add-on

1. Open this repository's **Releases** page and download `plugin.video.xtwitter-1.0.6.zip` from release `v1.0.6`.
2. Open Kodi.
3. Go to **Add-ons** → **Install from zip file**.
4. Choose the downloaded ZIP.
5. Open **X (Twitter)** from Video add-ons.

## Login cookie

The add-on expects at least:

```text
auth_token=XXX;ct0=XXX
```

Use the values from the same active browser session. Do not mix an `auth_token` from one session with a `ct0` from another.

### Android / ADB note

Long values can be truncated or misinterpreted when entered through `adb shell input text`, especially around shell metacharacters such as `;`. If you use ADB, verify that the entire value reaches the Kodi text field. `scrcpy` clipboard paste is often safer for long cookie strings.

## Updating

Kodi can normally install a newer ZIP over an existing version. Local add-on data, including Local Favorites, is stored separately from the add-on code.
