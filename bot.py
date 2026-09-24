import asyncio
import os
import threading
from flask import Flask
from playwright.async_api import async_playwright

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Swim & Heal Bot is active and running!"

def run_web_server():
    app.run(host='0.0.0.0', port=10000)

async def walk_from_spawn_to_pool(page):
    print("Navigating from world spawn to Swimming Pool...")

    # Left 6s
    await page.keyboard.down("KeyA")
    await asyncio.sleep(6.0)
    await page.keyboard.up("KeyA")
    await asyncio.sleep(0.2)

    # Down 3s
    await page.keyboard.down("KeyS")
    await asyncio.sleep(3.0)
    await page.keyboard.up("KeyS")
    await asyncio.sleep(0.2)

    # Left 1.5s
    await page.keyboard.down("KeyA")
    await asyncio.sleep(1.5)
    await page.keyboard.up("KeyA")
    await asyncio.sleep(0.2)

    # Down 9s
    await page.keyboard.down("KeyS")
    await asyncio.sleep(9.0)
    await page.keyboard.up("KeyS")
    await asyncio.sleep(0.2)

    # Left 2s
    await page.keyboard.down("KeyA")
    await asyncio.sleep(2.0)
    await page.keyboard.up("KeyA")
    await asyncio.sleep(0.5)

    print("Arrived at the Swimming Pool from spawn!")

async def walk_to_chapel(page):
    print("HP low! Walking to Chapel to heal...")
    
    # Right 3s
    await page.keyboard.down("KeyD")
    await asyncio.sleep(3.0)
    await page.keyboard.up("KeyD")
    await asyncio.sleep(0.2)

    # Up 12s
    await page.keyboard.down("KeyW")
    await asyncio.sleep(12.0)
    await page.keyboard.up("KeyW")
    await asyncio.sleep(0.2)

    # Right 1s
    await page.keyboard.down("KeyD")
    await asyncio.sleep(1.0)
    await page.keyboard.up("KeyD")
    await asyncio.sleep(0.2)

    # Up 2s
    await page.keyboard.down("KeyW")
    await asyncio.sleep(2.0)
    await page.keyboard.up("KeyW")
    await asyncio.sleep(0.5)

    # Press X to rest/heal in Chapel
    print("Arrived at Chapel. Pressing X and resting for 15 seconds...")
    await page.keyboard.press("KeyX")
    await asyncio.sleep(15.0)

async def walk_back_to_pool(page):
    print("Healed! Walking back to Swimming Pool...")

    # Down 2s
    await page.keyboard.down("KeyS")
    await asyncio.sleep(2.0)
    await page.keyboard.up("KeyS")
    await asyncio.sleep(0.2)

    # Left 1s
    await page.keyboard.down("KeyA")
    await asyncio.sleep(1.0)
    await page.keyboard.up("KeyA")
    await asyncio.sleep(0.2)

    # Down 12s
    await page.keyboard.down("KeyS")
    await asyncio.sleep(12.0)
    await page.keyboard.up("KeyS")
    await asyncio.sleep(0.2)

    # Left 3s
    await page.keyboard.down("KeyA")
    await asyncio.sleep(3.0)
    await page.keyboard.up("KeyA")
    await asyncio.sleep(0.5)

    print("Back at the Swimming Pool!")

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

        # Focus canvas so keyboard inputs register
        try:
            await page.click("canvas")
            print("Clicked game canvas to focus input.")
        except Exception as e:
            print(f"Canvas focus error: {e}")

        # Navigate from spawn point to pool prompt on startup
        await walk_from_spawn_to_pool(page)

        race_count = 0

        print("Starting Main Automation Loop...")
        while True:
            try:
                # Every 5 races, walk to Chapel to heal and return
                if race_count > 0 and race_count % 5 == 0:
                    await walk_to_chapel(page)
                    await walk_back_to_pool(page)

                print(f"--- Entering Queue for Swim Race #{race_count + 1} ---")
                
                # 1. Join swim queue
                await page.keyboard.press("KeyX")
                await asyncio.sleep(1.0)

                btn = page.locator("#vc-prompt")
                if await btn.is_visible():
                    await btn.click()
                    print("Clicked join line prompt!")

                # 2. Wait in line
                print("Waiting in line for race to start...")
                for _ in range(15):
                    await page.keyboard.press("KeyX")
                    await asyncio.sleep(1.0)

                # 3. Perform swim lap
                print("Swimming forward...")
                await page.keyboard.down("KeyW")
                await asyncio.sleep(4.5)
                await page.keyboard.up("KeyW")

                await asyncio.sleep(0.5)

                print("Swimming back...")
                await page.keyboard.down("KeyS")
                await asyncio.sleep(4.5)
                await page.keyboard.up("KeyS")

                print("Race completed!")
                race_count += 1

                await asyncio.sleep(6.0)

            except Exception as e:
                print(f"Error during execution loop: {e}")
                await asyncio.sleep(2.0)

def start_bot_thread():
    asyncio.run(run_bot())

if __name__ == "__main__":
    threading.Thread(target=start_bot_thread, daemon=True).start()
    run_web_server()
