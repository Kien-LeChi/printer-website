import time  
import win32api
import os

from time import sleep
from watchdog.events import FileSystemEvent, FileSystemEventHandler, FileCreatedEvent, FileDeletedEvent
from watchdog.observers import Observer

SPOOL_DIR = r"C:\\Windows\\System32\\spool\\PRINTERS\\"


class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        if type(event) == FileCreatedEvent:
            print("New file found in spool")
            print(event, "\n\n")

        elif type(event) == FileDeletedEvent:
            print("File deleted from spool")
            print(event, "\n\n");
            

def main():
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, SPOOL_DIR, recursive=True)
    observer.start()

    try:
        while True:
            sleep(1)

    finally:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()
