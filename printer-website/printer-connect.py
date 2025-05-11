import time
import win32api
import os
import shutil
import PyPDF2
import json

from win32print import EnumPrinters, PRINTER_ENUM_LOCAL, PRINTER_ENUM_CONNECTIONS, GetPrinter
from time import sleep
from watchdog.events import FileSystemEvent, FileSystemEventHandler, DirCreatedEvent, FileCreatedEvent, FileDeletedEvent
from watchdog.observers import Observer

PRINTER_NAME: str = ""
PRINTER_NO: int = 0

UPLOAD_BASE_DIR = r".\\usr\\uploaded\\"
PROCESS_BASE_DIR = r".\\usr\\processed\\"

SPOOL_FILE_TRACKING = r"C:\\Windows\\System32\\spool\\PRINTERS"

FILE_PRINT_FAILED = 0
FILE_PRINT_SUCCESSFUL = 1
FILE_PRINT_NOT_FOUND = 2

DEVMODE = None

def init() -> None:
    print("Initializing watcher...")
    
    printers = EnumPrinters(PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS)
    
    for index, printer in enumerate(printers):
        global PRINTER_NAME
        global PRINTER_NO
        print(printer[2])
        if 'Microsoft' in printer[2]:
            PRINTER_NO = index
            PRINTER_NAME = printer[2]
            break  
    
    if not PRINTER_NAME:
        print("Printer not found...")
    else:
        print(f"Printer found: Now using {PRINTER_NAME}")
       
        printer_info = GetPrinter(PRINTER_NAME, 2)
        
        global DEVMODE
        DEVMODE = printer_info["pDevMode"]
        
    failed = True
    dir_list = os.listdir(UPLOAD_BASE_DIR) 
    for dir in dir_list:
        print(f"========== Debugging initializing ========== ({dir})\n")
        response = print_files_in_dir(dir_name = os.path.join(UPLOAD_BASE_DIR, dir))    
        if response == FILE_PRINT_SUCCESSFUL:
            print(f"File printed successfully: {dir}")
            failed = False
        elif response == FILE_PRINT_FAILED:
            print(f"File failed to print: {dir}")
        elif response == FILE_PRINT_NOT_FOUND:
            print(f"Files and/or Directories not found: {dir}")
        else:
            print("Error during processing `print_files_in_dir()`")
    if not failed:            
        print("Finished initializing. Upload directory is now empty.")
    return


class MyEventHandler(FileSystemEventHandler):
    def on_any_event(self, event: FileSystemEvent) -> None:
        if type(event) == DirCreatedEvent:
            sleep(5) ## Wait for the file to be uploaded :)))
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
    color = None
    copies = None
    pages = None
    '''
    Weird way to maneuver but it works for
    now.
    '''
    
    if not os.path.exists(dir_name):
        return FILE_PRINT_NOT_FOUND
    
    file_list = os.listdir(dir_name)
    
    if len(file_list) == 0:
        print(f"No files found in {dir_name}")
        print(f"Deleting {dir_name}")
        shutil.rmtree(dir_name)
        return FILE_PRINT_NOT_FOUND
    
    target_path = os.path.join(PROCESS_BASE_DIR, os.path.basename(dir_name))
    if not os.path.exists(target_path):
        os.mkdir(target_path)
    
    for file_name in file_list:
        if file_name == "settings.json":
            
            with open(file_name) as settings_data:
                d = json.loads(settings_data)
                copies = d['copies']
                pages = d['pages']
                color = d['colors']
                
                DEVMODE.Duplex = color
            shutil.move(os.path.join(dir_name, file_name), 
                        os.path.join(target_path, file_name))
            continue
        print(f"Printing {file_name}")
        response = True
        for _ in range(copies):
            print_status = execute_print(dir_name, file_name)
            response &= print_status['status']
        sleep(4)
        
        if response == False:
            failed = True
            print(f"Error while printing {file_name} at {dir_name}")
            
        elif response == True:
            shutil.move(os.path.join(dir_name, file_name), 
                        os.path.join(target_path, file_name))   
        
        print("--- Finished a file ---\n\n")
    
    if not failed or not len(file_list):
        print(f"Finished printing from {dir_name}")
        print(f"Deleting {dir_name}")
        shutil.rmtree(dir_name)
        
    elif failed:
        print(f"""\t Error while trying to print one of the files in {dir_name}.\n
                  \t All files will be automatically the nex time the server is restarted.""")
    return FILE_PRINT_SUCCESSFUL
     
def pdf_file_len(file_path: str) -> int:
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    except Exception as e:
        print(e)
        return -1
    
def execute_print(path_name: str, file_name: str):
    file_path = os.path.join(path_name, file_name)
    file_pages = pdf_file_len(file_path)
    
    if file_pages == -1:
        return {'status': False, 'error': "Document is not valid. Pages returned is -1.\n"}
    
    print(f"File Path: {file_path}\nTotal length of document in pages: {file_pages}")
    try:
        win32api.ShellExecute(
            0,
            "printto",
            file_path,
            f'"{PRINTER_NAME}"',
            ".",
            0
        )
        sleep(4 * file_pages)
        return {'status': True}
    except Exception as e:
        return {'status': False, 'error': f"{e}"}
    
def main():
    event_handler = MyEventHandler()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_BASE_DIR, recursive=True)
    observer.start()
    
    try:
        while True:
            sleep(1)
                
    finally:
        observer.stop()
        observer.join()

if __name__ == '__main__':
    print("Script is starting...")
    init()
    main()