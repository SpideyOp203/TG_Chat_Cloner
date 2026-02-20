# How the TG_Chat_Cloner Works 
Heya NERDS!! , If youre here i think you wanna know whats happening inside the cloner.
This document explains the technical logic behind this tool for those who want to understand the "under the hood" process.

## 1. The Core (Pyrogram)
The script uses the **Pyrogram** library, which communicates directly with Telegram's MTProto API. Unlike "Bot API" tools, this script acts as a **User-Bot**, allowing it to access restricted channels where traditional bots might be blocked.

## 2. The Cloning Process
The script follows a "Download-then-Upload" cycle:
1. **Iterate**: The script fetches messages from the source channel starting from the oldest or the "last saved" ID.
2. **Buffer**: It identifies the media type (Photo, Video, Document, etc.).
3. **Download**: Media is downloaded into a temporary local directory. 
4. **Upload**: The script sends that media to your destination channel.
5. **Clean up**: Temporary files are deleted immediately after a successful upload to save disk space.

## 3. Real-Time Progress Tracking
We use the `tqdm` library integrated with Pyrogram's `progress` callback:
* **Mathematical Logic**: 
  $$Progress \% = (\text{Current Bytes} / \text{Total Bytes}) \times 100$$
* This allows the terminal to display a live bar showing MB/s and Estimated Time of Arrival (ETA).

## 4. Resume & Persistence Logic
To prevent starting from scratch if the script stops, we use a **Checkpoint System**:
* Every time a message is successfully cloned, its ID is written to a file named `last_id_SOURCE_ID.txt`.
* On restart, the script reads this file and asks the Telegram API for messages *only* newer than that ID (`offset_id`).

## 5. Security & Rate Limiting
* **FloodWait**: Telegram limits how fast you can upload. The script catches `FloodWait` errors and automatically "sleeps" for the required number of seconds before resuming.
* **Sensitive Data**: By using a `.gitignore`, the script ensures that `API_HASH` and `.session` files stay on your local machine and never reach the cloud.
