import customtkinter as ctk
import yt_dlp
import threading
import os
import sys
import re
import subprocess
import tracklist as tracklist_mod
import ocr as ocr_mod
from tkinter import filedialog

# ── Hacker Noir Palette ──────────────────────────────────────────────────────
BG       = "#0a0a0a"
BG_FRAME = "#0d0d0d"
BG_ENTRY = "#111111"
FG       = "#00ff41"
FG_DIM   = "#007a1e"
FG_HOVER = "#00cc35"
BORDER   = "#003d0f"

FONT_TITLE = ("Share Tech Mono", 22, "bold")
FONT_SUB   = ("Share Tech Mono", 11)
FONT_MAIN  = ("Share Tech Mono", 13)
FONT_SMALL = ("Share Tech Mono", 11)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


def _btn(parent, text, command, state="normal", **kw):
    return ctk.CTkButton(
        parent, text=text, command=command, state=state,
        fg_color=BG_FRAME, hover_color=BG_ENTRY,
        text_color=FG, border_color=BORDER, border_width=1,
        font=FONT_SMALL, **kw
    )


def _radio(parent, text, variable, value):
    return ctk.CTkRadioButton(
        parent, text=text, variable=variable, value=value,
        text_color=FG, fg_color=FG, hover_color=FG_HOVER,
        border_color=FG_DIM, font=FONT_SMALL
    )


def _btn_primary(parent, text, command, **kw):
    return ctk.CTkButton(
        parent, text=text, command=command,
        fg_color=FG_DIM, hover_color=FG, text_color=BG,
        border_color=FG, border_width=1,
        font=("Share Tech Mono", 11, "bold"), **kw
    )


class _Ui:
    """Plain attribute bag for a built dialog."""
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _setup_dialog(dialog, title, width, height, min_w, min_h):
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.minsize(min_w, min_h)
    dialog.resizable(True, True)
    dialog.configure(fg_color=BG)


def build_manual_tracklist_dialog(parent, ocr_engine=None, clipboard_image=None, pick_image=None):
    """Build (but do not show modally) the manual tracklist dialog.

    The button row is packed at the bottom BEFORE the expanding textbox, so the
    action buttons keep their space whatever the window size or display scaling.
    """
    ocr_engine = ocr_engine or ocr_mod.windows_ocr
    clipboard_image = clipboard_image or ocr_mod.clipboard_image_path
    min_size = (520, 400)
    dialog = ctk.CTkToplevel(parent)
    _setup_dialog(dialog, "Enter Tracklist Manually", 560, 520, *min_size)

    btn_row = ctk.CTkFrame(dialog, fg_color=BG)
    btn_row.pack(side="bottom", fill="x", padx=10, pady=(4, 10))
    status = ctk.CTkLabel(dialog, text="", text_color=FG_DIM, font=FONT_SMALL, wraplength=500, justify="left")
    status.pack(side="bottom", anchor="w", padx=10)
    ctk.CTkLabel(
        dialog, text="No tracklist found. Paste track times and names, one per line\n(e.g. 0:00 Intro), or paste/read a screenshot. Leave empty to download as a single file.",
        text_color=FG, font=FONT_SMALL, justify="left", wraplength=500
    ).pack(side="top", anchor="w", padx=10, pady=(10, 4))
    box = ctk.CTkTextbox(dialog, fg_color=BG_ENTRY, text_color=FG, border_color=BORDER, border_width=1, font=FONT_SMALL)
    box.pack(side="top", fill="both", expand=True, padx=10, pady=4)
    result = {'data': None}

    def on_ok(event=None):
        text = box.get("1.0", "end").strip()
        if not text:
            dialog.destroy()
            return "break"
        parsed = tracklist_mod.parse_manual_text(text)
        if not parsed:
            status.configure(text="No lines with a time (m:ss or h:mm:ss) were found.")
            return "break"
        result['data'] = parsed
        dialog.destroy()
        return "break"

    def read_image(path):
        status.configure(text="Reading text from image...")
        dialog.update_idletasks()
        text, err = ocr_mod.image_to_text(path, engine=ocr_engine)
        if err:
            status.configure(text=err + " You can still paste the text.")
            return
        existing = box.get("1.0", "end").strip()
        box.delete("1.0", "end")
        box.insert("1.0", (existing + chr(10) if existing else "") + text)
        status.configure(text="Text read from image. Check and correct it, then click Use This Tracklist (Ctrl+Enter).")

    def on_image():
        if pick_image:
            path = pick_image()
        else:
            path = filedialog.askopenfilename(
                parent=dialog, title="Choose a screenshot of the tracklist",
                filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff"), ("All files", "*.*")])
        if path:
            read_image(path)

    def on_paste(event=None):
        """Ctrl+V: an image on the clipboard is OCR'd; text paste is left to the default."""
        path = clipboard_image()
        if not path:
            return None
        read_image(path)
        return "break"

    btn_ok = _btn_primary(btn_row, "Use This Tracklist", on_ok)
    btn_ok.pack(side="right", padx=(6, 0))
    btn_skip = _btn(btn_row, "Skip (single file)", dialog.destroy)
    btn_skip.pack(side="right", padx=(6, 0))
    btn_image = _btn(btn_row, "Read From Image...", on_image)
    btn_image.pack(side="left")

    dialog.bind("<Control-Return>", on_ok)
    box._textbox.bind("<Control-Return>", on_ok)
    box._textbox.bind("<Control-v>", on_paste)
    box._textbox.bind("<Control-V>", on_paste)
    return _Ui(dialog=dialog, box=box, status=status, result=result, min_size=min_size,
               btn_ok=btn_ok, btn_skip=btn_skip, btn_image=btn_image,
               on_ok=on_ok, on_image=on_image, on_paste=on_paste)


def build_confirm_dialog(parent, tracklist):
    """Build the confirm dialog; button row is reserved first so it is never clipped."""
    min_size = (480, 360)
    dialog = ctk.CTkToplevel(parent)
    _setup_dialog(dialog, "Confirm Tracklist", 560, 620, *min_size)

    btn_row = ctk.CTkFrame(dialog, fg_color=BG)
    btn_row.pack(side="bottom", fill="x", padx=10, pady=(4, 10))
    list_frame = ctk.CTkScrollableFrame(
        dialog, fg_color=BG_FRAME, border_color=BORDER, border_width=1,
        scrollbar_button_color=BORDER, scrollbar_button_hover_color=FG_DIM
    )
    list_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    entries = []
    for time, title in tracklist:
        row = ctk.CTkFrame(list_frame, fg_color=BG_FRAME)
        row.pack(fill="x", pady=2)

        t_entry = ctk.CTkEntry(row, width=80, fg_color=BG_ENTRY, text_color=FG, border_color=BORDER, font=FONT_SMALL)
        t_entry.insert(0, time)
        t_entry.pack(side="left", padx=5)

        n_entry = ctk.CTkEntry(row, fg_color=BG_ENTRY, text_color=FG, border_color=BORDER, font=FONT_SMALL)
        n_entry.insert(0, title)
        n_entry.pack(side="left", fill="x", expand=True, padx=5)

        entries.append((t_entry, n_entry))

    result = {'confirmed': False, 'data': []}

    def on_confirm(event=None):
        result['data'] = [(t.get(), n.get()) for t, n in entries]
        result['confirmed'] = True
        dialog.destroy()

    btn_confirm = _btn_primary(btn_row, "Confirm & Split", on_confirm)
    btn_confirm.pack(side="right", padx=(6, 0))
    _btn(btn_row, "Cancel", dialog.destroy).pack(side="right", padx=(6, 0))
    dialog.bind("<Control-Return>", on_confirm)
    return _Ui(dialog=dialog, list_frame=list_frame, entries=entries, result=result,
               min_size=min_size, btn_confirm=btn_confirm, on_confirm=on_confirm)


class YoutubeDLApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.configure(fg_color=BG)
        self.title("Weyland-Yutani Music Extractor")
        self.geometry("620x580")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # ── Header ───────────────────────────────────────────────────────────
        self.label_title = ctk.CTkLabel(
            self, text="Weyland-Yutani Music Extractor",
            font=FONT_TITLE, text_color=FG, fg_color=BG
        )
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 2))

        self.label_sub = ctk.CTkLabel(
            self, text="Building better music. One track at a time.",
            font=FONT_SUB, text_color=FG_DIM, fg_color=BG
        )
        self.label_sub.grid(row=1, column=0, padx=20, pady=(0, 12))

        # ── Auto-Split (top, default ON) ──────────────────────────────────────
        self.autosplit_var = ctk.BooleanVar(value=True)
        self.chk_autosplit = ctk.CTkCheckBox(
            self, text="Auto-split tracks by chapters / tracklist",
            variable=self.autosplit_var,
            text_color=FG, fg_color=FG, hover_color=FG_HOVER,
            border_color=FG_DIM, checkmark_color=BG, font=FONT_SMALL
        )
        self.chk_autosplit.grid(row=2, column=0, padx=24, pady=(0, 10), sticky="w")

        # ── URL Input ─────────────────────────────────────────────────────────
        self.frame_input = ctk.CTkFrame(self, fg_color=BG_FRAME, border_color=BORDER, border_width=1)
        self.frame_input.grid(row=3, column=0, padx=20, pady=6, sticky="ew")
        self.frame_input.grid_columnconfigure(0, weight=1)

        self.entry_url = ctk.CTkEntry(
            self.frame_input, placeholder_text="Paste YouTube URL here...",
            fg_color=BG_ENTRY, text_color=FG, placeholder_text_color=FG_DIM,
            border_color=BORDER, font=FONT_SMALL
        )
        self.entry_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_fetch = _btn(self.frame_input, "Fetch Formats", self.start_fetch_formats)
        self.btn_fetch.grid(row=0, column=1, padx=10, pady=10)

        # ── Format Options ────────────────────────────────────────────────────
        self.frame_options = ctk.CTkScrollableFrame(
            self, label_text="Formats",
            fg_color=BG_FRAME, border_color=BORDER, border_width=1,
            label_fg_color=BG_FRAME, label_text_color=FG_DIM,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=FG_DIM
        )
        self.frame_options.grid(row=4, column=0, padx=20, pady=6, sticky="nsew")

        # ── Download Button ───────────────────────────────────────────────────
        self.btn_download = _btn(self, "Download Selected", self.start_download, state="disabled", width=200)
        self.btn_download.grid(row=5, column=0, padx=20, pady=14)

        # ── Log ───────────────────────────────────────────────────────────────
        self.textbox_log = ctk.CTkTextbox(
            self, height=100,
            fg_color=BG_FRAME, text_color=FG_DIM,
            border_color=BORDER, border_width=1, font=FONT_SMALL
        )
        self.textbox_log.grid(row=6, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.textbox_log.insert("0.0", "> system ready.\n")

        self.formats = []
        self.selected_format = ctk.StringVar()
        self.video_info = None
        self.output_folder = os.getcwd()

    def log(self, message):
        self.textbox_log.insert("end", f"> {message}\n")
        self.textbox_log.see("end")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.log(f"output → {folder}")

    def start_fetch_formats(self):
        url = self.entry_url.get()
        if not url:
            self.log("enter a URL first.")
            return

        self.btn_fetch.configure(state="disabled")
        self.log(f"fetching: {url}")

        for widget in self.frame_options.winfo_children():
            widget.destroy()

        threading.Thread(target=self.fetch_info_thread, args=(url,), daemon=True).start()

    def fetch_info_thread(self, url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_info = info
                self.formats = info.get('formats', [])

            self.after(0, self.update_options_ui)
        except Exception as e:
            self.after(0, lambda: self.log(f"error: {e}"))
            self.after(0, lambda: self.btn_fetch.configure(state="normal"))

    def _section_label(self, text):
        ctk.CTkLabel(
            self.frame_options, text=text,
            text_color=FG_DIM, fg_color=BG_FRAME, font=FONT_SMALL
        ).pack(anchor="w", padx=10, pady=(10, 2))

    def update_options_ui(self):
        self.btn_fetch.configure(state="normal")
        self.btn_download.configure(state="normal")

        if self.video_info:
            self.log(f"found: {self.video_info.get('title', '?')}")

        # ── Audio (primary) ───────────────────────────────────────────────────
        self._section_label("── AUDIO ───────────────────────")
        _radio(self.frame_options, "High   · 320 kbps MP3", self.selected_format, "audio_high").pack(anchor="w", padx=18, pady=3)
        _radio(self.frame_options, "Medium · 128 kbps MP3", self.selected_format, "audio_medium").pack(anchor="w", padx=18, pady=3)
        _radio(self.frame_options, "Low    ·  64 kbps MP3", self.selected_format, "audio_low").pack(anchor="w", padx=18, pady=3)

        # ── Video (secondary) ─────────────────────────────────────────────────
        self._section_label("── VIDEO ───────────────────────")
        _radio(self.frame_options, "Best Video (auto)",      self.selected_format, "best").pack(anchor="w", padx=18, pady=3)
        _radio(self.frame_options, "1080p (if available)",  self.selected_format, "bestvideo[height<=1080]+bestaudio/best[height<=1080]").pack(anchor="w", padx=18, pady=3)
        _radio(self.frame_options, "720p  (if available)",  self.selected_format, "bestvideo[height<=720]+bestaudio/best[height<=720]").pack(anchor="w", padx=18, pady=3)

        self.selected_format.set("audio_high")

        # ── Output Folder ─────────────────────────────────────────────────────
        self._section_label("── OUTPUT ──────────────────────")
        _btn(self.frame_options, "Select Output Folder", self.select_output_folder).pack(anchor="w", padx=18, pady=(4, 10))

    # ── Tracklist Parsing ─────────────────────────────────────────────────────

    def parse_tracklist(self, info):
        d_matches = tracklist_mod.scan_text(info.get('description', ''))
        if len(d_matches) >= 2:
            return d_matches

        best = []
        for c in info.get('comments', []):
            if not isinstance(c, dict):
                continue
            matches = tracklist_mod.scan_text(c.get('text', ''))
            if len(matches) > len(best):
                best = matches

        return best if len(best) > len(d_matches) else d_matches

    def manual_tracklist_dialog(self):
        """Ask the user to paste a track list. Returns parsed list, or None to skip."""
        ui = build_manual_tracklist_dialog(self)
        ui.dialog.grab_set()
        ui.dialog.wait_window()
        return ui.result['data']

    def confirm_tracklist(self, tracklist):
        ui = build_confirm_dialog(self, tracklist)
        ui.dialog.wait_window()
        return ui.result

    # ── Splitting ─────────────────────────────────────────────────────────────

    def split_video(self, input_file, tracklist):
        self.log("splitting tracks...")
        if not tracklist:
            return

        ffmpeg_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_exe):
            ffmpeg_exe = 'ffmpeg'

        _, ext = os.path.splitext(input_file)

        for i, (start_time, title) in enumerate(tracklist):
            safe = "".join(c for c in title if c.isalpha() or c.isdigit() or c == ' ').rstrip()
            out_path = os.path.join(self.output_folder, f"{i+1:02d} - {safe}{ext}")
            cmd = [ffmpeg_exe, '-y', '-i', input_file, '-ss', start_time, '-c', 'copy']
            if i < len(tracklist) - 1:
                cmd.extend(['-to', tracklist[i+1][0]])
            cmd.append(out_path)
            self.log(f"export: {i+1:02d} - {safe}")
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            except Exception as e:
                self.log(f"split error: {e}")

        self.log("splitting complete.")

    # ── Download ──────────────────────────────────────────────────────────────

    def start_download(self):
        fmt = self.selected_format.get()
        url = self.entry_url.get()
        if not fmt:
            return

        tracklist_to_use = []
        if self.autosplit_var.get() and self.video_info:
            self.log("checking for tracklist...")
            tracklist = self.parse_tracklist(self.video_info)

            if len(tracklist) < 2:
                self.log("fetching comments...")
                self.update()
                try:
                    opts = {'getcomments': True, 'skip_download': True, 'quiet': True, 'noplaylist': True}
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info_c = ydl.extract_info(url, download=False)
                        tracklist = self.parse_tracklist(info_c)
                except Exception as e:
                    self.log(f"comment fetch failed: {e}")

            if not tracklist:
                self.log("no tracklist found automatically.")
                tracklist = self.manual_tracklist_dialog()
                if tracklist is None:
                    self.log("no tracklist — downloading as single file.")
                    tracklist = []

            if tracklist:
                res = self.confirm_tracklist(tracklist)
                if not res['confirmed']:
                    self.log("cancelled.")
                    return
                tracklist_to_use = res['data']

        self.btn_download.configure(state="disabled")
        self.btn_fetch.configure(state="disabled")
        threading.Thread(target=self.download_thread, args=(url, fmt, tracklist_to_use), daemon=True).start()

    def download_thread(self, url, fmt, tracklist=None):
        self.after(0, lambda: self.log("download starting..."))

        ffmpeg_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe')

        ydl_opts = {
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }
        if os.path.exists(ffmpeg_exe):
            ydl_opts['ffmpeg_location'] = ffmpeg_exe

        audio_quality = {
            'audio_high':   '320',
            'audio_medium': '128',
            'audio_low':    '64',
        }

        if fmt in audio_quality:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality[fmt],
            }]
        elif fmt == "best":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = fmt

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            if fmt in audio_quality:
                base, _ = os.path.splitext(filename)
                filename = base + ".mp3"

            self.after(0, lambda: self.log("download complete."))

            if tracklist:
                self.after(0, lambda: self.log("processing splits..."))
                self.split_video(filename, tracklist)

        except Exception as e:
            self.after(0, lambda: self.log(f"download error: {e}"))
            if "ffmpeg" in str(e).lower():
                self.after(0, lambda: self.log("ffmpeg missing — audio conversion failed."))

        self.after(0, lambda: self.btn_download.configure(state="normal"))
        self.after(0, lambda: self.btn_fetch.configure(state="normal"))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '?')
            self.after(0, lambda: self.label_title.configure(text=f"Weyland-Yutani Music Extractor  [{p}]"))
        elif d['status'] == 'finished':
            self.after(0, lambda: self.label_title.configure(text="Weyland-Yutani Music Extractor"))


if __name__ == "__main__":
    app = YoutubeDLApp()
    app.mainloop()
