# TG_Chat_Cloner V2

A powerful, asynchronous Telegram chat and channel cloner built with Pyrogram and Python. Designed to archive content, migrate media archives, and bypass forwarding restrictions without blowing up local disk storage or triggering Telegram API rate limits.

---

## Why V2?
In V1, ID scanning and cloning were split across multiple standalone scripts (`find_ids.py` and `master_cloner.py`). V2 consolidates the entire workflow into a single, state-aware terminal interface (`master_cloner_V2.py`) with several major architectural improvements:

* **Unified CLI Interface:** Scan dialogs, manage saved pairs, and execute migrations from a single interactive menu.
* **Dual-Mode Execution:** 
  * **Saved Batch Mode:** Store frequently synced channel pairs in `config.json` and run them sequentially.
  * **Single-Time Ad-Hoc Mode:** Clone a channel on the fly without saving the mapping to your permanent config.
* **History Overrides:** Choose at runtime whether to resume from your last checkpoint or force a clean sync from ID 0.
* **Zero Disk Bloat:** Media is downloaded in streaming chunks, uploaded immediately, and deleted from your local hard drive the exact second the upload resolves.
* **FloodWait Resilience:** Automatically catches Telegram API rate limits, pauses execution for the exact penalty duration requested by the server, and cleanly resumes without crashing.

---

## Complete Setup & Installation Guide

### 1. Prerequisites
* **Python 3.9+** installed on your system.
* **Telegram API Credentials:** You must generate your own `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org) under **API development tools**.

### 2. Clone the Repository
Open your terminal and clone the project to your local machine:
```bash
git clone [https://github.com/SpideyOp203/TG_Chat_Cloner.git](https://github.com/SpideyOp203/TG_Chat_Cloner.git)
cd TG_Chat_Cloner

```

### 3. Create a Virtual Environment (Recommended)
To prevent dependency conflicts with other Python projects on your system, create and activate an isolated virtual environment (venv) before installing the packages.

**On Linux / macOS:**

### Create the virtual environment
```bash 
python3 -m venv venv

```
### Activate the virtual environment

```bash
source venv/bin/activate
```

**On Windows (Command Prompt / PowerShell):**

### Create the virtual environment
```bash
python -m venv venv
```

### Activate on Command Prompt:
```bash
venv\Scripts\activate.bat
```

### OR Activate on PowerShell:
```bash 
.\venv\Scripts\Activate.ps1
```

(When activated, your terminal prompt will show (venv) at the beginning or end of the line).

### 4. Install Dependencies
With your virtual environment active, install the required Pyrogram and cryptographic libraries:

```bash
pip install -r requirements.txt
```

(Note: tgcrypto is included in the requirements. It is written in C and speeds up Pyrogram's MTProto media encryption/decryption speeds by up to 400%).



## Step-by-Step Usage & Menu Walkthrough
### Step 1: Launch the Script
Make sure your virtual environment is active, then start the master script:

```bash
python master_cloner_V2.py
```

### Step 2: First-Time Authentication
If this is your first time running the script in this directory, it will initiate an interactive onboarding sequence:

1. **Enter API_ID:** Paste your integer ID from my.telegram.org.

2. **Enter API_HASH:** Paste your alphanumeric hash string.

3. Pyrogram will then prompt for your Telegram phone number (including country code, e.g., +1234567890).

4. Enter the login confirmation code sent to your Telegram app.

5. If your account has Two-Factor Authentication (2FA) enabled, enter your password when prompted.

Once authenticated, Pyrogram generates a local session file named cloner_session.session. You will never need to log in again on subsequent runs unless you manually delete this file.

### Step 3: Navigating the CLI Menu
Upon launch, you will see the interactive command menu:

```bash
1. List Chats & IDs
2. Add Channel Pair (For Saved List)
3. Run Saved Multiple Cloner
4. Run Single-Time Cloner
5. Exit
```

### Mode 1: List Chats & IDs
* What it does: Scans your Telegram account's active dialogs (up to the recent limit) and prints them to the terminal.

* How to use: Select 1. Scroll through the terminal output to find the exact names of your source and destination channels. Copy their full ID numbers (e.g., -100...) to your clipboard or a notepad.

### Mode 2: Add Channel Pair (For Saved List)
* What it does: Appends a [source_id, destination_id] mapping into your local config.json file for automated batch cloning.

* How to use: Select 2. Paste your Source Chat ID and press Enter. Then paste your Destination Chat ID and press Enter. You can run Option 2 multiple times to queue up as many channel pairs as you want.

### Mode 3: Run Saved Multiple Cloner
* What it does: Automatically loops through every channel pair saved in your config.json file and executes the cloning pipeline sequentially.

* How to use: Select 3. The script will ask one verification question upfront:

```bash 
Clone all saved pairs from scratch? (y/n):
```

* Type n (Normal / Resume Sync): The script checks your local disk for a file named last_id_{source}.txt. It reads the last cloned message ID and instructs Telegram to only download messages newer than that checkpoint. This saves massive amounts of time and data.

* Type y (Force Reset Sync): The script ignores existing tracking files and clones the entire message history of every configured channel starting from message ID 1.

### Mode 4: Run Single-Time Cloner
* What it does: Executes an ad-hoc, one-off migration without adding the IDs to your permanent config.json file.

* How to use: Select 4. Enter the Source ID, enter the Destination ID, and answer y/n for whether you want to clone from scratch. The script will sync the chat immediately and discard the IDs from memory once finished.

### Mode 5: Exit
* What it does: Closes the Pyrogram MTProto socket cleanly and terminates the Python process.
	
## Local File Storage Architecture
As you use the cloner, it will generate local tracking files inside your project directory (TG_Chat_Cloner/). Here is where they are located and what they do:

```bash
TG_Chat_Cloner/
│
├── master_cloner_V2.py       # Main application script
├── requirements.txt          # Python dependencies
├── .gitignore                # Protects secrets from being pushed to GitHub
│
├── cloner_session.session    # [GENERATED] Your encrypted Telegram login token
├── config.json               # [GENERATED] Stores your API keys and saved channel pairs
└── last_id_100123456789.txt  # [GENERATED] Progress checkpoint (stores last copied msg ID)
```
## ⚠️ Technical Notes & Warnings:
* Anti-Spam Cooldown: The script enforces a strict 3-second sleep (await asyncio.sleep(3)) after every successful message transfer. Do not remove or shorten this delay. Attempting to blast media to Telegram without throttling will trigger algorithmic anti-spam defenses, resulting in severe FloodWait penalties or account restrictions.

* Reversing History: Telegram's API serves message history from newest to oldest by default. To prevent your destination channel from being built backwards, the cloner caches the unread message IDs in memory and reverses the list before uploading, guaranteeing chronological integrity.

* Git Privacy: The .gitignore file is pre-configured to block .session, .json, and .txt files. Never force-push or upload your cloner_session.session file to GitHub or share it with anyone, as it grants full access to your Telegram account.

## Security & Complete Deletion Guide
If you are running this script on a shared computer, a cloud VPS, or simply want to remove all traces of your account from the application, follow this 3-step cleanup sequence:

### Step 1: Exit the Application
If the script is running, press Ctrl + C in your terminal or select Option 5 from the menu to close the active socket.

### Step 2: Wipe Local Session and Tracking Files
Open your terminal inside the project directory and delete the generated configuration, session tokens, and progress trackers:

**On Linux / macOS:**

```bash
rm -f *.session *.session-journal *.txt config.json
```

**On Windows (Command Prompt):**

```bash
del /f /q *.session *.session-journal *.txt config.json
```

**On Windows (PowerShell):**

```bash
Remove-Item *.session, *.session-journal, *.txt, config.json -ErrorAction SilentlyContinue

```

(Once deleted, your local folder is completely clean and retains no memory of your account or API keys).

### Step 3: Revoke Access from Telegram (Kill Active Session)
Even after deleting local files, the MTProto authorization hash remains technically valid on Telegram's servers until revoked. To permanently terminate the session:

1. Open the official Telegram app on your phone or desktop.

2. Navigate to Settings → Devices (or Active Sessions).

3. Look through the list of active devices for an entry matching your system (often labeled with your API ID name, Pyrogram, or your operating system like Windows / macOS / Linux with the current timestamp).

4. Tap on that session and select Terminate Session (or Log Out).

Your Telegram account is now completely unlinked, revoked, and removed from the cloner.
