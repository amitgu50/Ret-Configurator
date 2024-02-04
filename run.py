import tkinter as tk
from tkinter import filedialog
import ChooseRMOD
import DevicesEditor
import pandas as pd
import FindDevices
from CreateOutputFile import CreateOutputFile_function
import subprocess
import platform

root = tk.Tk()
root.title("RET CONFIGURATOR")
root.geometry(f'{root.winfo_screenwidth()}x{int(root.winfo_screenheight())-75}')
root.config(bg='grey20')

rc = tk.Label(root, text="RET CONFIGURATOR", font =("Courier", 20), bg='grey20', fg="white")
rc.pack(pady=8)
# ASCII art
ascii_art = """
######@@####################@@@@################@@@###@@#########@@#############
######%=@#@@@@@@@@@@@@@##@*=---=+%############@===%##%=+@########%+#############
######@-=%#@@@@@@@@@@@@#%-::----:-+@#########%-:-*@##*:-@#######@=-%############
######@---%##@@@@@@@@@#*-:=*@@@%+-:+@#######*-:-%####*:=@#######@+:=@###########
######@----*##@@@@@@@#@-:=@######*--*######*-:=@#####*:=@########@--*###########
######@-----+@#@@@@@@#+:-@#@######+:=@###@+::+@#@@@@#*:=@#########+:=@##########
######@--%=:-+@#@@@@#@=:*#########@--%##@=:-+@##@@@@#*:=@#########@-:*##########
######@--%@+-:=@#@@@#@--%#########@=:*#%=:-*####@@@@#*:=@##########*:-@#########
######@--%#@*-:-%#@@#@--%##########=:*#*:-=@###@@@@@#*:=@####@@@@@@@%--%########
######@--%####%-:-*##@=:+#########%--%###%-:-%#@@@@@#*:=@###*-=======--=@#######
######@--%#####%=:-+@#*:-%#######@=:=@#@@#%-:-*##@@@#*:=@##@-:----------*#######
######@--%######@=::+@@=:-*@####%=:-%#@@@@#@=:-*##@@#*:=@##+:-%%%%%%%%+:=@######
######@--%#######@+--@#@=:-=+**=-:-*##@@@@@#@+:-+@#@#*:=@#%--*########@-:*######
######@--%#########*-@##@+-:::::-=%###@@@@@@#@+-:=@##*:-@@=:=@#@@@@@@@#*:-@#####
######@**@##########%@#@##@%*++*%@####@@@@@@@##%**%@@@*%@@**@#@@@@@@@@@@%*@@@@@@
###################@##@@@@############@@@@@@@@#####@@###@####@@@@@@@@@@####@@@@@

UNOFFICIAL Version 5.0
"""

# Use a Label widget to display the ASCII art with a monospace font
label = tk.Label(root, text=ascii_art, font=("Courier", 12), padx=10, pady=10, bg='grey20', fg="white")
label.pack(pady=10)
# Centering the window on the screen
window_width = 650
window_height = 550
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width / 2) - (window_width / 2)
y = (screen_height / 2) - (window_height / 2)
root.geometry(f'{root.winfo_screenwidth()}x{int(root.winfo_screenheight())-75}')

xls = pd.ExcelFile('Values.xlsx')
modified_dfs = {}
for sheet_name in xls.sheet_names:
    df = xls.parse(sheet_name)
    df = df.astype(str)
    modified_dfs[sheet_name] = df
with pd.ExcelWriter('Values.xlsx') as writer:
    for sheet_name, df in modified_dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

la = tk.StringVar()
la.set("Upload your XML file with detected RET by pressing this button")

def handle_device_editor(DEVICES):
    filename = CreateOutputFile_function(DEVICES)
    # Open File Location Button
    description_label.config(fg="green")
    la.set("Your Output XML File Is Ready")
    # open_file_button = tk.Button(root, text="Open File Location", command=open_file_location, width=20)
    browse_button.config(command=lambda: open_file_location(filename), text="Open File Location", fg="green")
    finish_label = tk.Label(root, text="please close window.", font=("Arial", 13), fg="red", bg="grey20")
    finish_label.pack(pady=10)
    print("finished")

def handle_choose_rmod(DEVICES, root):
    root.destroy()
    for device in DEVICES:
        device.Update()
    DevicesEditor.edit_device_records(DEVICES, handle_device_editor)

file_selected = False

def choose_XML():
    global file_selected
    if not file_selected:
        file_path = filedialog.askopenfilename()
        DEVICES = FindDevices.FindDevices_function(file_path)
        file_selected = True
        ChooseRMOD.Choose_Rmod_Function(DEVICES, handle_choose_rmod)

def open_file_location(filename):
    file_path = filename
    if platform.system() == "Darwin":  # macOS
        subprocess.run(["open", "-R", file_path])
    elif platform.system() == "Windows":  # Windows
        # Convert forward slashes to backward slashes for Windows path
        file_path = file_path.replace("/", "\\")
        subprocess.run(f'explorer /select,{file_path}', shell=True)


# Description
description_label = tk.Label(root, textvariable=la, font=("Arial", 19), bg='grey20', fg="white")
description_label.pack(pady=10)

# Browse Button
browse_button = tk.Button(root, text="BROWSE", command=choose_XML, width=20, bg='white', fg="grey20")
browse_button.pack(pady=5)



root.mainloop()