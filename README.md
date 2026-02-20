
# TG_Chat_Cloner 🚀

I built this tool to archive content from Telegram channels and supergroups. It is specifically designed to handle "restricted" content that normally cannot be forwarded, making it perfect for personal backups of educational materials or media. 

This version includes **real-time progress bars** so you can monitor download speeds and estimated completion times.

## 🌟 Features
* **Live Progress Bars:** View download/upload speeds (MB/s) and ETA for videos and large files using `tqdm`.
* **Full Media Support:** Automatically detects and clones Photos, Videos (with thumbnails), Voice Notes, and Audio files.
* **Document Handling:** Perfectly clones PDFs, ZIPs, and other documents.
* **Poll Cloning:** Re-creates polls in the destination channel (note: votes do not carry over).
* **Resume Support:** Automatically saves the last message ID to a `.txt` file so the script can resume exactly where it left off after a crash or internet cutout.
* **Flood Protection:** Built-in delays and error handling for Telegram's rate limits to keep your account safe.

## 🛠️ Prerequisites
* **Python 3.8+**
* A Telegram account and your own API keys (get them at [my.telegram.org](https://my.telegram.org)).
* Libraries: `pyrogram`, `tgcrypto`, and `tqdm`.

## 📦 Installation
1. Clone this repository to your local machine.
2. Install the required dependencies:
```bash
pip install -r requirements.txt

```

## 📖 How to Use

### Step 1: Get your Chat IDs

Run `find_ids.py`. This will list every chat you are currently in along with its unique ID.

```bash
python find_ids.py

```

*Look for IDs starting with -100; these are the ones you need for the cloner.*

### Step 2: Configure the Cloner

Open `master_cloner.py` and enter your `API_ID` and `API_HASH`.
Then, add your source and destination IDs to the `CHANNELS_TO_CLONE` list:

```python
CHANNELS_TO_CLONE = [
    [-100SourceID, -100DestinationID], # Example: From Source to Destination
]

```

### Step 3: Start Cloning

Run the main script and watch the progress bars:

```bash
python master_cloner.py

```

## ⚠️ A Note on Security

I have included a `.gitignore` to ensure your `.session` files (which act as your login password) and your `last_id_*.txt` logs are never uploaded to GitHub. **Never share your session files or API keys with anyone.**

## ⚖️ Disclaimer

This tool is for personal use and educational purposes only. Please respect copyright laws and the privacy of channel owners. I am not responsible for any misuse or account issues resulting from the use of this script.
