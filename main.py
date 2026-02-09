import random
import time
import os
import typer
from playwright.sync_api import sync_playwright
from rich.console import Console
from rich.progress import track

app = typer.Typer()
console = Console()

def human_type_text(page, text: str, wpm: int):
    """
    Types text with human-like characteristics:
    - Variable speed (based on WPM)
    - Occasional pauses
    - Simulated typos and corrections
    """
    # Calculate base delays
    chars_per_minute = wpm * 5
    base_delay = 60 / chars_per_minute
    
    # QWERTY adjacency map for realistic typos (partial)
    nearby_keys = {
        'a': 'qsxz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfc', 'e': 'wsdr',
        'f': 'drtgv', 'g': 'ftyhb', 'h': 'gyujn', 'i': 'ujko', 'j': 'huikm',
        'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
        'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awzed', 't': 'rfgy',
        'u': 'yhji', 'v': 'cfgb', 'w': 'qeas', 'x': 'zsdc', 'y': 'tghu',
        'z': 'asx'
    }

    for char in track(text, description="Typing (Humanized)..."):
        # 1. Random pauses (thinking breaks)
        if random.random() < 0.01: # 1% chance of long pause
            time.sleep(random.uniform(1.0, 3.0))
        
        # 2. Typos (Error simulation)
        # Only simulate typos for lowercase letters to keep it simple
        if random.random() < 0.03 and char.lower() in nearby_keys: # 3% chance
            typo_char = random.choice(nearby_keys[char.lower()])
            page.keyboard.type(typo_char)
            time.sleep(random.uniform(0.1, 0.3)) # Reacion time
            page.keyboard.press("Backspace")
            time.sleep(random.uniform(0.1, 0.3)) # Correction time

        # 3. Type the actual character
        page.keyboard.type(char)
        
        # 4. Variable delay per keystroke
        # Fast typists are consistent but have micro-variations
        delay = random.gauss(base_delay, base_delay * 0.2)
        delay = max(0.01, delay) # Minimum physical limit
        time.sleep(delay)

@app.command()
def logout():
    """
    Securely removes the local Chrome profile data.
    Use this to clear your session credentials from the disk.
    """
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    if os.path.exists(user_data_dir):
        console.print(f"[yellow]Removing profile data at {user_data_dir}...[/yellow]")
        try:
            import shutil
            shutil.rmtree(user_data_dir)
            console.print("[green]Profile deleted successfully. You will need to log in again next time.[/green]")
        except Exception as e:
            console.print(f"[red]Error deleting profile: {e}[/red]")
            console.print("You may need to close any open Chrome windows first.")
    else:
        console.print("No profile data found.")

@app.command()
def login():
    """
    Launches a standard Chrome window for you to log in.
    Run this if you see "This browser or app may not be secure".
    """
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Common Chrome paths on Windows
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
            
    if not chrome_path:
        console.print("[bold red]Error:[/bold red] Could not find Google Chrome installation.")
        console.print("Please ensure Chrome is installed.")
        return

    console.print(f"[green]Launching standard Chrome for login...[/green]")
    console.print(f"Profile: {user_data_dir}")
    console.print(f"Chrome Path: {chrome_path}")
    console.print("[bold yellow]Please log in to your Google Account in the opened window, then close it and run 'python main.py run'[/bold yellow]")
    
    # Construct command
    cmd = [
        chrome_path,
        f"--user-data-dir={user_data_dir}",
        "--new-window",
        "--no-first-run",
        "--no-default-browser-check",
        "https://docs.google.com"
    ]
    
    console.print(f"Executing: {' '.join(cmd)}")
    
    import subprocess
    # creating a separate process group
    subprocess.Popen(cmd, close_fds=True, shell=False)

@app.command()
def run(
    url: str = typer.Option(..., prompt="Google Doc URL", help="The URL of the Google Doc to type into."),
    source_file: str = typer.Option("source.txt", help="Path to the file containing text to type."),
    wpm: int = typer.Option(60, help="Approximate typing speed in words per minute."),
    cleanup: bool = typer.Option(False, help="Clear the source file after typing is complete.")
):
    """
    Simulates human typing into a Google Doc from a source file.
    """
    if not os.path.exists(source_file):
        console.print(f"[bold red]Error:[/bold red] Source file '{source_file}' not found.")
        return

    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    if not content:
        console.print(f"[bold red]Error:[/bold red] Source file '{source_file}' is empty.")
        return

    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    console.print(f"[blue]Using Chrome profile at: {user_data_dir}[/blue]")
    
    if not os.path.exists(user_data_dir):
         console.print("[yellow]First time run? You might need to run 'python main.py login' first if authentication fails.[/yellow]")

    with sync_playwright() as p:
        # Launch persistent context
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="chrome", # Use installed Chrome
                args=["--start-maximized", "--disable-blink-features=AutomationControlled"],
                no_viewport=True,
                # Explicitly tell Chrome NOT to warn about these, and try to stop Playwright from adding them
                ignore_default_args=["--enable-automation", "--no-sandbox"] 
            )
            
            # Stealth: Hide navigator.webdriver
            browser.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
        except Exception as e:
            console.print(f"[bold red]Error launching browser:[/bold red] {e}")
            console.print("[yellow]Try running 'python main.py login' first.[/yellow]")
            return
        
        page = browser.pages[0]
        console.print(f"Navigating to {url}...")
        try:
            page.goto(url, timeout=60000) # Increased timeout
        except Exception as e:
             console.print(f"[bold red]Navigation failed:[/bold red] {e}")
             console.print("The browser might have been closed or the URL is invalid.")
             return

        console.print("[bold green]Press ENTER in the terminal when the Google Doc is loaded, editable, and the cursor is placed where you want to start typing.[/bold green]")
        input()

        console.print(f"Starting to type {len(content)} characters...")
        
        # Focus the page just in case
        page.bring_to_front()
        
        human_type_text(page, content, wpm)

        console.print("[bold green]Done![/bold green]")
        
        if cleanup:
            console.print("[yellow]Cleaning up source file...[/yellow]")
            with open(source_file, "w") as f:
                f.write("")
            console.print("[green]Source file cleared.[/green]")

        # Keep browser open for a moment
        time.sleep(2)


if __name__ == "__main__":
    app()
