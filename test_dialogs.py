"""Layout/behaviour tests for the tracklist dialogs. Windows stay withdrawn:
no grab_set, no wait_window, no focus, nothing mapped."""
import pytest
import customtkinter as ctk
import gui


@pytest.fixture(scope="module")
def root():
    r = ctk.CTk()
    r.withdraw()
    yield r
    r.destroy()


def _outer(dialog, w):
    """The direct pack child of dialog that contains w (scrollable frames wrap themselves)."""
    while w.master is not dialog and w.master is not None:
        w = w.master
    return w


def _fixed_required_px(dialog, expander):
    expander = _outer(dialog, expander)
    """Sum of required heights of every packed child except the expanding one."""
    total = 0
    for w in dialog.pack_slaves():
        if w is expander:
            continue
        info = w.pack_info()
        pady = info["pady"]
        pad = sum(pady) if isinstance(pady, (tuple, list)) else 2 * int(pady)
        total += w.winfo_reqheight() + pad
    return total


def _is_bottom_packed_before(dialog, widget_in_row, expander):
    slaves = dialog.pack_slaves()
    expander = _outer(dialog, expander)
    row = widget_in_row
    while row.master is not dialog:
        row = row.master
    return row.pack_info()["side"] == "bottom" and slaves.index(row) < slaves.index(expander)


def test_manual_dialog_reserves_button_row_first(root):
    ui = gui.build_manual_tracklist_dialog(root)
    try:
        assert _is_bottom_packed_before(ui.dialog, ui.btn_ok, ui.box)
    finally:
        ui.dialog.destroy()


def test_manual_dialog_buttons_fit_at_min_size(root):
    ui = gui.build_manual_tracklist_dialog(root)
    try:
        ui.dialog.update_idletasks()
        scale = ui.dialog._get_window_scaling()
        min_w, min_h = ui.min_size
        need = _fixed_required_px(ui.dialog, ui.box)
        # leave at least 100 logical px for the textbox at the minimum size
        assert need + 100 * scale <= min_h * scale
    finally:
        ui.dialog.destroy()


def test_manual_dialog_resizable_with_minsize(root):
    ui = gui.build_manual_tracklist_dialog(root)
    try:
        assert ui.dialog.resizable() == (True, True) or tuple(ui.dialog.wm_resizable()) == (1, 1)
        assert ui.dialog.bind("<Control-Return>")
    finally:
        ui.dialog.destroy()


def test_ok_parses_and_returns(root):
    ui = gui.build_manual_tracklist_dialog(root)
    ui.box.insert("1.0", "0:00 Intro\n3:45 Song")
    ui.on_ok()
    assert ui.result["data"] == [("00:00:00", "Intro"), ("00:03:45", "Song")]


def test_ok_with_no_times_keeps_dialog_open(root):
    ui = gui.build_manual_tracklist_dialog(root)
    try:
        ui.box.insert("1.0", "no times here")
        ui.on_ok()
        assert ui.result["data"] is None
        assert ui.dialog.winfo_exists()
    finally:
        ui.dialog.destroy()


def test_paste_with_clipboard_image_runs_ocr(root):
    ui = gui.build_manual_tracklist_dialog(
        root, ocr_engine=lambda p: "0:00 A\n1:00 B", clipboard_image=lambda: "clip.png")
    try:
        assert ui.on_paste() == "break"
        assert "0:00 A" in ui.box.get("1.0", "end")
    finally:
        ui.dialog.destroy()


def test_paste_text_is_left_to_default(root):
    ui = gui.build_manual_tracklist_dialog(root, clipboard_image=lambda: None)
    try:
        assert ui.on_paste() is None
    finally:
        ui.dialog.destroy()


def test_confirm_dialog_reserves_button_row_first(root):
    ui = gui.build_confirm_dialog(root, [("00:00:00", "A"), ("00:01:00", "B")])
    try:
        assert _is_bottom_packed_before(ui.dialog, ui.btn_confirm, ui.list_frame)
        ui.dialog.update_idletasks()
        scale = ui.dialog._get_window_scaling()
        assert _fixed_required_px(ui.dialog, ui.list_frame) + 100 * scale <= ui.min_size[1] * scale
    finally:
        ui.dialog.destroy()


def test_confirm_collects_edited_rows(root):
    ui = gui.build_confirm_dialog(root, [("00:00:00", "A")])
    ui.entries[0][1].delete(0, "end")
    ui.entries[0][1].insert(0, "Renamed")
    ui.on_confirm()
    assert ui.result == {"confirmed": True, "data": [("00:00:00", "Renamed")]}
