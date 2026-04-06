import yt_dlp
import subprocess

def get_stream_url(query : str) -> tuple[str,str]:
    '''Inputs : format, mode of stdout, playlist preference, and searching site'''

    ydl_opts = {
        "format" : "bestaudio",
        "quiet" : True,
        "no_warnings" : True,
        "noplaylist" : True,
        "default_search" : "ytsearch1",
        # "quiet" : True,
        # "noplaylist" : True,
        # "default_search" : "ytsearch1", 
        # "no_warnings" : True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        if "entires" in info:
            entry = list(info["entries"][0])
        else:
            entry = info

        # entries = list(info["entries"])
        # entry = entries[0]

        if "requested_formats" in entry:
            url = entry["requested_formats"][0]["url"]
        else:
            formats = entry["formats"]
            audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none"]
            best = max(audio_formats, key=lambda f : f.get("abr") or 0)
            url = best["url"]
        return url, entry["title"]
    

def stream_song(url : str):
    '''stream audio using mpv.'''
    subprocess.run([
        "ffplay",
        "-nodisp",          
        "-autoexit", 
        "-loglevel", "quiet",        
        url
    ])

    subprocess.run(
        ["mpv", "--no-audio", "--really-quiet", url]
    )

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
        info = ydl.extract_info(query, download=False)
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