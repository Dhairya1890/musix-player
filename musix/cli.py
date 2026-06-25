import shutil
import typer
from pathlib import Path
from rich.console import Console

try:
    from .player import get_stream_url, stream_song, search_songs, download_song
    from .db import (
        check_playlist, create_playlist,
        delete_playlist as _db_delete_playlist,
        add_song_to_playlist, get_playlist_songs,
        list_playlists as _db_list_playlists,
        log_play, get_history,
    )
except ImportError:
    from player import get_stream_url, stream_song, search_songs, download_song
    from db import (
        check_playlist, create_playlist,
        delete_playlist as _db_delete_playlist,
        add_song_to_playlist, get_playlist_songs,
        list_playlists as _db_list_playlists,
        log_play, get_history,
    )

app = typer.Typer()
console = Console()


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    A terminal-based music player powered by yt-dlp and mpv.
    """
    if ctx.invoked_subcommand is None:
        logo = r'''
[bold cyan]
  __  __ _    _  _____ _______   __
 |  \/  | |  | |/ ____|_   _\ \ / /
 | \  / | |  | | (___   | |  \ V /
 | |\/| | |  | |\___ \  | |   > <
 | |  | | |__| |____) |_| |_ / . \
 |_|  |_|\____/|_____/|_____/_/ \_\
[/bold cyan]'''
        console.print(logo)
        console.print("[bold green]Welcome to Musix![/bold green] Play your favorite songs directly from the terminal.\n")
        console.print("Getting Started:")
        console.print("  [cyan]musix play \"song name\"[/cyan]                       - Instantly stream a song.")
        console.print("  [cyan]musix search \"song name\"[/cyan]                     - Search and select from top results.")
        console.print("  [cyan]musix download \"song name\"[/cyan]                   - Download a song as an audio file.")
        console.print("  [cyan]musix playlist \"name\"[/cyan]                        - Create a playlist.")
        console.print("  [cyan]musix add-song \"song name\" \"playlist\"[/cyan]        - Add a song to a playlist.")
        console.print("  [cyan]musix play-playlist \"playlist name\"[/cyan]           - Play a playlist.")
        console.print("  [cyan]musix list-playlists[/cyan]                          - List all playlists.")
        console.print("  [cyan]musix history[/cyan]                                 - Show recently played songs.")
        console.print("\nRun [green]musix --help[/green] for a full list of commands.\n")


@app.command()
def search(query: str):
    '''Search YouTube and pick a song to stream.'''
    console.print(f'[cyan]Searching[/cyan] for {query}')
    console.print()

    result = search_songs(query)

    if not result:
        console.print('[red]No results found[/red]')
        raise typer.Exit()

    for i, song in enumerate(result, 1):
        duration = f"{song['duration'] // 60}:{song['duration'] % 60:02d}"
        console.print(f"[cyan]{i}[/cyan] [white]{song['title']}[/white] [dim]{song['channel']} | {duration}[/dim]")
        console.print()

    choice = typer.prompt("Pick a number (0 to cancel)")
    try:
        choice = int(choice)
    except ValueError:
        console.print("[red]Enter a valid number[/red]")
        raise typer.Exit()

    if choice == 0:
        raise typer.Exit()

    if choice < 1 or choice > len(result):
        console.print("[red]Enter a number from the list[/red]")
        raise typer.Exit()

    selected = result[choice - 1]
    console.print(f"\n[green]▶ Playing:[/green] {selected['title']}")

    url, title, youtube_id = get_stream_url(f"https://www.youtube.com/watch?v={selected['youtube_id']}")
    log_play(title, youtube_id)
    stream_song(url)


@app.command()
def play(query: str):
    '''Stream a song by name or URL.'''
    console.print(f'[green]> Searching:[/green] {query}')

    url, title, youtube_id = get_stream_url(query)

    console.print(f'[green]-> Now Playing:[/green] {title}')
    console.print('[dim]Press q to stop | p to pause[/dim]')

    log_play(title, youtube_id)
    stream_song(url)


@app.command()
def play_playlist(playlist_name: str):
    '''Play all songs in a playlist. Skips unavailable tracks.'''
    if not check_playlist(playlist_name):
        console.print(f"[red]Playlist '{playlist_name}' does not exist![/red]")
        raise typer.Exit()

    songs = get_playlist_songs(playlist_name)
    if not songs:
        console.print(f"[yellow]Playlist '{playlist_name}' is empty.[/yellow]")
        raise typer.Exit()

    console.print(f"[green]Playing Playlist:[/green] {playlist_name}")
    for song_id, song_name in songs:
        console.print(f"\n[cyan]▶ Now Playing:[/cyan] {song_name}")
        try:
            url, title, youtube_id = get_stream_url(f"https://www.youtube.com/watch?v={song_id}")
        except Exception as e:
            console.print(f"[yellow]Skipping '{song_name}': {e}[/yellow]")
            continue
        log_play(title, youtube_id)
        stream_song(url)


@app.command()
def download(query: str):
    '''Search and download a song as an audio file.'''
    console.print(f'[cyan]Searching[/cyan] for {query}')
    result = search_songs(query)

    if not result:
        console.print('[red]No results found[/red]')
        raise typer.Exit()

    for i, song in enumerate(result, 1):
        duration = f"{song['duration'] // 60}:{song['duration'] % 60:02d}"
        console.print(f"[cyan]{i}[/cyan] [white]{song['title']}[/white] [dim]{song['channel']} | {duration}[/dim]")

    choice = typer.prompt("Pick a number (0 to cancel)")
    try:
        choice = int(choice)
    except ValueError:
        console.print("[red]Enter a valid number[/red]")
        raise typer.Exit()

    if choice == 0:
        raise typer.Exit()
    if choice < 1 or choice > len(result):
        console.print("[red]Enter a number from the list[/red]")
        raise typer.Exit()

    selected = result[choice - 1]
    output_dir = Path.home() / "Music" / "musix"
    output_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[green]Downloading:[/green] {selected['title']}")
    console.print(f"[dim]Saving to {output_dir}[/dim]")
    download_song(selected['youtube_id'], str(output_dir))
    console.print("[green]Done![/green]")


@app.command()
def history():
    '''Show recently played songs.'''
    plays = get_history(20)
    if not plays:
        console.print("[dim]No play history yet.[/dim]")
        raise typer.Exit()

    console.print("[bold]Recently played:[/bold]\n")
    for song_name, youtube_id, played_at in plays:
        link = f"[dim]https://youtu.be/{youtube_id}[/dim]" if youtube_id else ""
        console.print(f"[dim]{played_at[:16]}[/dim]  [white]{song_name}[/white]  {link}")


@app.command()
def list_playlists():
    '''List all playlists.'''
    playlists = _db_list_playlists()
    if not playlists:
        console.print("[dim]No playlists yet. Create one with [cyan]musix playlist \"name\"[/cyan][/dim]")
        raise typer.Exit()
    for name in playlists:
        console.print(f'[cyan]•[/cyan] {name}')


@app.command()
def playlist(name: str):
    '''Create a new playlist.'''
    if check_playlist(name):
        console.print(f"[yellow]Playlist '{name}' already exists.[/yellow]")
    else:
        create_playlist(name)
        console.print(f"[green]'{name}'[/green] created successfully!")


@app.command()
def delete_playlist(name: str):
    '''Delete a playlist and all its songs.'''
    if _db_delete_playlist(name):
        console.print(f"[red]'{name}'[/red] deleted.")
    else:
        console.print(f"[yellow]Playlist '{name}' not found.[/yellow]")


@app.command()
def add_song(name: str, playlist_name: str):
    '''Search and add a song to a playlist.'''
    if not check_playlist(playlist_name):
        console.print(f"[red]Playlist '{playlist_name}' does not exist![/red]")
        raise typer.Exit()

    console.print(f"[cyan]Searching for[/cyan] {name}")
    results = search_songs(name)

    if not results:
        console.print('[red]No results found[/red]')
        raise typer.Exit()

    for i, song in enumerate(results, 1):
        duration = f"{song['duration'] // 60}:{song['duration'] % 60:02d}"
        console.print(f"[green]{i}[/green] {song['title']} [dim]{song['channel']} | {duration}[/dim]")

    console.print()
    choice = typer.prompt(f"Pick a number from 1 to {len(results)}")
    try:
        choice = int(choice)
    except ValueError:
        console.print("[yellow]Enter a valid number[/yellow]")
        raise typer.Exit()

    if choice == 0:
        raise typer.Exit()
    if choice < 1 or choice > len(results):
        console.print("[yellow]Enter a valid number[/yellow]")
        raise typer.Exit()

    selected = results[choice - 1]
    console.print(f"[green]Selected:[/green] {selected['title']}")
    add_song_to_playlist(
        selected['title'], playlist_name,
        selected['youtube_id'], int(selected['duration']),
        selected['channel'],
    )


def main():
    if not shutil.which("mpv"):
        console.print("[red]Error:[/red] mpv is not installed. Please install it first:")
        console.print("  Linux: [cyan]sudo apt install mpv[/cyan]")
        console.print("  Mac:   [cyan]brew install mpv[/cyan]")
        console.print("  Windows: [cyan]scoop install mpv[/cyan]")
        raise typer.Exit(1)
    app()


if __name__ == "__main__":
    main()
