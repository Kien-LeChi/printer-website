import win32print
import win32ui
import win32api
import os

printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
printer_no = 0
printer_name: str = None

rel_path = "./file.pdf"
file_path = os.path.abspath(rel_path)
print(file_path)

for index, printer in enumerate(printers):
    if 'USB' in printer[2]:
        printer_no = index
        printer_name = printer[2]
       
print(f"Printer found: {printer_name}")       
       
if os.path.exists(file_path):   
    print("File exist")
    win32api.ShellExecute(
        0,
        "printto",
        file_path,
        f'"{printer_name}"',
        ".",
        0
    ) 
