"""OCR seam: Windows built-in text recognition (Windows.Media.Ocr) via winsdk.

Kept separate so parsing/tests never import Windows APIs. winsdk is imported
lazily; if it is missing the app still runs and image_to_text reports a message.
"""
import asyncio
import os


class OcrUnavailable(Exception):
    pass


async def _recognize(path):
    try:
        from winsdk.windows.media.ocr import OcrEngine
        from winsdk.windows.graphics.imaging import BitmapDecoder
        from winsdk.windows.storage import StorageFile, FileAccessMode
    except ImportError as e:
        raise OcrUnavailable("Windows OCR needs the 'winsdk' package (pip install winsdk).") from e
    engine = OcrEngine.try_create_from_user_profile_languages()
    if engine is None:
        raise OcrUnavailable("No Windows OCR language pack is installed.")
    file = await StorageFile.get_file_from_path_async(os.path.abspath(path))
    stream = await file.open_async(FileAccessMode.READ)
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()
    result = await engine.recognize_async(bitmap)
    lines = result.lines
    out = []
    keep = []  # hold WinRT objects alive; releasing them mid-loop crashes winsdk
    for i in range(lines.size):
        line = lines.get_at(i)
        keep.append(line)
        out.append(line.text)
    return "\n".join(out)


def windows_ocr(path):
    """Return recognised text, one line per text line. Raises OcrUnavailable."""
    return asyncio.run(_recognize(path))


def image_to_text(path, engine=windows_ocr):
    """Returns (text, error_message). Never raises; error_message is None on success."""
    try:
        text = engine(path)
    except OcrUnavailable as e:
        return "", str(e)
    except Exception as e:
        return "", "Could not read text from image: %s" % e
    if not text or not text.strip():
        return "", "No text was recognised in that image."
    return text, None


def clipboard_image_path(grab=None):
    """If the clipboard holds an image, save it to a temp PNG and return the path; else None.

    Text on the clipboard (or no Pillow / any error) returns None so normal paste works.
    """
    try:
        if grab is None:
            from PIL import ImageGrab
            grab = ImageGrab.grabclipboard
        img = grab()
        if img is None or isinstance(img, (list, tuple, str)) or not hasattr(img, "save"):
            return None
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".png", prefix="wme-clip-")
        os.close(fd)
        img.save(path, "PNG")
        return path
    except Exception:
        return None
