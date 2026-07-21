import asyncio
import json
import logging
import os
import sys
from tqdm import tqdm
from pyrogram import Client, errors

# mute pyrogram's annoying background socket disconnect errors
logging.getLogger("pyrogram").setLevel(logging.ERROR)

CONFIG_FILE = "config.json"
SESSION_NAME = "cloner_session"

def get_config():
    # quick onboarding if config is missing
    if not os.path.exists(CONFIG_FILE):
        print("\n--- First-Time Setup ---")
        api_id = int(input("Enter API_ID: ").strip())
        api_hash = input("Enter API_HASH: ").strip()
        config = {"api_id": api_id, "api_hash": api_hash, "channels": []}
        save_config(config)
        return config
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

async def list_chats(app):
    # dump all open dialogs so we can easily grab chat IDs
    print("\n--- Fetching Dialogs ---")
    async for dialog in app.get_dialogs():
        chat = dialog.chat
        chat_type = chat.type.value if hasattr(chat.type, 'value') else chat.type
        title = chat.title or f"{chat.first_name or ''} {chat.last_name or ''}".strip()
        print(f"[{chat_type.upper()}] {title} | ID: {chat.id}")
    print("------------------------\n")

def add_channel_pair(config):
    # save a new source -> dest pair to config
    try:
        source = int(input("Enter Source Chat ID: ").strip())
        dest = int(input("Enter Destination Chat ID: ").strip())
        config["channels"].append([source, dest])
        save_config(config)
        print(f"Added pair to saved list: {source} -> {dest}")
    except ValueError:
        print("⚠️ Invalid ID format. Must be an integer.")

async def progress_callback(current, total, pbar):
    # sync tqdm bar with pyrogram's chunk progress
    if pbar.total != total:
        pbar.total = total
    pbar.update(current - pbar.n)

async def clone_channel(app, source, dest, ignore_history=False):
    print(f"\n==========================================")
    print(f"Starting Sync: {source} -> {dest}")
    print(f"==========================================")
    
    # strip negative sign from channel id for clean filenames
    progress_file = f"last_id_{abs(source)}.txt"
    last_id = 0
    
    # read last cloned id if we're resuming
    if not ignore_history and os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            last_id = int(f.read().strip() or 0)

    # get messages newer than our last checkpoint
    messages = [msg async for msg in app.get_chat_history(source) if msg.id > last_id]
    
    # pyrogram fetches newest first, reverse it to clone oldest -> newest
    messages.reverse()
    
    if not messages:
        print(f"No new messages found for {source}.")
        return

    print(f"Found {len(messages)} new messages to clone.\n")

    for msg in messages:
        try:
            # ignore system events like "user joined" or pins
            if msg.service:
                continue

            print(f"Processing ID: {msg.id}")

            if msg.poll:
                print("    Type: Poll")
                await app.send_poll(
                    dest,
                    msg.poll.question,
                    [o.text for o in msg.poll.options],
                    is_anonymous=msg.poll.is_anonymous,
                    type=msg.poll.type,
                    allows_multiple_answers=msg.poll.allows_multiple_answers
                )
            elif msg.media:
                media_type = msg.media.value
                print(f"    Type: Media ({media_type.upper()})")
                
                # dl to disk with progress bar
                with tqdm(total=0, unit='B', unit_scale=True, desc=f"    DL {media_type}") as pbar:
                    path = await app.download_media(msg, progress=progress_callback, progress_args=(pbar,))
                
                if path:
                    try:
                        # upload to destination
                        with tqdm(total=0, unit='B', unit_scale=True, desc=f"    UL {media_type}") as pbar:
                            # match send method to media type (e.g. send_photo), fallback to document
                            sender = getattr(app, f"send_{media_type}", app.send_document)
                            await sender(dest, path, caption=msg.caption, progress=progress_callback, progress_args=(pbar,))
                    finally:
                        # delete local file right away even if upload fails
                        if os.path.exists(path):
                            os.remove(path)
            elif msg.text:
                print("    Type: Text")
                await app.send_message(dest, msg.text)

            # checkpoint ID after every successful clone
            with open(progress_file, "w") as f:
                f.write(str(msg.id))
            
            # 3s delay to avoid flood bans
            print(f"Cloned ID {msg.id}. Cooldown 3s...\n")
            await asyncio.sleep(3)

        except errors.FloodWait as e:
            # hit flood wait, sleep for whatever penalty time telegram asks
            print(f"⚠️ Telegram flood wait! Sleeping for {e.value}s...\n")
            await asyncio.sleep(e.value)
        except Exception as e:
            # don't let one broken message crash the whole loop
            print(f"❌ Error on ID {msg.id}: {e}\n")

async def run_saved_cloner(app, config):
    if not config["channels"]:
        print("No channels configured. Use Option 2 first.")
        return
    
    # ask once if we should start fresh or resume for the whole batch
    mode = input("\nClone all saved pairs from scratch? (y/n): ").strip().lower()
    ignore_history = True if mode == 'y' else False
    
    for source, dest in config["channels"]:
        await clone_channel(app, source, dest, ignore_history=ignore_history)
    print("Batch cloning finished.")

async def run_single_time_cloner(app):
    # one-off cloning without saving to config
    try:
        source = int(input("\nEnter Single-Time Source Chat ID: ").strip())
        dest = int(input("Enter Single-Time Destination Chat ID: ").strip())
        
        mode = input("Clone from scratch? (y/n): ").strip().lower()
        ignore_history = True if mode == 'y' else False
        
        await clone_channel(app, source, dest, ignore_history=ignore_history)
        print("Single-time clone finished.")
    except ValueError:
        print("⚠️ Invalid ID format. Must be an integer.")

async def main():
    config = get_config()
    app = Client(SESSION_NAME, api_id=config["api_id"], api_hash=config["api_hash"])
    
    # start app and CLI menu
    async with app:
        while True:
            print("\n1. List Chats & IDs")
            print("2. Add Channel Pair (For Saved List)")
            print("3. Run Saved Multiple Cloner")
            print("4. Run Single-Time Cloner")
            print("5. Exit")
            choice = input("Select mode (1-5): ").strip()
            
            if choice == "1":
                await list_chats(app)
            elif choice == "2":
                add_channel_pair(config)
            elif choice == "3":
                await run_saved_cloner(app, config)
            elif choice == "4":
                await run_single_time_cloner(app)
            elif choice == "5":
                break
            else:
                print("⚠️ Invalid selection.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # exit cleanly on ctrl+c without printing a massive traceback
        sys.exit(0)
