import yt_dlp
import subprocess

def get_stream_url(query : str) -> tuple[str,str,str]:
    '''Inputs : format, mode of stdout, playlist preference, and searching site'''

    ydl_opts = {
        "format" : "bestaudio",
        "quiet" : True,
        "no_warnings" : True,
        "noplaylist" : True,
        "default_search" : "ytsearch1",
        "writesubtitles" : True,
        "writeautomaticsub" : True,
        "subtitleslangs" : ["en", "HI"]
        # "quiet" : True,
        # "noplaylist" : True,
        # "default_search" : "ytsearch1", 
        # "no_warnings" : True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = query if query.startswith(("http://", "https://")) else f"ytsearch1:{query}"
        info = ydl.extract_info(search_query, download=False)

        if "entries" in info:
            entry = info["entries"][0]
        else:
            entry = info

        # entries = list(info["entries"])
        # entry = entries[0]

        sub_url = None
        subs = entry.get("subtitles") or entry.get("automatic_captions") or {}

        if "en" in subs:
            for sub in subs["en"]:
                if sub.get("ext") == "vtt":
                    sub_url = sub["url"]
                    break

        if "requested_formats" in entry:
            url = entry["requested_formats"][0]["url"]
        else:
            formats = entry["formats"]
            audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            best = max(audio_formats, key=lambda f : f.get("abr") or 0)
            url = best["url"]
        return url, entry["title"], sub_url
    

def stream_song(url : str, sub_url : str = None):
    '''stream audio using mpv.'''
    cmd = [
        "mpv",
        "--video=no",
        "--terminal=yes",
        "--msg-level=all=error,statusline=status"
    ]
    
    if sub_url:
        cmd.append(f"--sub-file={sub_url}")
        
    cmd.append(url)

    subprocess.run(cmd)

def search_songs(query : str) -> list[dict]:
    '''yt-dlp fetches top 5 results
       display as a list
       user selects a number
    '''

    ydl_opts = {
        'quiet' : True,
        "no_warnings" : True,
        "noplaylist" : True,
        "default_search" : "ytsearch5"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_query = query if query.startswith(("http://", "https://")) else f"ytsearch5:{query}"
        info = ydl.extract_info(search_query, download=False)
        entries = list(info["entries"])
        result = []
        for entry in entries:
            result.append({
                "title" : entry["title"],
                "youtube_id" : entry["id"],
                "duration" : entry.get("duration", 0),
                "channel" : entry.get("channel", "Unknown"),
            })

        return result