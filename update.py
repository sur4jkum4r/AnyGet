import os
import sys
import subprocess
import shutil

print("🔄 Updating AnyGet...")

# Backup old files (optional)
if not os.path.exists("backup"):
    os.makedirs("backup")
files = ["AnyGet.py", "update.py", "lang.json", "success.mp3"]
for f in files:
    if os.path.exists(f):
        shutil.copy(f, f"backup/{f}")

# Clone latest repo to temp folder
if os.path.exists("temp_update"):
    shutil.rmtree("temp_update")

os.system("git clone https://github.com/sur4jkum4r/AnyGet.git temp_update")

# Overwrite old files with new files
for f in files:
    src = f"temp_update/{f}"
    if os.path.exists(src):
        shutil.copy(src, f)
        print(f"✅ Updated: {f}")

# Clean temp folder
shutil.rmtree("temp_update")

print("✨ Update complete! Please restart AnyGet.")
