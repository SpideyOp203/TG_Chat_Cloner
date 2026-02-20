import asyncio
from pyrogram import Client

# You'll need to get your own API ID and Hash from my.telegram.org , after getting API ID and Hash replace 0 with API ID and put the Hash inbetween "Your_Hash".
API_ID = 0  
API_HASH = ""

async def main():
    # I'm using "anon" as the session name here. 
    # This will create an 'anon.session' file in your folder.
    async with Client("anon", api_id=API_ID, api_hash=API_HASH) as app:
        print("\n--- Listing all your chats ---\n")
        
        async for dialog in app.get_dialogs():
            chat = dialog.chat
            
            # This identifies if it's a private chat, group, or channel
            chat_type = chat.type.value if hasattr(chat.type, 'value') else chat.type
            
            # Grabbing the name of the chat or the person
            title = chat.title or f"{chat.first_name or ''} {chat.last_name or ''}".strip()
            
            print(f"Type: {chat_type.upper()}")
            print(f"Name: {title}")
            print(f"ID: {chat.id}")
            print("-" * 25)

        print("\n--- All done! ---")
        print("Grab the IDs you need (usually starting with -100) for the cloner script.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
