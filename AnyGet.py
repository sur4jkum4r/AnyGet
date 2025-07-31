import os
import sys
import shutil
import subprocess
import requests
import csv
import time
from datetime import datetime
from colorama import init, Fore
from pyfiglet import Figlet
from tqdm import tqdm
import json

try:
    from playsound import playsound
except ImportError:
    subprocess.call([sys.executable, "-m", "pip", "install", "playsound"])
    from playsound import playsound

init(autoreset=True)

LOCAL_VERSION = "1.0.0"
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "Assets")
VERSION_FILE = os.path.join(ASSETS_DIR, "version.txt")
SUCCESS_SOUND = os.path.join(ASSETS_DIR, "success.mp3")

# ================================
# Load Language
# ================================
def load_lang():
    if os.path.exists('lang.json'):
        with open('lang.json', 'r') as f:
            lang = json.load(f)
    else:
        lang = {
            "thank_you": "✨ Thank you for using AnyGet! Have a great day! ✨",
            "about": "📢 ABOUT",
            "contact": "Contact",
            "location": "Location",
            "created_by": "Created by",
            "tool_name": "Tool Name"
        }
    return lang

LANG = load_lang()

# ================================
# Center helper
# ================================
def center_text(text):
    term_width = os.get_terminal_size().columns
    lines = text.split('\n')
    centered = '\n'.join(line.center(term_width) for line in lines)
    return centered

# ================================
# Banner & info
# ================================
def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    fig = Figlet(font='slant')
    banner = fig.renderText("AnyGet")
    print(Fore.YELLOW + center_text(banner))
    creator = f"{LANG['created_by']}: Suraj Prajapati x ChatGPT"
    print(Fore.GREEN + center_text(creator))
    print(Fore.WHITE + center_text("─" * 60))
    print(Fore.CYAN + center_text("AnyGet: Powerful CLI Downloader for Video, Audio & Files"))
    print(Fore.CYAN + center_text("Safe 4K default, Ultra Best for power users, Manual for pros"))
    print(Fore.CYAN + center_text("Open Source • Apache 2.0 • By Suraj for the world ❤️"))
    print(Fore.WHITE + center_text("─" * 60) + "\n")

# ================================
# Init log
# ================================
def init_log():
    if not os.path.exists('AnyGet'):
        os.mkdir('AnyGet')
    if not os.path.exists('AnyGet/history'):
        os.makedirs('AnyGet/history')
    if not os.path.exists('AnyGet/history/downloader_history.csv'):
        with open('AnyGet/history/downloader_history.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Date', 'Time', 'Type', 'URL', 'Status', 'FileSize'])

# ================================
# Update log
# ================================
def update_log(entry):
    with open('AnyGet/history/downloader_history.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(entry)

# ================================
# Storage info
# ================================
def show_storage_info():
    try:
        if os.name == 'nt':
            path = "C:\\"
        else:
            path = os.path.expanduser("~")
        total, used, free = shutil.disk_usage(path)
        print(Fore.YELLOW + "📂 STORAGE INFO")
        print(f"   • Total : {total // (2**30)} GB")
        print(f"   • Used  : {used // (2**30)} GB")
        print(f"   • Free  : {free // (2**30)} GB\n")
    except Exception as e:
        print(Fore.RED + f"❌ Could not get storage info: {e}")

# ================================
# Version check
# ================================
def check_version():
    try:
        remote_url = "https://raw.githubusercontent.com/sur4jkum4r/AnyGet/main/Assets/version.txt"
        remote = requests.get(remote_url).text.strip()
        if LOCAL_VERSION != remote:
            print(f"\n🔔 Update available! Local: {LOCAL_VERSION} → Remote: {remote}")
            update = input("⚡ Do you want to update now? (y/n): ").lower()
            if update == 'y':
                subprocess.call([sys.executable, "update.py"])
                sys.exit()
        else:
            print(Fore.GREEN + "✅ You have the latest version.\n")
    except Exception as e:
        print(Fore.RED + f"⚠️ Could not check update: {e}")

# ================================
# URL checker
# ================================
def get_valid_url():
    attempts = 0
    while attempts < 3:
        url = input(Fore.CYAN + "🔗 Enter URL: ").strip()
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            if r.status_code < 400:
                size = r.headers.get('Content-Length', None)
                if size:
                    size_mb = round(int(size) / (1024 * 1024), 2)
                    print(Fore.GREEN + f"✅ Approx File Size: {size_mb} MB")
                else:
                    print(Fore.YELLOW + "ℹ️  File size not available.")
                return url
            else:
                print(Fore.RED + "❌ URL not reachable. Try again.")
        except:
            print(Fore.RED + "❌ Invalid URL or No Response. Try again.")
        attempts += 1

    print(Fore.RED + "\n🚫 Invalid URL entered 3 times. Please raise an issue on GitHub & stay tuned for update.")
    clean_exit()

# ================================
# Download content with yt-dlp format select
# ================================
def download_content(content_type, url):
    folder = f"AnyGet/Downloads/{content_type}s"
    os.makedirs(folder, exist_ok=True)

    custom_name = input(Fore.YELLOW + "📁 Do you want custom file name? (y/n): ").lower()
    if custom_name == 'y':
        local_filename = input("📝 Enter custom name (without extension): ")
    else:
        local_filename = url.split("/")[-1].split("?")[0]
        if not local_filename:
            local_filename = "AnyGet_File"

    filepath = os.path.join(folder, local_filename)

    try:
        if content_type == "Video":
            print(Fore.CYAN + "\n🌟 Mode: [1] Safe Best (4K max)  [2] Ultra Best  [3] Manual Codes\n")
            mode = input(Fore.YELLOW + "👉 Select Mode [1/2/3]: ")

            if mode == '1':
                subprocess.call(['yt-dlp', '-f', 'bestvideo[height<=2160]+bestaudio', '-o', f"{filepath}.%(ext)s", url])
            elif mode == '2':
                subprocess.call(['yt-dlp', '-f', 'bestvideo+bestaudio', '-o', f"{filepath}.%(ext)s", url])
            elif mode == '3':
                subprocess.call(['yt-dlp', '-F', url])
                format_code = input(Fore.YELLOW + "👉 Enter format code (e.g., 137+140): ").strip()
                subprocess.call(['yt-dlp', '-f', format_code, '-o', f"{filepath}.%(ext)s", url])
            else:
                print(Fore.RED + "❌ Invalid mode selected.")

        else:
            r = requests.get(url, stream=True)
            total = int(r.headers.get('content-length', 0))
            with open(filepath, 'wb') as f, tqdm(
                desc=local_filename,
                total=total,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in r.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)

        print(Fore.GREEN + f"✅ Download complete: {filepath}")
        if os.path.exists(SUCCESS_SOUND):
            playsound(SUCCESS_SOUND)
        else:
            print(Fore.YELLOW + "✅ Download Successfully ✅")

    except Exception as e:
        print(Fore.RED + f"❌ Error: {str(e)}")
        print(Fore.YELLOW + "📢 Please raise an issue on GitHub & stay tuned for next update.")

# ================================
# Clean exit
# ================================
def clean_exit():
    print(Fore.CYAN + f"\n{LANG['thank_you']}\n")
    time.sleep(3)
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit()

# ================================
# Start point
# ================================
def start_downloader():
    while True:
        print(Fore.CYAN + "🌟 What do you want to download?")
        print("  [1] Video")
        print("  [2] Audio")
        print("  [3] Image")
        print("  [4] Any File")
        print("  [5] About Tool")
        print("  [6] Check for Updates")
        print("  [0] Exit\n")

        choice = input(Fore.YELLOW + "👉 Your Choice: ")

        if choice == '0':
            clean_exit()
        elif choice == '5':
            print(Fore.YELLOW + f"\n{LANG['about']}")
            print(f"   • {LANG['tool_name']}: AnyGet")
            print(f"   • {LANG['created_by']}: Suraj Prajapati x ChatGPT")
            print(f"   • Powerful open-source downloader for videos, audios, images & files.")
            print(f"   • Safe merge with 4K max, Ultra Best for power users, Manual for pro coders.")
            print(f"   • License: Apache 2.0 — free to use, fork & modify!")
            print(f"   • {LANG['contact']}: sur4jkum4r.org@gmail.com")
            print(f"   • {LANG['location']}: Ahmedabad, India\n")
        elif choice == '6':
            check_version()
        elif choice in ['1', '2', '3', '4']:
            type_map = {'1': 'Video', '2': 'Audio', '3': 'Image', '4': 'AnyFile'}
            urls = []
            batch = input(Fore.CYAN + "🌐 Do you want to download multiple URLs? (y/n): ").lower()
            if batch == 'y':
                count = int(input("🔢 How many URLs?: "))
                for i in range(count):
                    print(f"\nURL {i+1}:")
                    url = get_valid_url()
                    urls.append(url)
            else:
                url = get_valid_url()
                urls.append(url)

            for url in urls:
                try:
                    download_content(type_map[choice], url)
                    status = "Success"
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {str(e)}")
                    print(Fore.YELLOW + "📢 Please raise an issue on GitHub & stay tuned for next update.")
                    status = "Failed"

                now = datetime.now()
                update_log([
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    type_map[choice],
                    url,
                    status,
                    "See above"
                ])

            again = input(Fore.YELLOW + "\n🌟 Do you want to download more? (y/n): ").lower()
            if again != 'y':
                clean_exit()
        else:
            print(Fore.RED + "❌ Invalid choice. Please select again.")

# ================================
# MAIN
# ================================
def main():
    show_banner()
    check_version()
    init_log()
    show_storage_info()
    start_downloader()

if __name__ == "__main__":
    main()
