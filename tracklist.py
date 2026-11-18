"""Pure tracklist parsing helpers (no GUI imports, unit-testable)."""
import re

_TIME = r'(?:\d{1,2}:)?\d{1,2}:\d{2}'


def _norm_time(t):
    parts = [int(x) for x in t.split(':')]
    if len(parts) == 2:
        parts = [0] + parts
    return "%02d:%02d:%02d" % tuple(parts)


def _strip_title(s):
    return re.sub(r'^[-\s]+|[-\s]+$', '', s.strip())


def scan_text(text):
    """Strict scan used for auto-detection in descriptions/comments."""
    if not text:
        return []
    found = []
    for line in text.split('\n'):
        line = line.strip()
        m = re.search(r'^(?P<time>' + _TIME + r')\s+(?P<title>.+)$', line) or \
            re.search(r'^(?P<title>.+?)\s+(?P<time>' + _TIME + r')$', line)
        if m:
            found.append((_norm_time(m.group('time')), _strip_title(m.group('title'))))
    return found


def parse_manual_text(text):
    """Lenient parse of user-pasted text: [0:00], (0:00), '1.' numbering, dashes."""
    if not text:
        return []
    found = []
    for line in text.split('\n'):
        line = re.sub(r'^\s*\d{1,3}\s*[.)\-]\s+', '', line)  # leading track number
        m = re.search(r'(?<![\d:])(?P<time>' + _TIME + r')(?![\d:])', line)
        if not m:
            continue
        rest = line[:m.start()] + ' ' + line[m.end():]
        rest = re.sub(r'[\[\]()]', ' ', rest)
        title = _strip_title(rest)
        title = re.sub(r'\s+', ' ', title)
        if title:
            found.append((_norm_time(m.group('time')), title))
    return sorted(found, key=lambda x: to_seconds(x[0]))


def to_seconds(t):
    parts = list(map(int, t.split(':')))
    return parts[0] * 3600 + parts[1] * 60 + parts[2] if len(parts) == 3 else parts[0] * 60 + parts[1]
