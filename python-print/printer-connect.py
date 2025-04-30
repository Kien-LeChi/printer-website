import time
import win32print
import win32api
import os
from watchdog.events import FileSystemEvent, FileSystemEventHandler, DirCreatedEvent
from watchdog.observers import Observer

PRINTER_NAME = None
PRINTER_NO = 0

def init() -> None:
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    
    for index, printer in enumerate(printers):
        if 'USB' in printer[2]:
            PRINTER_NO = index
            PRINTER_NAME = printer[2]
            break      
    return
class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        if type(event) == DirCreatedEvent:
            print(event)
            response = print_files_in_dir(dir_path = event.src_path, dir_name=event.dest_path)
            
            if response == True:
                print("File printed successfully")
            elif response == False:
                print("File failed to print.")
            else:
                print("Error during processing `print_files_in_dir()`")
            
def print_files_in_dir(dir_path: str, dir_name: str) -> bool:
    abs_path = os.path.abspath(dir_path)
    if os.path.exists(abs_path):
        print("Printing files...")
        for filename in os.listdir(dir_path):
            try:
                win32api.ShellExecute(
                    0,
                    "printto",
                    abs_path,
                    f'"{PRINTER_NAME}"',
                    ".",
                    0
                )
                return True
            except Exception as error:
                print(f"Error while trying to print: {error}")
                return False
            
    pass


def main():
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == '__main__':
    init()
    main()