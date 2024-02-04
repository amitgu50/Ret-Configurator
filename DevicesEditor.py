import tkinter as tk
from tkinter import ttk
from openpyxl import load_workbook
from DeviceClass import Device

# Define a function to update the table with the latest data
def update_table(device_table, devices, device_attributes):
    device_table.delete(*device_table.get_children())  # Clear the existing table
    for i, device in enumerate(devices):
        device_table.insert(parent='', index='end', iid=i, text=i, values=[getattr(device, attribute) for attribute in device_attributes])

def load_band_values():
    try:
        workbook = load_workbook('Values.xlsx')
        sheet = workbook['antmod-baseid']
        band_values = set(cell.value for cell in sheet['C'] if cell.value and not cell.value == "nan" and not cell.value == "baseStationID")
        return ["na"] + list(band_values)
    except Exception as e:
        print(f"Error loading band values: {e}")
        return ["na"]


def edit_device_records(DEVICES, callback):
    selected_item_id = None
    DEVICES = sorted(DEVICES, key =lambda device: int(device.sector))
    def select_record(event):
        nonlocal selected_item_id
        selected_item = device_table.selection()[0]
        if selected_item_id != selected_item:
            selected_item_id = selected_item
            fill_entry_fields(selected_item)

    def fill_entry_fields(selected_item):
        item_data = device_table.item(selected_item)
        device_index = item_data['text']
        device = devices[int(device_index)]
        clear_entry_fields()
        for i, attribute in enumerate(device_attributes):
            readonly = False
            if entry_fields[i]['state'] == 'readonly':
                readonly = True
            entry_fields[i].config(state="normal")
            entry_fields[i].delete(0, tk.END)
            entry_fields[i].insert(0, getattr(device, attribute))
            if readonly:
                entry_fields[i].config(state="readonly")
        entry_fields[-2].set(device.band)

    def clear_entry_fields():
        for entry in entry_fields:
            entry.delete(0, tk.END)

    def divide_antIDN_values(devices, device_table):
        antIDN_dict = {}
        for device in devices:
            antIDN = tuple(device.antIDN)
            if antIDN in antIDN_dict:
                antIDN_dict[antIDN].append(device)
            else:
                antIDN_dict[antIDN] = [device]
        for devices_with_same_antIDN in antIDN_dict.values():
            if len(devices_with_same_antIDN) > 1:
                total_values = len(devices_with_same_antIDN[0].antIDN)
                num_devices = len(devices_with_same_antIDN)
                num_values_per_device = total_values // num_devices
                remainder = total_values % num_devices
                start_index = 0
                for i, device in enumerate(devices_with_same_antIDN):
                    end_index = start_index + num_values_per_device
                    if i < remainder:
                        end_index += 1 
                    new_antIDN = list(devices_with_same_antIDN[i].antIDN[start_index:end_index])
                    device.antIDN = new_antIDN
                    device_index = devices.index(device)
                    device_table.item(device_index, values=[getattr(device, attribute) for attribute in device_attributes])
                    start_index = end_index

    def update_record():
        selected_item = device_table.selection()[0]
        item_data = device_table.item(selected_item)
        device_index = item_data['text']
        device = devices[int(device_index)]
        for i, attribute in enumerate(device_attributes):
            setattr(device, attribute, entry_fields[i].get())
        device.band = entry_fields[-2].get() 
        device.Update()
        device_table.item(selected_item, values=[getattr(device, attribute) for attribute in device_attributes])
        for i, device in enumerate(devices):
            device.Update()
        divide_antIDN_values(devices, device_table)
        for i, device in enumerate(devices):
            device.antIdnShortcut = device.FindAntShortcut()
        for i, device in enumerate(devices):
            device_table.item(i, values=[getattr(device, attribute) for attribute in device_attributes])
    
    def OnLoad():
        divide_antIDN_values(devices, device_table)
        for i, device in enumerate(devices):
            device.antIdnShortcut = device.FindAntShortcut()
        for i, device in enumerate(devices):
            device_table.item(i, values=[getattr(device, attribute) for attribute in device_attributes])

    def done():
        divide_antIDN_values(devices, device_table)
        if callback:
            callback(devices)
        root.destroy()

    root = tk.Toplevel()
    root.title('Device Editor')
    root.geometry(f'{root.winfo_screenwidth()}x{int(root.winfo_screenheight())-75}')
    root.configure(bg='grey20')

    device_frame = tk.Frame(root, bg='grey20')
    device_frame.pack(fill='both', expand=True)

    device_scroll = tk.Scrollbar(device_frame)
    device_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    device_table = ttk.Treeview(device_frame, yscrollcommand=device_scroll.set)
    device_table.pack(fill='both', expand=True)

    device_scroll.config(command=device_table.yview)

    device_attributes = ["aldNumber", "antModel", "sector", "serialNumber", "serialID", "antIdnShortcut", "mrbtsId", "rmod", "cellid", "band", "angle"]

    device_table['columns'] = device_attributes

    for attribute in device_attributes:
        device_table.column(attribute, anchor=tk.CENTER, width=100)
        device_table.heading(attribute, text=attribute, anchor=tk.CENTER)



    devices = DEVICES

    for i, device in enumerate(devices):
        device_table.insert(parent='', index='end', iid=i, text=i, values=[getattr(device, attribute) for attribute in device_attributes])

    entry_frame = tk.Frame(root, bg='grey20')
    entry_frame.pack(fill='both', pady=20)

    entry_labels = ["ALD Number", "Ant Model", "Sector", "Serial Number", "Serial ID", "Ant IDN", "MRBTS ID", "RMOD", "Cell-ID"]
    entry_fields = []

    for i, label in enumerate(entry_labels):
        tk.Label(entry_frame, text=label, bg='grey20', fg='red').grid(row=0, column=i)
        entry = tk.Entry(entry_frame, font=("Helvetica", 12), bg="grey20", fg="red")
        entry.grid(row=1, column=i, padx=5, pady=5, sticky='nsew')
        entry.config(state='readonly')
        entry_fields.append(entry)


    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom1.TCombobox", fieldbackground="green", foreground="white")
    band_values = load_band_values()  # Load band values from Excel file
    band_label = tk.Label(entry_frame, text="Band", bg='grey20', fg='white')
    band_label.grid(row=0, column=len(entry_labels))
    band_combobox = ttk.Combobox(entry_frame, style="Custom1.TCombobox", values=band_values, font=("Helvetica", 12))
    band_combobox.grid(row=1, column=len(entry_labels), padx=5, pady=5, sticky='nsew')
    entry_fields.append(band_combobox)  # Add the combobox to entry_fields

    angle_label = tk.Label(entry_frame, text="Angle", bg='grey20', fg='white')
    angle_label.grid(row=0, column=len(entry_labels) + 1)
    angle_entry = tk.Entry(entry_frame, font=("Helvetica", 12))
    angle_entry.grid(row=1, column=len(entry_labels) + 1, padx=5, pady=5, sticky='nsew')
    angle_entry.config(bg="green")
    entry_fields.append(angle_entry)  # Add the angle entry field to entry_fields

    for i in range(len(entry_labels) + 2):  # Include the combobox and angle entry field
        entry_frame.grid_columnconfigure(i, weight=1)

    refresh_button = tk.Button(root, text="Apply", command=update_record, font=("Helvetica", 12))
    refresh_button.pack(pady=10)

    done_button = tk.Button(root, text="Finish", command=done, font=("Helvetica", 12))
    done_button.pack(pady=10)

    label = tk.Label(root, text="1. Choose a row, if needed.\n2. If required, update the Band and Angle.\n3. For unused antenna ports, set the Band to 'na'.\n4. Click 'Finish' to export the final SCF file.", font=('Helvetica 20'), bg="grey20", fg="white", anchor='w', justify='left')
    label.pack(pady=10, side="left", anchor='w') 

    device_table.bind("<ButtonRelease-1>", select_record)
    root.after(10, OnLoad)
    root.mainloop()