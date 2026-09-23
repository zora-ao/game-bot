import asyncio
import threading
from flask import Flask
from playwright.async_api import async_playwright

# 1. Web server to keep Render happy and responding to ping health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is active and running!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

# 2. Automation script
async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()

        print("Navigating to game URL...")
        await page.goto("https://paios-classroom.com/campus", wait_until="networkidle")

        print("Waiting 15 seconds for game elements to load...")
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
    # Start Playwright in a background thread
    threading.Thread(target=start_bot_thread, daemon=True).start()
    
    # Start Flask web server
    run_web_server()
