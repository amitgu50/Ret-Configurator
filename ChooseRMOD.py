import tkinter as tk
from tkinter import ttk
from DeviceClass import Device

def Choose_Rmod_Function(DEVICES, callback=None):
    def select_record(event):
        selected_item = device_table.selection()[0]
        item_data = device_table.item(selected_item)
        ant_model, serial_number, rmod, sector = item_data['values']
        fill_entry_fields(ant_model, serial_number, rmod, sector)

    def fill_entry_fields(ant_model, serial_number, rmod, sector):
        names = [ant_model, serial_number, rmod, sector]
        clear_entry_fields()
        for i in range(4):
            readonly = False
            if entry_fields[i]['state'] == 'readonly':
                readonly = True
            entry_fields[i].config(state="normal")
            entry_fields[i].delete(0, tk.END)
            entry_fields[i].insert(0, names[i])
            if readonly:
                entry_fields[i].config(state="readonly")

    def clear_entry_fields():
        for entry in entry_fields:
            entry.delete(0, tk.END)

    def update_record():
        selected_item = device_table.selection()[0]
        item_data = device_table.item(selected_item)
        ant_model, serial_number, rmod, sector = [entry.get() for entry in entry_fields]

        # Update the DEVICES object with the new sector value
        for device in DEVICES:
            if device.rmod == rmod:
                device.sector = sector

        device_table.item(selected_item, values=(ant_model, serial_number, rmod, sector))
        device.Update()

    def done():
        if callback:
            callback(DEVICES, root)
        root.destroy()

    root = tk.Tk()
    root.title('Match RMOD And SECTOR')
    root.geometry(f'{root.winfo_screenwidth()}x{int(root.winfo_screenheight())-75}')
    root.configure(bg='grey20')

    device_frame = tk.Frame(root, bg='grey20')
    device_frame.pack(fill='both', expand=True)

    device_scroll = tk.Scrollbar(device_frame)
    device_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    device_table = ttk.Treeview(device_frame, yscrollcommand=device_scroll.set)
    device_table.pack(fill='both', expand=True)

    device_scroll.config(command=device_table.yview)

    device_table['columns'] = ("Ant Models", "Serial Numbers", "RMOD", "Sector")

    for attribute in device_table['columns']:
        device_table.column(attribute, anchor=tk.CENTER, width=100)
        device_table.heading(attribute, text=attribute, anchor=tk.CENTER)
    
    label = tk.Label(root, text="Pick a row, modify the Sector if required, and press Apply to save changes\n\nAt the end - press Finish ", font=('Helvetica 20'), bg="grey20", fg="white")
    label.pack(pady=10)  # adding some padding for better visual spacing

    entry_frame = tk.Frame(root, bg='grey20')
    entry_frame.pack(fill='both', pady=20)

    entry_labels = ["Ant Model", "Serial Number", "RMOD", "Sector"]
    entry_fields = []

    for i, label in enumerate(entry_labels):
        tk.Label(entry_frame, text=label, bg='grey20', fg='white').grid(row=0, column=i)
        entry = tk.Entry(entry_frame, font=("Helvetica", 12))
        entry.grid(row=1, column=i, padx=5, pady=5, sticky='nsew')
        if not (label == "Sector"):
            entry.config(state='readonly')
        else:
            entry.config(bg="green")
        entry_fields.append(entry)

    for i in range(len(entry_labels)):
        entry_frame.grid_columnconfigure(i, weight=1)

    apply_button = tk.Button(root, text="Apply", command=update_record, font=("Helvetica", 12))
    apply_button.pack(pady=10)

    done_button = tk.Button(root, text="Finish", command=done, font=("Helvetica", 12))
    done_button.pack(pady=10)

    device_table.bind("<ButtonRelease-1>", select_record)

    # Create a dictionary to store device data grouped by RMOD
    devices_by_rmod = {}

    # Populate the devices_by_rmod dictionary
    for device in DEVICES:
        rmod = device.rmod
        if rmod not in devices_by_rmod:
            devices_by_rmod[rmod] = {
                "ant_models": [],
                "serial_numbers": [],
                "sectors": device.sector  # Initialize with the first sector value
            }
        devices_by_rmod[rmod]["ant_models"].append(device.antModel)
        devices_by_rmod[rmod]["serial_numbers"].append(device.serialNumber)

    # Populate the device table with device data grouped by RMOD
    for rmod, data in devices_by_rmod.items():
        ant_models = ', '.join(data["ant_models"])
        serial_numbers = ', '.join(data["serial_numbers"])
        device_table.insert(parent='', index='end', values=(ant_models, serial_numbers, rmod, data["sectors"]))

    root.mainloop()

# Example usage:
# device_objects = [Device(...), Device(...)]
# Call the function to display and edit devices by rmod
# Choose_Rmod_Function(device_objects)
