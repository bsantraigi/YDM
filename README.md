# YDM Pro (High-Performance YouTube Playlist Downloader)

**YDM Pro** is a robust, threaded downloader built for power users. It moves beyond simple scripts to offer a full dashboard for managing YouTube playlist downloads with support for 4K/8K quality, concurrent downloading, and pause/resume capabilities.

## 🚀 Key Features

*   **📺 High Quality Support**: Download videos in **4K, 2K, 1080p, 720p**, or 480p.
    *   *Automatically merges best video+audio streams using FFmpeg.*
*   **⚡ Concurrent Parsing & Downloading**: "Stream Parsing" engine lets you start downloading videos the moment they are found, without waiting for the whole playlist to parse.
*   **📋 Advanced Queue Management**:
    *   **Dashboard View**: See real-time status, size, progress, speed, and ETA for every video in a scrollable table.
    *   **Pause/Resume**: Immediately pause active downloads (network cut? no problem) and resume exactly where you left off.
    *   **Retry Failed**: One-click retry for any videos that failed due to network errors.
    *   **Selection**: Check/Uncheck specific videos to skip ones you don't need.
*   **🔗 Universal Support**: Works with Playlist URLs and Single Video URLs.

## 🛠️ Requirements

*   **Python 3.8+**
*   **FFmpeg** (Required for 1080p+ merging):
    *   Download from [ffmpeg.org](https://ffmpeg.org/download.html).
    *   The app is pre-configured to look in `C:\ffmpeg-...\bin`, or just add it to your System PATH.
*   **Python Modules**:
    ```bash
    pip install yt-dlp
    ```
    *Note: `tkinter` is usually included with Python.*

## 📦 Installation & Usage

1.  **Clone/Download** this repository.
2.  **Install dependencies** (see above).
3.  **Run the application**:
    ```bash
    python yListerFull.py
    ```

### How to Use
1.  **Paste URL**: Enter a YouTube Playlist or Video URL.
2.  **Select Quality**: Choose your target resolution (e.g., "1080p (HD)").
3.  **Pars/Start**:
    *   Click **Parse** to load the video list.
    *   Check **Auto-Start Download** to begin immediately.
4.  **Manage**:
    *   Use the [☑] checkboxes to skip videos.
    *   Use **Pause Queue** / **Resume Queue** to control bandwidth.
    *   Use **Retry Failed** if your internet drops.

## 📸 Screenshots

*(Add your screenshot here)*

## ⚠️ Note on IDM
This version supersedes the old IDM-based tool. `yt-dlp` + FFmpeg is superior because it can download separate video/audio streams (Dash) and merge them, allowing for **1080p/4K** downloads which IDM often cannot handle smoothly for YouTube.

## 🤝 Contributors
*   Original Author: [bsantraigi](https://github.com/bsantraigi)
*   Current Maintained Version: **YDM Pro**
