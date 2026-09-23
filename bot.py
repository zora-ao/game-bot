import asyncio
import os
import json
import threading
from flask import Flask
from playwright.async_api import async_playwright

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is active and running!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        # Load saved browser session/cookies if present
        if os.path.exists("storage.json"):
            context = await browser.new_context(
                storage_state="storage.json",
                viewport={'width': 1280, 'height': 720}
            )
            print("Loaded saved login session successfully!")
        else:
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            print("Warning: No storage.json found. Bot running without logged-in session.")

        page = await context.new_page()

        print("Navigating to game URL...")
        await page.goto("https://paios-classroom.com/campus", wait_until="networkidle")

        print("Waiting 15 seconds for campus/canvas to load...")
        await asyncio.sleep(15)

        print("Starting task loop...")
        while True:
            try:
                btn = page.locator("#vc-prompt")
                if await btn.is_visible():
                    await btn.click()
                    print("Clicked action button!")
                else:
                    print("Waiting for task button...")
            except Exception as e:
                print(f"Error: {e}")

            await asyncio.sleep(0.3)

def start_bot_thread():
    asyncio.run(run_bot())

if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    run_web_server()
