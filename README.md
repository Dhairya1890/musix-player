# Musix CLI Player 🎵

A lightweight, terminal-based music player powered by `yt-dlp` and `mpv`. Search for your favorite songs, play them instantly, and build local playlists right inside your terminal!

## Prerequisites
You must have `mpv` installed on your system. 
- **Linux:** `sudo apt install mpv`
- **Mac:** `brew install mpv`
- **Windows:** `scoop install mpv`

## Installation
You can install Musix directly from PyPI using pip:
```bash
pip install musix-cli-player
```

## Quick Start
Once installed, just type the global command `musix` to launch the helper, or use one of the commands below:

- **Play a song instantly:** `musix play "song name"`
- **Search and pick a song:** `musix search "artist name"`
- **Create a playlist:** `musix playlist "My Playlist"`
- **Add a song to playlist:** `musix add-song "song name" "My Playlist"`
- **Play a playlist:** `musix play-playlist "My Playlist"`

## Controls
During playback, the terminal is fully interactive:
- `p` or `Space`: Play / Pause
- `q`: Quit current song / Skip to next in playlist
- `9` / `0`: Decrease / Increase Volume
