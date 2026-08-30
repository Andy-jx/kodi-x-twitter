# Contributing

Contributions, bug reports and compatibility feedback are welcome.

## Before opening an Issue

Please include:

- add-on version
- Kodi version
- operating system / Android version
- device model when relevant
- exact error message
- relevant `kodi.log` lines

Remove all cookies, tokens, email addresses, phone numbers and private feed content first.

## Pull requests

Keep changes focused. Avoid mixing unrelated refactors with endpoint fixes.

Before submitting:

```bash
python -m compileall -q plugin.video.xtwitter
python - <<'PY'
import xml.etree.ElementTree as ET
ET.parse('plugin.video.xtwitter/addon.xml')
print('addon.xml OK')
PY
```

Do not commit generated `__pycache__` or `.pyc` files.
