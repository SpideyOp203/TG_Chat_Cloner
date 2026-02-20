import asyncio
import os
import time
from tqdm import tqdm
from pyrogram import Client, errors

# --- CONFIGURATION ---
# Replace 0 and "" with your keys from my.telegram.org
MY_API_ID = 0 
MY_API_HASH = ""

# List your [Source_ID, Destination_ID] pairs here.
# Example: [[-100123456789, -100987654321]]
CHANNELS_TO_CLONE = [
    [0, 0], # Add your specific channel IDs here
]

# Callback function to update the progress bar during download/upload
async def progress_callback(current, total, pbar):
    if pbar.total != total:
        pbar.total = total
    pbar.update(current - pbar.n)

async def clone_channel(app, source, dest):
    print(f"\n--- Starting Clone: {source} -> {dest} ---")
    
    # Progress tracking to avoid duplicates
    progress_file = f"last_id_{abs(source)}.txt"
    last_processed_id = 0
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            last_processed_id = int(f.read().strip())

    messages = []
    async for msg in app.get_chat_history(source):
        if msg.id > last_processed_id:
            messages.append(msg)
    
    # Sort from oldest to newest
    messages.reverse()
    if not messages:
        print(f"Nothing new for {source}. Skipping...")
        return

    print(f"Found {len(messages)} new messages.")

    for message in messages:
        try:
            if message.service: 
                continue

            # 1. POLLS
            if message.poll:
                print(f"📊 Cloning Poll ({message.id})")
                options = [opt.text for opt in message.poll.options]
                await app.send_poll(
                    chat_id=dest,
                    question=message.poll.question,
                    options=options,
                    is_anonymous=message.poll.is_anonymous,
                    type=message.poll.type,
                    allows_multiple_answers=message.poll.allows_multiple_answers
                )

            # 2. MEDIA WITH PROGRESS BAR (PHOTOS, VIDEOS, PDFs, VOICE)
            elif message.media:
                media_type = message.media.value
                
                # Download with progress tracking
                with tqdm(total=0, unit='B', unit_scale=True, desc=f"📥 Downloading {media_type}") as pbar:
                    file_path = await app.download_media(
                        message, 
                        progress=progress_callback, 
                        progress_args=(pbar,)
                    )
                
                if file_path:
                    # Upload with progress tracking
                    with tqdm(total=0, unit='B', unit_scale=True, desc=f"📤 Uploading {media_type}") as pbar:
                        if message.photo:
                            await app.send_photo(dest, file_path, caption=message.caption, progress=progress_callback, progress_args=(pbar,))
                        elif message.video:
                            await app.send_video(dest, file_path, caption=message.caption, progress=progress_callback, progress_args=(pbar,))
                        elif message.voice:
                            await app.send_voice(dest, file_path, caption=message.caption, progress=progress_callback, progress_args=(pbar,))
                        elif message.audio:
                            await app.send_audio(dest, file_path, caption=message.caption, progress=progress_callback, progress_args=(pbar,))
                        else:
                            # Handles PDFs, documents, etc.
                            await app.send_document(dest, file_path, caption=message.caption, progress=progress_callback, progress_args=(pbar,))
                    
                    if os.path.exists(file_path): 
                        os.remove(file_path)
            
            # 3. TEXT ONLY
            elif message.text:
                await app.send_message(dest, message.text)

            # Update the progress tracker
            with open(progress_file, "w") as f:
                f.write(str(message.id))
            
            print(f"✅ Finished {message.id}. Waiting 3s...")
            await asyncio.sleep(3)

        except errors.FloodWait as e:
            print(f"⚠️ Telegram Limit: Sleeping {e.value}s")
            await asyncio.sleep(e.value)
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    # 'anon' creates the session file locally
    async with Client("anon", api_id=MY_API_ID, api_hash=MY_API_HASH) as app:
        for source, dest in CHANNELS_TO_CLONE:
            await clone_channel(app, source, dest)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript stopped manually.")
