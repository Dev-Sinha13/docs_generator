import asyncio
import random
import os
from playwright.async_api import async_playwright

class TypewriterSession:
    def __init__(self):
        self.browser = None
        self.page = None
        self.stop_requested = False
        self.is_running = False
        self.progress = 0
        self.status = "Idle"

    async def launch_browser(self, login_mode=False):
        """Launches the browser context."""
        print(f"DEBUG: Attempting to launch browser. Login mode: {login_mode}")
        user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
        os.makedirs(user_data_dir, exist_ok=True)
        print(f"DEBUG: Profile path: {user_data_dir}")
        
        args = ["--start-maximized", "--disable-blink-features=AutomationControlled"]
        if login_mode:
            # Minimal args for login mode
            pass 
        
        # We need to restart playwright for each session to ensure clean state
        try:
            print("DEBUG: Starting Playwright...")
            self.playwright = await async_playwright().start()
            print("DEBUG: Playwright started.")
            
            print("DEBUG: Launching persistent context...")
            self.browser = await self.playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                channel="chrome",
                args=args,
                no_viewport=True,
                ignore_default_args=["--enable-automation", "--no-sandbox"]
            )
            print("DEBUG: Browser context launched.")
            
            # Stealth script
            if not login_mode:
                await self.browser.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)
                
            self.page = self.browser.pages[0]
            print("DEBUG: Page retrieved.")
            
            if login_mode:
                print("DEBUG: Navigating to Google Docs for login...")
                await self.page.goto("https://docs.google.com")
                
            return True, "Success"
        except Exception as e:
            error_msg = f"ERROR launching browser: {type(e).__name__}: {repr(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            self.status = error_msg
            return False, error_msg

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        self.is_running = False
        self.status = "Stopped"

    async def type_content(self, url: str, text: str, wpm: int):
        if not await self.launch_browser():
            self.status = "Error: Could not launch browser"
            return

        self.is_running = True
        self.stop_requested = False
        self.status = "Navigating..."
        self.progress = 0

        try:
            await self.page.goto(url, timeout=60000)
            self.status = "Waiting for user to click..."
            
            # We can't easily detect "user clicked", so we'll wait a fixed time or for a signal?
            # Creating a reliable signal in headless/API mode is hard.
            # INSTEAD: We will check if the element is focused? 
            # For now, let's just wait for a 'start' signal from UI, but since this is one function
            # we might just wait a few seconds after load, or expect the user to have clicked focus.
            # Actually, let's just wait 5 seconds for them to focus, then start.
            
            self.status = "Starting in 5 seconds... CLICK THE DOC!"
            for i in range(5, 0, -1):
                if self.stop_requested: break
                self.status = f"Starting in {i}s... CLICK DOC NOW"
                await asyncio.sleep(1)

            if self.stop_requested:
                await self.close_browser()
                return

            self.status = "Typing..."
            
            # Logic from main.py
            chars_per_minute = wpm * 5
            base_delay = 60 / chars_per_minute
            
            nearby_keys = {
                'a': 'qsxz', 'b': 'vghn', 'c': 'xdfv', 'd': 'serfc', 'e': 'wsdr',
                'f': 'drtgv', 'g': 'ftyhb', 'h': 'gyujn', 'i': 'ujko', 'j': 'huikm',
                'k': 'jiolm', 'l': 'kop', 'm': 'njk', 'n': 'bhjm', 'o': 'iklp',
                'p': 'ol', 'q': 'wa', 'r': 'edft', 's': 'awzed', 't': 'rfgy',
                'u': 'yhji', 'v': 'cfgb', 'w': 'qeas', 'x': 'zsdc', 'y': 'tghu',
                'z': 'asx'
            }

            total_chars = len(text)
            for i, char in enumerate(text):
                if self.stop_requested:
                    self.status = "Stopped by user"
                    break
                
                # Progress
                self.progress = int((i / total_chars) * 100)
                self.status = f"Typing... {self.progress}%"

                # 1. Random pauses
                if random.random() < 0.01:
                    await asyncio.sleep(random.uniform(1.0, 3.0))

                # 2. Typos
                if random.random() < 0.03 and char.lower() in nearby_keys:
                    typo_char = random.choice(nearby_keys[char.lower()])
                    await self.page.keyboard.type(typo_char)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    await self.page.keyboard.press("Backspace")
                    await asyncio.sleep(random.uniform(0.1, 0.3))

                # 3. Type char
                await self.page.keyboard.type(char)

                # 4. Delay
                delay = random.gauss(base_delay, base_delay * 0.2)
                delay = max(0.01, delay)
                await asyncio.sleep(delay)

            self.status = "Completed"
            self.progress = 100
            
        except Exception as e:
            self.status = f"Error: {str(e)}"
        
        finally:
            self.is_running = False
            # Don't auto-close immediately so they can see result? 
            # Or maybe close after a delay.
            await asyncio.sleep(2)
            await self.close_browser()

# Singleton instance
session = TypewriterSession()
