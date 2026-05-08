import typer
from rich.console import Console
from player import get_stream_url, stream_song, search_songs
from db import CheckPlaylist, CreatePlaylist, DeletePlaylist, addSongToPlaylist, getPlaylistSongs

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
        console.print("  [cyan]musix play \"song name\"[/cyan]       - Instantly stream a song.")
        console.print("  [cyan]musix search \"song name\"[/cyan]     - Search and select from top results.")
        console.print("  [cyan]musix playlist \"name\"[/cyan]        - Create your own playlist.")
        console.print("  [cyan]musix add-song \"song name\"[/cyan] - Add a song to a playlist.")
        console.print("  [cyan]musix play-playlist \"playlist name\" [/cyan] - Play a playlist.")
        console.print("\nRun [green]musix --help[/green] for a full list of commands.\n")

@app.command()
def search(query : str):
    '''Let user search and pick the song'''

    console.print(f'[cyan]Searching[/cyan] for {query}')
    console.print()
    
    result = search_songs(query)

    if not result :
        console.print(f'[red]No Results found[/red]')
        raise typer.Exit()
    
    for i, song in enumerate(result, 1):
        duration = f"{song["duration"] // 60} : {song["duration"] % 60:02d}"
        console.print(f"[cyan]{i}[/cyan] [white]{song['title']}[/white]"
                      f"[dim] {song["channel"]} | {duration}[/dim]"
                      )
        console.print()
    
    console.print()
    choice = typer.prompt("Pick a number ( 0 to cancel )")

    try :
        choice = int(choice)

    except ValueError:
        console.print("[red]You don't know how numbers looks like[/red]")
        raise typer.Exit()
    
    if choice == 0:
        raise typer.Exit()
    
    if choice < 1 or choice > len(result):
        console.print("[red]Seriously, did I gave the option to choose that number?[/red]")
        raise typer.Exit()
    
    selected = result[choice - 1]
    console.print(f"\n[green]▶ Playing:[/green] {selected['title']}")

    url, title, sub_url = get_stream_url(
    f"https://www.youtube.com/watch?v={selected['youtube_id']}"
)

    stream_song(url, sub_url)

@app.command()
def play(query : str):
    '''stream a song'''
    console.print(f'[green]> Searching:[/green] {query}')

    url, title, sub_url = get_stream_url(query)

    console.print(f'[green]-> Now Playing:[/green] {title}')
    console.print('[dim]Press q to stop[/dim]')
    console.print('[dim]Press p to pause/un-pause[/dim]')

    stream_song(url, sub_url)

@app.command()
def play_playlist(playlist : str):
    '''Play all songs in a playlist'''
    if not CheckPlaylist(playlist):
        console.print(f"[red]Playlist '{playlist}' does not exist![/red]")
        raise typer.Exit()
        
    songs = getPlaylistSongs(playlist)
    if not songs:
        console.print(f"[yellow]Playlist '{playlist}' is empty.[/yellow]")
        raise typer.Exit()

    console.print(f"[green]Playing Playlist:[/green] {playlist}")
    for song_id, song_name in songs:
        console.print(f"\n[cyan]▶ Now Playing:[/cyan] {song_name}")
        url, title, sub_url = get_stream_url(f"https://www.youtube.com/watch?v={song_id}")
        stream_song(url, sub_url)

@app.command()
def download():
    pass

@app.command()
def history():
    pass

@app.command()
def playlist(name : str):
    if not CheckPlaylist(name) :
        if CreatePlaylist(name):
            console.print(f"[green]{name}[/green] Created Successfully !")
    else :
        console.print("Playlist Already Created!")

@app.command()
def deletePlaylist(name : str):
    if DeletePlaylist(name):
        console.print(f"[red]{name}[/red] successfully deleted!")
    else :
        console.print("[yellow]ERROR[/yellow]")

@app.command()
def addSong(name : str, playlist : str):
    searched_songs = search_songs(name)

    '''Print searched_songs'''

    console.print(f"[cyan]Searching for[/cyan] {name}")
    i = 1
    store = list()
    for song_details in searched_songs:
        console.print(f"[green]{i}[/green] {song_details["title"]} - {song_details["duration"]//60}:{song_details["duration"]%60:02d} ")
        store.append({song_details["youtube_id"] : [song_details["title"], song_details["duration"], song_details["channel"]]})
        i += 1
    i -= 1
        
    console.print()
    choice = typer.prompt(f"Pick a number from 1 to {i} to add the song: ")

    try:
        choice = int(choice)
    except ValueError:
        console.print(f"[yellow]Enter a valid number[/yellow]")
        typer.Exit()

    if choice == 0:
        raise typer.Exit()
    elif choice >= i:
        console.print(f"[yellow]Enter a valid number[/yellow]")
    else :
        (song_id, [song_title, song_duration, song_channel]), = store[choice-1].items()
        console.print(f"[green]Selected[/green] : {song_title}")
        
    song_duration = int(song_duration)
    addSongToPlaylist(song_title, playlist, song_id, song_duration, song_channel)

    

    


def main():
    app()

if __name__ == "__main__":
    main()