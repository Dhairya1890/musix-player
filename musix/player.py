import subprocess
from pathlib import Path


def get_stream_url(query: str) -> tuple[str, str, str]:
    '''Returns (stream_url, title, youtube_id)'''

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "default_search": "ytsearch1",
    }

    import yt_dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = query if query.startswith(("http://", "https://")) else f"ytsearch1:{query}"
        info = ydl.extract_info(search_query, download=False)

        entry = info["entries"][0] if "entries" in info else info

        if "requested_formats" in entry:
            url = entry["requested_formats"][0]["url"]
        else:
            formats = entry["formats"]
            audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            if not audio_formats:
                # fall back to any format that carries audio (e.g. muxed streams)
                audio_formats = [f for f in formats if f.get("acodec") != "none"]
            if not audio_formats:
                raise ValueError(f"No playable audio format found for: {entry['title']}")
            best = max(audio_formats, key=lambda f: f.get("abr") or 0)
            url = best["url"]

        return url, entry["title"], entry["id"]


def stream_song(url: str):
    '''Stream audio using mpv.'''
    cmd = [
        "mpv",
        "--video=no",
        "--terminal=yes",
        "--msg-level=all=error,statusline=status",
        url,
    ]
    subprocess.run(cmd)


def download_song(youtube_id: str, output_dir: str):
    '''Download audio to output_dir using yt-dlp.'''
    ydl_opts = {
        "format": "bestaudio",
        "no_warnings": True,
        "noplaylist": True,
        "outtmpl": str(Path(output_dir) / "%(title)s.%(ext)s"),
    }
    import yt_dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f"https://www.youtube.com/watch?v={youtube_id}"])


def search_songs(query: str) -> list[dict]:
    '''Fetch top 5 results from YouTube and return as a list of dicts.'''

    ydl_opts = {
        'quiet': True,
        "no_warnings": True,
        "noplaylist": True,
        "default_search": "ytsearch5",
    }

    import yt_dlp
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = query if query.startswith(("http://", "https://")) else f"ytsearch5:{query}"
        info = ydl.extract_info(search_query, download=False)
        return [
            {
                "title": entry["title"],
                "youtube_id": entry["id"],
                "duration": entry.get("duration", 0),
                "channel": entry.get("channel", "Unknown"),
            }
            for entry in info["entries"]
        ]
