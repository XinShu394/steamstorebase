import os
import shutil
import time
import subprocess
import sqlite3
import json
from pathlib import Path

# Setup paths
DATA_DIR = Path("data")
SNAPSHOT_SRC = DATA_DIR / "app_list_manual_test.json"
SNAPSHOT_DST = DATA_DIR / "app_list_verification.json"

def setup():
    print("Setting up test environment...")
    # Clean DBs
    for db in ["steam_data.db", "tasks.db"]:
        path = DATA_DIR / db
        if path.exists():
            try:
                os.remove(path)
                print(f"Removed {db}")
            except Exception as e:
                print(f"Warning: Could not remove {db}: {e}")

    # Remove any existing app_list_verification.json
    if SNAPSHOT_DST.exists():
        os.remove(SNAPSHOT_DST)

    # Create snapshot
    if SNAPSHOT_SRC.exists():
        shutil.copy(SNAPSHOT_SRC, SNAPSHOT_DST)
        print(f"Created snapshot {SNAPSHOT_DST}")
    else:
        print("Error: Source snapshot not found!")

def check_results():
    print("\nChecking results...")
    
    # Check Tasks DB
    tasks_db = DATA_DIR / "tasks.db"
    if tasks_db.exists():
        conn = sqlite3.connect(tasks_db)
        cursor = conn.cursor()
        cursor.execute("SELECT app_id, status FROM tasks")
        tasks = cursor.fetchall()
        print(f"Tasks found: {len(tasks)}")
        for task in tasks:
            print(f"  AppID: {task[0]}, Status: {task[1]}")
        conn.close()
    else:
        print("Error: tasks.db not found!")

    # Check Games DB
    games_db = DATA_DIR / "steam_data.db"
    if games_db.exists():
        conn = sqlite3.connect(games_db)
        cursor = conn.cursor()
        cursor.execute("SELECT steam_appid, name, type FROM games")
        games = cursor.fetchall()
        print(f"Games found: {len(games)}")
        for game in games:
            print(f"  AppID: {game[0]}, Name: {game[1]}, Type: {game[2]}")
        conn.close()
    else:
        print("Error: steam_data.db not found!")

def run_crawler():
    print("\nRunning crawler (timeout 25s)...")
    try:
        # Run module src.main
        proc = subprocess.Popen(
            ["python", "-m", "src.main"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8', # Ensure correct encoding for Chinese logs if any
            errors='replace'
        )
        
        try:
            outs, errs = proc.communicate(timeout=25)
        except subprocess.TimeoutExpired:
            print("Timeout reached, stopping crawler...")
            proc.terminate()
            try:
                outs, errs = proc.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                outs, errs = proc.communicate()
            
        print("Crawler output sample (last 1000 chars):")
        print(outs[-1000:] if outs else "No stdout") 
        if errs:
            print("Crawler errors:")
            print(errs)
            
    except Exception as e:
        print(f"Error running crawler: {e}")

if __name__ == "__main__":
    setup()
    run_crawler()
    check_results()
