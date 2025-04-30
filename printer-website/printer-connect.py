import time
import win32print
import win32api
import os
import shutil
from watchdog.events import FileSystemEvent, FileSystemEventHandler, DirCreatedEvent
from watchdog.observers import Observer

PRINTER_NAME = None
PRINTER_NO = 0

UPLOAD_BASE_DIR = r".\\usr\\uploaded\\"
PROCESS_BASE_DIR = r".\\usr\\processed\\"

FILE_PRINT_FAILED = 0
FILE_PRINT_SUCCESSFUL = 1
FILE_PRINT_NOT_FOUND = 2


def init() -> None:
    print("Initializing watcher...")
    
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    
    for index, printer in enumerate(printers):
        if 'USB' in printer[2]:
            PRINTER_NO = index
            PRINTER_NAME = printer[2]
            break  
       
    dir_list = os.listdir(UPLOAD_BASE_DIR) 
    for dir in dir_list:
        print(f"Debugging initializing: {dir}")
        response = print_files_in_dir(dir_name = os.path.join(UPLOAD_BASE_DIR, dir))    
        if response == FILE_PRINT_SUCCESSFUL:
            print(f"File printed successfully: {dir}")
        elif response == FILE_PRINT_FAILED:
            print(f"File failed to print: {dir}")
        elif response == FILE_PRINT_NOT_FOUND:
            print(f"Files and/or Directories not found: {dir}")
        else:
            print("Error during processing `print_files_in_dir()`")
            
    print("Finished initializing. Upload directory is now empty.")
    return


class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        if type(event) == DirCreatedEvent:
            print(f"New directory detected: {event.src_path}")
            abs_path = os.path.abspath(event.src_path)
            
            response = print_files_in_dir(dir_name = abs_path)
            
            if response == FILE_PRINT_SUCCESSFUL:
                print(f"File printed successfully: {abs_path}")
            elif response == FILE_PRINT_FAILED:
                print(f"File failed to print: {abs_path}")
            elif response == FILE_PRINT_NOT_FOUND:
                print(f"Files and/or Directories not found: {abs_path}")
            else:
                print("Error during processing `print_files_in_dir()`")    
            return None
        
        else:
            return None
        

def print_files_in_dir(dir_name: str) -> None:
    
    '''
    In this case, dir_name should always be the absolute path
    corresponds to the printer-connect.py script's directory.
    In this case, is printer-website.
    
    It can be the absolute path.
    '''
    
    failed: bool = False
    '''
    Weird way to maneuver but it works for
    now.
    '''
    
    if not os.path.exists(dir_name):
        return FILE_PRINT_NOT_FOUND
    
    file_list = os.listdir(dir_name)
    
    if len(file_list) == 0:
        return FILE_PRINT_NOT_FOUND
    
    target_path = os.path.join(PROCESS_BASE_DIR, os.path.basename(dir_name))
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    
    for file_name in file_list:
        print(f"Printing {file_name}")
        response = execute_print(dir_name, file_name)
        
        if response['status'] == False:
            failed = True
            print(response['error'], f"Error while printing {file_name} at {dir_name}")
            
        elif response['status'] == True:
            shutil.move(target_path, os.path.join(PROCESS_BASE_DIR, file_name))
    
    if not failed:
        print(f"Finished printing from {dir_name}")
        print(f"Deleting {dir_name}")
        shutil.rmtree(dir_name)
    elif failed:
        print(f"""\t Error while trying to print one of the files in {dir_name}.\n
                  \t All files will be automatically the nex time the server is restarted.""")
    return None
     
def execute_print(path_name: str, file_name: str):
    file_path = os.path.join(path_name, file_name)
    try:
        win32api.ShellExecute(
            0,
            "printto",
            file_path,
            f'"{PRINTER_NAME}"',
            ".",
            0
        )
        return {'status': True}
    except Exception as e:
        return {'status': True, 'error': f"{e}"}
    
def main():
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_BASE_DIR, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

if __name__ == '__main__':
    print("Script is starting...")
    init()
    main()