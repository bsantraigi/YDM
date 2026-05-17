# coding: utf-8
# Description: Advanced Youtube Playlist Downloader with UI
# Usage: python3 yListerFull.py

import re
import sys
import yt_dlp
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.filedialog as tkFileDialog
import os
import subprocess
from threading import Thread, Lock
import queue as Queue
import time
import datetime
import shutil

# FFmpeg path - auto detect from system PATH (where winget installs it)
FFMPEG_PATH = shutil.which("ffmpeg") or "ffmpeg"

class YoutubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Youtube Playlist Downloader Pro")
        self.root.geometry("900x650") 
        self.root.resizable(True, True)

        # Variables
        self.playlist_url = StringVar()
        self.save_path = StringVar(value=os.getcwd())
        self.download_mode = StringVar(value="hq")
        self.resolution_var = StringVar(value="1080p (HD)")
        self.auto_start = BooleanVar(value=True)
        self.is_parsing = False
        self.is_downloading = False
        self.is_paused = False # Pause flag
        
        # Data
        self.videos_dict = {} # Map iid -> video_data
        self.parse_queue = Queue.Queue()
        self.download_queue = Queue.Queue()
        self.completed_count = 0
        self.total_count = 0
        self.total_downloading = 0
        
        # Locks
        self.ui_lock = Lock()

        self.setup_ui()

    def setup_ui(self):
        # Main Container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=BOTH, expand=True)

        # --- Top Section: Inputs ---
        input_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        input_frame.pack(fill=X, pady=(0, 10))

        # URL Input
        ttk.Label(input_frame, text="Playlist/Video URL:").grid(row=0, column=0, sticky=W, padx=5)
        ttk.Entry(input_frame, textvariable=self.playlist_url, width=60).grid(row=0, column=1, padx=5, sticky=EW)
        ttk.Button(input_frame, text="Parse", command=self.start_parsing).grid(row=0, column=2, padx=5)

        # Save Path
        ttk.Label(input_frame, text="Save Path:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.save_path, width=60).grid(row=1, column=1, padx=5, sticky=EW)
        ttk.Button(input_frame, text="Browse", command=self.browse_folder).grid(row=1, column=2, padx=5)

        # Options
        opts_frame = ttk.Frame(input_frame)
        opts_frame.grid(row=2, column=0, columnspan=3, sticky=W, pady=5)
        
        ttk.Label(opts_frame, text="Quality:").pack(side=LEFT, padx=5)
        res_combo = ttk.Combobox(opts_frame, textvariable=self.resolution_var, state="readonly", width=15)
        res_combo['values'] = ("Best (4K/8K)", "1440p (2K)", "1080p (HD)", "720p (HD)", "480p")
        res_combo.pack(side=LEFT, padx=5)

        ttk.Checkbutton(opts_frame, text="Auto-Start Download", variable=self.auto_start).pack(side=LEFT, padx=15)

        input_frame.columnconfigure(1, weight=1)

        # --- Middle Section: List View ---
        list_frame = ttk.LabelFrame(main_frame, text="Video Queue", padding="5")
        list_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Treeview
        columns = ("title", "status", "size", "progress", "speed_eta")
        self.tree = ttk.Treeview(list_frame, columns=columns, selectmode="extended", yscrollcommand=scrollbar.set)
        
        self.tree.heading("#0", text="", anchor=CENTER) # Checkbox column
        self.tree.column("#0", width=40, stretch=False, anchor=CENTER)
        
        self.tree.heading("title", text="Title", anchor=W)
        self.tree.column("title", width=300, minwidth=200)
        
        self.tree.heading("status", text="Status", anchor=W)
        self.tree.column("status", width=120, minwidth=100)
        
        self.tree.heading("size", text="Size", anchor=E)
        self.tree.column("size", width=80, minwidth=60)
        
        self.tree.heading("progress", text="Progress", anchor=W)
        self.tree.column("progress", width=150, minwidth=100) # Text progress bar

        self.tree.heading("speed_eta", text="Speed / ETA", anchor=W)
        self.tree.column("speed_eta", width=150, minwidth=100)

        self.tree.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Bindings if needed (e.g., right click)
        
        # --- Bottom Section: Status & Controls ---
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=X)

        self.status_label = ttk.Label(status_frame, text="Ready.")
        self.status_label.pack(side=LEFT)

        controls_frame = ttk.Frame(status_frame)
        controls_frame.pack(side=RIGHT)

        ttk.Button(controls_frame, text="Start Download", command=self.start_download_manager).pack(side=LEFT, padx=2)
        self.pause_btn = ttk.Button(controls_frame, text="Pause Queue", command=self.toggle_pause)
        self.pause_btn.pack(side=LEFT, padx=2)
        ttk.Button(controls_frame, text="Retry Failed", command=self.retry_failed).pack(side=LEFT, padx=2)
        ttk.Button(controls_frame, text="Clear Finished", command=self.clear_finished).pack(side=LEFT, padx=2)

    def browse_folder(self):
        d = tkFileDialog.askdirectory()
        if d: self.save_path.set(d)

    def add_video_to_list(self, video_data):
        # Insert into Treeview
        # Using checkmark chars for the #0 column to simulate checkbox state (simplified)
        iid = self.tree.insert("", END, text="☑", values=(
            video_data['title'],
            "Queued",
            "-",
            "Waiting...",
            "-"
        ))
        video_data['iid'] = iid
        video_data['state'] = 'queued' # queued, parsing, downloading, completed, error, skipped
        self.videos_dict[iid] = video_data
        
        # If auto-start is allowed, we can signal the downloader immediately
        # But we use the manager loop for that

    def start_parsing(self):
        url = self.playlist_url.get()
        if not url: return

        self.is_parsing = True
        self.status_label.config(text="Parsing playlist...")
        
        # Clear previous if new parse? Or append? appending is safer
        # self.tree.delete(*self.tree.get_children())
        
        t = Thread(target=self.run_crawler, args=(url,))
        t.daemon = True
        t.start()
        
        if self.auto_start.get():
            self.start_download_manager()

    def run_crawler(self, url):
        ydl_opts = {
            'quiet': True,
            'extract_flat': True, # Fast extraction, get metadata later or now? 
            # Flat extract gives minimal info. For "Title" we might need a bit more, 
            # but deep extract is slow. Let's do flat then `extract_info` per video in downloader?
            # Or lazy load.
            # Ideally we want titles immediately. `extract_flat` usually gives titles.
            'no_warnings': True,
            'ignoreerrors': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # If single video, this might behave differently with extract_flat
                # simple check:
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    # It's a playlist
                    for entry in info['entries']:
                        if not entry: continue
                        self.process_parsed_entry(entry)
                else:
                    # Single video
                    self.process_parsed_entry(info)
                    
        except Exception as e:
            err_msg = str(e)
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            err_msg = ansi_escape.sub('', err_msg)
            print(f"Parse Error: {err_msg}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Parse error: {err_msg}"))
            
        self.is_parsing = False
        self.root.after(0, lambda: self.status_label.config(text="Parsing complete."))

    def process_parsed_entry(self, entry):
        title = entry.get('title', 'Unknown')
        video_id = entry.get('id')
        url = entry.get('url') or entry.get('webpage_url')
        if not url:
            url = f"https://www.youtube.com/watch?v={video_id}"
            
        video_data = {
            'title': title,
            'url': url,
            'filename': re.sub(r'[<>:\"\/\\|\?\*]+', "_", title)
        }
        
        # Thread-safe UI update
        self.root.after(0, lambda: self.add_video_to_list(video_data))


    def start_download_manager(self):
        if self.is_downloading: return
        self.is_downloading = True
        
        t = Thread(target=self.download_manager_loop)
        t.daemon = True
        t.start()

    def download_manager_loop(self):
        # Continuously look for 'queued' items in treeview and start download
        
        while True:
            # Check Pause
            if self.is_paused:
                time.sleep(1)
                continue

            # Find next queued item
            next_iid = None
            
            # Ask main thread for next queued item
            q = Queue.Queue()
            self.root.after(0, lambda: q.put(self.get_next_queued_iid()))
            next_iid = q.get()
            
            if next_iid:
                # Download it
                self.process_video(next_iid)
            else:
                # If parsing is done and no more files, stop
                if not self.is_parsing:
                    time.sleep(1) # Wait a bit to be sure
                    # Check again
                    self.root.after(0, lambda: q.put(self.get_next_queued_iid()))
                    if not q.get():
                        break
                
                time.sleep(1)

        self.is_downloading = False
        self.root.after(0, lambda: self.status_label.config(text="All active downloads complete."))

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_btn.config(text="Resume Queue")
            self.status_label.config(text="Queue Paused")
        else:
            self.pause_btn.config(text="Pause Queue")
            self.status_label.config(text="Resuming...")
            
            # Re-queue paused items
            for iid in self.tree.get_children():
                status = self.tree.item(iid)['values'][1]
                if status == "Paused":
                    self.update_row(iid, status="Queued", speed_eta="-")


    def retry_failed(self):
        # Find all "Error" or "Skipped" and set to Queued
        reset_count = 0
        for iid in self.tree.get_children():
            status = self.tree.item(iid)['values'][1]
            if status in ["Error", "Skipped", "Cancelled"]:
                self.update_row(iid, status="Queued", progress="Waiting...", speed_eta="-")
                self.tree.item(iid, text="☑") # Re-check it
                reset_count += 1
        
        if reset_count > 0:
            self.status_label.config(text=f"Reset {reset_count} items. Starting download...")
            self.start_download_manager()
        else:
            messagebox.showinfo("Info", "No failed items to retry.")

    def get_next_queued_iid(self):
        # Run on main thread
        for iid in self.tree.get_children():
            # Check if checked (text="☑") and status="Queued"
            item = self.tree.item(iid)
            if item['text'] == "☑" and item['values'][1] == "Queued":
                return iid
        return None

    def process_video(self, iid):
        # Update status
        self.update_row(iid, status="Downloading...", progress="Starting...")
        
        video_data = self.videos_dict[iid]
        url = video_data['url']
        filename = video_data['filename']
        output_path = self.save_path.get()
        
        # Prepare options
        res_str = self.resolution_var.get()
        height_map = {
            "Best (4K/8K)": "Best",
            "1440p (2K)": "1440",
            "1080p (HD)": "1080",
            "720p (HD)": "720",
            "480p": "480"
        }
        max_height = height_map.get(res_str, "Best")
        
        if max_height and max_height != "Best":
            format_str = f'bestvideo[height<={max_height}]+bestaudio/best[height<={max_height}]/best'
        else:
            format_str = 'bestvideo+bestaudio/best'

        safe_filename = filename # Extension handled by yt-dlp
        output_template = os.path.join(output_path, f"{safe_filename}.%(ext)s")

        # ANSI Escape code stripper
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

        def progress_hook(d):
            # Immediate Pause Check
            if self.is_paused:
                raise Exception("_PAUSED_BY_USER_")

            if d['status'] == 'downloading':
                try:
                    p = d.get('_percent_str', '0%').strip()
                    s = d.get('_speed_str', '0B/s').strip()
                    eta = d.get('_eta_str', '?:??').strip()
                    size = d.get('_total_bytes_str') or d.get('_total_bytes_estimate_str') or "?"
                    
                    # Clean ANSI codes
                    p = ansi_escape.sub('', p)
                    s = ansi_escape.sub('', s)
                    eta = ansi_escape.sub('', eta)
                    size = ansi_escape.sub('', size)
                    
                    self.root.after(0, lambda: self.update_row(
                        iid=iid,
                        status="Downloading",
                        size=size,
                        progress=p,
                        speed_eta=f"{s} - {eta}"
                    ))
                except Exception as ex:
                    pass
            elif d['status'] == 'finished':
                self.root.after(0, lambda: self.update_row(iid, status="Processing...", progress="100%"))

        ydl_opts = {
            'format': format_str,
            'merge_output_format': 'mp4',
            'outtmpl': output_template,
            'ffmpeg_location': FFMPEG_PATH,
            'progress_hooks': [progress_hook],
            'no_warnings': True,
            'ignoreerrors': False, 
            'quiet': True, 
            'format_sort': ['res', 'ext:mp4:m4a'],
            'ignore_config': True,
            'cookiesfrombrowser': None,
            
            # Fail fast settings
            'socket_timeout': 10,
            'retries': 3,
            'fragment_retries': 3,
            
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            },
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, lambda: self.update_row(iid, status="Completed", progress="100%", speed_eta="Done"))
        except Exception as e:
            err_msg = str(e)
            # Remove ANSI color codes that might come from yt-dlp error string
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            err_msg = ansi_escape.sub('', err_msg)
            
            if "_PAUSED_BY_USER_" in err_msg:
                self.root.after(0, lambda: self.update_row(iid, status="Paused", speed_eta="Paused"))
            else:
                self.root.after(0, lambda: self.update_row(iid, status="Error", speed_eta=err_msg))


    def update_row(self, iid, status=None, size=None, progress=None, speed_eta=None):
        try:
            current_values = self.tree.item(iid)['values']
            # values: title, status, size, progress, speed_eta
            new_values = list(current_values)
            
            if status: new_values[1] = status
            if size: new_values[2] = size
            if progress: new_values[3] = progress
            if speed_eta: new_values[4] = speed_eta
            
            self.tree.item(iid, values=new_values)
            
            # Auto-scroll to active
            # self.tree.see(iid) 
        except Exception:
            pass # Item might be deleted

    def clear_finished(self):
        for iid in self.tree.get_children():
            values = self.tree.item(iid)['values']
            if values[1] == "Completed":
                self.tree.delete(iid)
                
    # Checkbox logic simulation
    def on_tree_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "tree": # The icon/text column
            iid = self.tree.identify_row(event.y)
            if iid:
                curr = self.tree.item(iid)['text']
                # Toggle
                new_text = "☐" if curr == "☑" else "☑"
                self.tree.item(iid, text=new_text)

if __name__ == "__main__":
    root = Tk()
    app = YoutubeDownloaderApp(root)
    # Bind toggle check
    app.tree.bind("<Button-1>", app.on_tree_click)
    
    root.mainloop()
