# Where things stand

Last updated: 2026-11-18

## What this is

A Windows desktop app (`gui.py`, customtkinter + yt-dlp + ffmpeg) that downloads YouTube audio or video and cuts albums into tracks using a track list found in the description or comments.

## Done on 2026-11-18

All three tasks are closed in the local task list (`tally list`).

| Task | What changed | Commit |
|------|--------------|--------|
| wme-4773d1 | Manual fallback when no track list is found: paste text, or read it from an image with Windows' built-in text recognition (`ocr.py`, `winsdk`). | `8a6aa9e`, `8fa4371` |
| wme-42108b | Automatic search now accepts `Title (start - end)` listings. Found with https://www.youtube.com/watch?v=Ry34Swxoq6Y, whose 40-track listing sits in a comment. | `8aeefee` |
| wme-c70ed4 | Dialog buttons can no longer be squeezed out of view; main action is highlighted; Ctrl+Enter proceeds; Ctrl+V with a copied image reads it. | `1830b50` |

## What is verified, and what is not

- Verified by the owner on a real run: reading a track list from an image and proceeding to the cut.
- Verified by script, not through the app window: the automatic search returns 40 tracks for the video above.
- Tests: `python -m pytest -q` reported 25 passed at commit `1830b50`.
- Not verified: Ctrl+V with a real copied image, and Ctrl+Enter with a real key press (tested with stand-ins only).
- Never explained: why the owner first could not see the proceed button. Off-screen measurement at 150% scaling showed the old dialog fit with 15 px to spare. If it happens again, get a screenshot.

## Known limits

- Windows' text recognition can drop a time on a line, most often hour-format ones such as `1:02:30`. That line is then skipped unless corrected in the box.
- A comment with a single stray time range cannot beat a real listing (the comment with the most matches wins), but there is no dedicated test for that.
- On Python 3.13 the `winsdk` line objects crash if iterated directly; `ocr.py` indexes them with `get_at(i)` on purpose. Do not "tidy" that loop.

## Working-folder notes

- `.gitignore` has an uncommitted change and `.tally/` is untracked; both come from the local task list and were left alone on purpose.
- `push1.wav` and `push2.wav` are the owner's files; do not add, commit or delete them.
- This is a personal project: never run a plain `tally init` or `tally sync` here.

## Next

- Run the app on the video above and confirm the confirm dialog lists the 40 tracks without the manual box.
- Optional: pyflakes still reports unused imports in `gui.py`.
