import tracklist as tl


def test_scan_time_first_and_title_first():
    text = "0:00 Intro\nSecond Song 3:45\n1:02:03 Finale"
    assert tl.scan_text(text) == [("00:00:00", "Intro"), ("00:03:45", "Second Song"), ("01:02:03", "Finale")]


def test_scan_empty():
    assert tl.scan_text("") == []
    assert tl.scan_text(None) == []


def test_manual_text_tolerates_brackets_numbering_dashes():
    text = "1. [0:00] - Opening\n2) (4:30) Middle Part\n3 - 9:10 - Closer\n\nrandom chatter line"
    assert tl.parse_manual_text(text) == [
        ("00:00:00", "Opening"), ("00:04:30", "Middle Part"), ("00:09:10", "Closer")]


def test_manual_text_sorted_by_time():
    assert tl.parse_manual_text("5:00 B\n0:00 A") == [("00:00:00", "A"), ("00:05:00", "B")]


def test_manual_text_no_matches():
    assert tl.parse_manual_text("nothing here") == []


def test_to_seconds():
    assert tl.to_seconds("01:02:03") == 3723
    assert tl.to_seconds("2:03") == 123


def test_manual_text_ocr_noise_bullets_pipes_spacing():
    text = "•  0:00   Intro\n| 4:30—Middle Part\n· 9:10 : Closer ~"
    assert tl.parse_manual_text(text) == [
        ("00:00:00", "Intro"), ("00:04:30", "Middle Part"), ("00:09:10", "Closer")]


def test_scan_title_with_parenthesised_range():
    text = ("The Lonely Road (0:02 - 8:36)\nSmoke in the Wind (8:36 - 12:06)\n"
            "What Remains to Be Found (57:46 - 1:01:04)")
    assert tl.scan_text(text) == [
        ("00:00:02", "The Lonely Road"), ("00:08:36", "Smoke in the Wind"),
        ("00:57:46", "What Remains to Be Found")]


def test_scan_range_variants_dash_types_brackets_and_leading():
    text = "A [0:00 – 3:00]\nB (3:00 — 5:00)\n5:00 - 7:00 C"
    assert tl.scan_text(text) == [("00:00:00", "A"), ("00:03:00", "B"), ("00:05:00", "C")]


def test_manual_text_strips_range_end():
    assert tl.parse_manual_text("Song (0:02 - 8:36)\nOther (8:36 - 12:06)") == [
        ("00:00:02", "Song"), ("00:08:36", "Other")]
