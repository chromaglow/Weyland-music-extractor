import customtkinter as ctk
import yt_dlp
import threading
import os
import sys

# Configuration
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class YoutubeDLApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Youtube-DL GUI")
        self.geometry("600x500")

        # Grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Log area expands

        # Title
        self.label_title = ctk.CTkLabel(self, text="Youtube Downloader", font=("Roboto", 24))
        self.label_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Input Area
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_input.grid_columnconfigure(0, weight=1)

        self.entry_url = ctk.CTkEntry(self.frame_input, placeholder_text="Paste YouTube URL here...")
        self.entry_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_fetch = ctk.CTkButton(self.frame_input, text="Fetch Formats", command=self.start_fetch_formats)
        self.btn_fetch.grid(row=0, column=1, padx=10, pady=10)

        # Options Area (Hidden initially)
        self.frame_options = ctk.CTkScrollableFrame(self, label_text="Formats")
        self.frame_options.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        # Download Button (Hidden initially)
        self.btn_download = ctk.CTkButton(self, text="Download Selected", command=self.start_download, state="disabled")
        self.btn_download.grid(row=3, column=0, padx=20, pady=20)

        # Status Log
        self.textbox_log = ctk.CTkTextbox(self, height=100)
        self.textbox_log.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.textbox_log.insert("0.0", "Ready.\n")

        self.formats = []
        self.selected_format = ctk.StringVar()
        self.video_info = None

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def start_fetch_formats(self):
        url = self.entry_url.get()
        if not url:
            self.log("Please enter a URL.")
            return
        
        self.btn_fetch.configure(state="disabled")
        self.log(f"Fetching info for: {url}")
        
        # Clear previous options
        for widget in self.frame_options.winfo_children():
            widget.destroy()

        threading.Thread(target=self.fetch_info_thread, args=(url,)).start()

    def fetch_info_thread(self, url):
        try:
            ydl_opts = {'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                self.video_info = info
                self.formats = info.get('formats', [])
                
                # Filter/Process formats to show relevant ones
                # We want: Best Video+Audio, 1080p, 720p, etc., and Best Audio
                
                # Create radio buttons for simplified options
                self.title_options = [
                    ("Best Video + Audio (Auto)", "best"),
                    ("Best Audio Only (MP3/M4A)", "bestaudio/best")
                ]
                
                # Add specific video resolutions if available
                # This is a basic filter, can be expanded
                seen_res = set()
                for f in self.formats:
                    h = f.get('height')
                    if h and h >= 360 and f.get('ext') == 'mp4':
                         if h not in seen_res:
                            seen_res.add(h)
                            
                sorted_res = sorted(list(seen_res), reverse=True)
                for res in sorted_res:
                    self.title_options.append((f"Video {res}p (MP4)", f"bestvideo[height<={res}]+bestaudio/best[height<={res}]"))

            # Update UI in main thread
            self.after(0, self.update_options_ui)

        except Exception as e:
            self.after(0, lambda: self.log(f"Error: {str(e)}"))
            self.after(0, lambda: self.btn_fetch.configure(state="normal"))

    def update_options_ui(self):
        self.btn_fetch.configure(state="normal")
        self.btn_download.configure(state="normal")
        
        if self.video_info:
            title = self.video_info.get('title', 'Unknown Title')
            self.log(f"Found: {title}")
        
        # Add "Best Audio" specifically requested
        ctk.CTkRadioButton(self.frame_options, text="Best Audio (High Quality)", variable=self.selected_format, value="audio_best").pack(anchor="w", padx=10, pady=5)
        
        # Add other options
        ctk.CTkRadioButton(self.frame_options, text="Best Video (Auto)", variable=self.selected_format, value="best").pack(anchor="w", padx=10, pady=5)
        
        # Add explicit resolutions
        # Filter raw formats is complex, let's just offer safe generic format strings for yt-dlp
        ctk.CTkRadioButton(self.frame_options, text="1080p (if available)", variable=self.selected_format, value="bestvideo[height<=1080]+bestaudio/best[height<=1080]").pack(anchor="w", padx=10, pady=5)
        ctk.CTkRadioButton(self.frame_options, text="720p (if available)", variable=self.selected_format, value="bestvideo[height<=720]+bestaudio/best[height<=720]").pack(anchor="w", padx=10, pady=5)

        self.selected_format.set("best") # Default

    def start_download(self):
        fmt = self.selected_format.get()
        url = self.entry_url.get()
        
        if not fmt:
            return

        self.btn_download.configure(state="disabled")
        self.btn_fetch.configure(state="disabled")
        
        threading.Thread(target=self.download_thread, args=(url, fmt)).start()

    def download_thread(self, url, fmt):
        self.after(0, lambda: self.log("Starting download..."))
        
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [self.progress_hook],
        }
        
        if fmt == "audio_best":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        elif fmt == "best":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            ydl_opts['format'] = fmt

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.log("Download complete!"))
        except Exception as e:
            self.after(0, lambda: self.log(f"Download Error: {str(e)}"))
            if "ffmpeg" in str(e).lower():
                 self.after(0, lambda: self.log("IMPORTANT: FFmpeg is missing. Audio conversion or merging failed."))
        
        self.after(0, lambda: self.btn_download.configure(state="normal"))
        self.after(0, lambda: self.btn_fetch.configure(state="normal"))

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', 'N/A')
            self.after(0, lambda: self.label_title.configure(text=f"Downloading: {p}"))
        elif d['status'] == 'finished':
            self.after(0, lambda: self.label_title.configure(text="Youtube Downloader"))

if __name__ == "__main__":
    app = YoutubeDLApp()
    app.mainloop()
