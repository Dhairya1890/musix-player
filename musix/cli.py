import typer
from rich.console import Console
from player import get_stream_url, stream_song, search_songs
from db import CheckPlaylist, CreatePlaylist, DeletePlaylist

app = typer.Typer()
console = Console()


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

    url, title = get_stream_url(
    f"https://www.youtube.com/watch?v={selected['youtube_id']}"
)

    stream_song(url)

@app.command()
def play(query : str):
    '''stream a song'''
    console.print(f'[green]> Searching:[/green] {query}')

    url, title = get_stream_url(query)

    console.print(f'[green]-> Now Playing:[/green] {title}')
    console.print('[dim]Press q to stop[/dim]')

    stream_song(url)



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


if __name__ == "__main__":
    app()