import asyncio
import os
import threading
from flask import Flask
from playwright.async_api import async_playwright

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Swim Bot is active and running!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        if os.path.exists("storage.json"):
            print("Loaded saved login session successfully!")
            context = await browser.new_context(
                storage_state="storage.json",
                viewport={'width': 1280, 'height': 720}
            )
        else:
            print("Warning: No storage.json found.")
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})

        page = await context.new_page()

        print("Navigating to game URL...")
        await page.goto("https://paios-classroom.com/campus", wait_until="networkidle")

        print("Waiting 15 seconds for canvas to load...")
        await asyncio.sleep(15)

        # Focus canvas so keypresses work
        try:
            await page.click("canvas")
            print("Clicked game canvas to focus input.")
        except Exception as e:
            print(f"Canvas focus error: {e}")

        race_count = 0

        print("Starting Swimming Race Loop...")
        while True:
            try:
                print(f"--- Starting Swim Race #{race_count + 1} ---")
                
                # 1. Press 'X' to enter the swim race
                await page.keyboard.press("KeyX")
                await asyncio.sleep(1.0)

                # Click prompt button if visible
                btn = page.locator("#vc-prompt")
                if await btn.is_visible():
                    await btn.click()
                    print("Clicked prompt button!")

                # Wait for race countdown to finish
                await asyncio.sleep(3.0)

                # 2. Swim forward (Hold W)
                print("Swimming forward...")
                await page.keyboard.down("KeyW")
                await asyncio.sleep(4.0)  # Adjust duration based on pool length
                await page.keyboard.up("KeyW")

                await asyncio.sleep(0.5)

                # 3. Swim back (Hold S)
                print("Swimming back...")
                await page.keyboard.down("KeyS")
                await asyncio.sleep(4.0)  # Adjust duration based on pool length
                await page.keyboard.up("KeyS")

                print("Finished lap! Waiting for race reset...")
                race_count += 1

                # Wait for race completion / reset to prompt
                await asyncio.sleep(5.0)

            except Exception as e:
                print(f"Error during swim race: {e}")
                await asyncio.sleep(2.0)

def start_bot_thread():
    asyncio.run(run_bot())

if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    run_web_server()
