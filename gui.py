import customtkinter as ctk
import yt_dlp
import threading
import os
import sys
import re
import subprocess
from tkinter import filedialog


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
        self.output_folder = os.getcwd() # Default to current directory
        self.autosplit_var = ctk.BooleanVar(value=False)

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.log(f"Output folder set to: {folder}")

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

        # Auto Split Option
        ctk.CTkCheckBox(self.frame_options, text="Auto Split by Chapters/Tracklist", variable=self.autosplit_var).pack(anchor="w", padx=10, pady=10)
        
        # Output Folder Button
        ctk.CTkButton(self.frame_options, text="Select Output Folder", command=self.select_output_folder).pack(anchor="w", padx=10, pady=5)

    def parse_tracklist(self, info):
        # Helper to parse lines
        def scan_text(text):
            if not text: return []
            lines = text.split('\n')
            found = []
            for line in lines:
                line = line.strip()
                match = None
                
                # Format 1: Time Title (e.g. 00:00 Intro)
                m1 = re.search(r'^(?P<time>(?:\d{1,2}:)?\d{1,2}:\d{2})\s+(?P<title>.+)$', line)
                
                # Format 2: Title Time (e.g. Intro 00:00)
                m2 = re.search(r'^(?P<title>.+?)\s+(?P<time>(?:\d{1,2}:)?\d{1,2}:\d{2})$', line)
                
                if m1:
                    match = m1
                elif m2:
                    match = m2
                    
                if match:
                    t = match.group('time')
                    if len(t.split(':')) == 2: t = "00:" + t # Normalize to HH:MM:SS
                    
                    # Clean title
                    title = match.group('title').strip()
                    # Remove trailing punctuation often found in descriptions (like " - ")
                    title = re.sub(r'^[-\s]+|[-\s]+$', '', title)
                    
                    found.append((t, title))
            return found

        # 1. Check description
        d_matches = scan_text(info.get('description', ''))
        if len(d_matches) >= 2: # Heuristic: if we find at least 2 tracks
             return d_matches

        # 2. Check comments
        comments = info.get('comments', [])
        # Find comment with most timestamps
        best_matches = []
        for c in comments:
             if not isinstance(c, dict): continue
             text = c.get('text', '')
             matches = scan_text(text)
             if len(matches) > len(best_matches):
                 best_matches = matches
        
        if len(best_matches) > len(d_matches):
            return best_matches
            
        return d_matches

    def confirm_tracklist(self, tracklist):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Tracklist")
        dialog.geometry("500x600")
        
        c_frame = ctk.CTkScrollableFrame(dialog)
        c_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        entries = []
        
        for i, (time, title) in enumerate(tracklist):
            row = ctk.CTkFrame(c_frame)
            row.pack(fill="x", pady=2)
            
            t_entry = ctk.CTkEntry(row, width=80)
            t_entry.insert(0, time)
            t_entry.pack(side="left", padx=5)
            
            n_entry = ctk.CTkEntry(row)
            n_entry.insert(0, title)
            n_entry.pack(side="left", fill="x", expand=True, padx=5)
            
            entries.append((t_entry, n_entry))
            
        result = {'confirmed': False, 'data': []}
        
        def on_confirm():
            new_tracklist = []
            for t_entry, n_entry in entries:
                new_tracklist.append((t_entry.get(), n_entry.get()))
            result['data'] = new_tracklist
            result['confirmed'] = True
            dialog.destroy()
            
        def on_cancel():
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Confirm & Split", command=on_confirm).pack(pady=10)
        ctk.CTkButton(dialog, text="Cancel Download", command=on_cancel, fg_color="red").pack(pady=5)
        
        dialog.wait_window()
        return result

    def split_video(self, input_file, tracklist):
        self.log("Starting video split...")
        if not tracklist:
            return

        # Ensure ffmpeg is found
        ffmpeg_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_exe):
            # Try system ffmpeg
            ffmpeg_exe = 'ffmpeg'
            
        base, ext = os.path.splitext(input_file)
        
        def get_seconds(time_str):
            parts = list(map(int, time_str.split(':')))
            if len(parts) == 3:
                return parts[0]*3600 + parts[1]*60 + parts[2]
            return parts[0]*60 + parts[1]

        for i, (start_time, title) in enumerate(tracklist):
            safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            output_name = f"{i+1:02d} - {safe_title}{ext}"
            output_path = os.path.join(self.output_folder, output_name)
            
            # Determine duration/end
            cmd = [ffmpeg_exe, '-y', '-i', input_file, '-ss', start_time, '-c', 'copy']
            
            if i < len(tracklist) - 1:
                next_start = tracklist[i+1][0]
                cmd.extend(['-to', next_start])
            
            cmd.append(output_path)
            
            self.log(f"Exporting: {output_name}")
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                self.log(f"Error splitting {output_name}: {e}")

        self.log("Splitting complete.")

    def start_download(self):
        fmt = self.selected_format.get()
        url = self.entry_url.get()
        
        if not fmt:
            return

        # Check for Auto Split
        tracklist_to_use = []
        if self.autosplit_var.get() and self.video_info:
            self.log("Checking for tracklist...")
            tracklist = self.parse_tracklist(self.video_info)
            
            # If nothing good found, try fetching comments explicitly
            if len(tracklist) < 2:
                 self.log("Fetching comments to search for tracklist...")
                 self.after(0, lambda: self.update()) # Process events to show log
                 try:
                     opts = {'getcomments': True, 'skip_download': True, 'quiet': True, 'noplaylist': True}
                     with yt_dlp.YoutubeDL(opts) as ydl_c:
                         info_c = ydl_c.extract_info(url, download=False)
                         tracklist = self.parse_tracklist(info_c)
                 except Exception as e:
                     self.log(f"Comment fetch failed: {e}")

            if not tracklist:
                self.log("No tracklist found.")
                # Proceed? or ask? For now just proceed without splitting 
                # or better -> ask user to manual entry? 
                # Let's just notify and continue download only
                # But user expects auto split. 
                pass 
            else:
                res = self.confirm_tracklist(tracklist)
                if not res['confirmed']:
                    self.log("Download check cancelled by user.")
                    return
                tracklist_to_use = res['data']

        self.btn_download.configure(state="disabled")
        self.btn_fetch.configure(state="disabled")
        
        threading.Thread(target=self.download_thread, args=(url, fmt, tracklist_to_use)).start()

    def download_thread(self, url, fmt, tracklist=None):
        self.after(0, lambda: self.log("Starting download..."))
        
        # Locate local ffmpeg
        ffmpeg_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg.exe')
        
        ydl_opts = {
            'outtmpl': os.path.join(self.output_folder, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
        }
        
        if os.path.exists(ffmpeg_exe):
            ydl_opts['ffmpeg_location'] = ffmpeg_exe
        
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
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                # Fix filename for audio conversion
                if fmt == "audio_best":
                    base, _ = os.path.splitext(filename)
                    filename = base + ".mp3"
            
            self.after(0, lambda: self.log("Download complete!"))
            
            if tracklist:
                self.after(0, lambda: self.log("Processing splits..."))
                self.split_video(filename, tracklist)
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
