import ocr


def test_returns_text_from_engine():
    text, err = ocr.image_to_text("x.png", engine=lambda p: "0:00 Intro\n3:45 Song")
    assert text == "0:00 Intro\n3:45 Song" and err is None


def test_unavailable_gives_message_not_exception():
    def boom(p):
        raise ocr.OcrUnavailable("winsdk missing")
    text, err = ocr.image_to_text("x.png", engine=boom)
    assert text == "" and "winsdk missing" in err


def test_empty_result_gives_message():
    text, err = ocr.image_to_text("x.png", engine=lambda p: "  \n ")
    assert text == "" and err


def test_unexpected_error_is_caught():
    def boom(p):
        raise RuntimeError("bad image")
    text, err = ocr.image_to_text("x.png", engine=boom)
    assert text == "" and "bad image" in err


def test_clipboard_image_saved_to_png(tmp_path):
    from PIL import Image
    import os
    p = ocr.clipboard_image_path(grab=lambda: Image.new("RGB", (4, 4)))
    try:
        assert p and p.endswith(".png") and os.path.getsize(p) > 0
    finally:
        if p:
            os.remove(p)


def test_clipboard_without_image_returns_none():
    assert ocr.clipboard_image_path(grab=lambda: None) is None
    assert ocr.clipboard_image_path(grab=lambda: ["C:/a.txt"]) is None
    assert ocr.clipboard_image_path(grab=lambda: (_ for _ in ()).throw(OSError("x"))) is None
