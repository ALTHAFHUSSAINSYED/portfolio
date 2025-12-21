import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

JSON_FILE = "portfolio_data.json"
BLOG_DIR = "generated_blogs"

class DataSyncHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(JSON_FILE):
            print(f"\n⚡ {JSON_FILE} changed. Syncing Resume & Projects...")
            subprocess.run(["python3", "backend/populate_vector_db_new.py"]) # Resume
            subprocess.run(["python3", "backend/sync_projects.py"])          # Projects (Mongo+Chroma)

        elif BLOG_DIR in event.src_path and event.src_path.endswith(".json"):
            print(f"\n⚡ Blog update detected. Syncing Blogs...")
            subprocess.run(["python3", "backend/migrate_local_blogs_new.py"])

if __name__ == "__main__":
    print("👀 Watcher Started. Waiting for changes...")
    event_handler = DataSyncHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
