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
