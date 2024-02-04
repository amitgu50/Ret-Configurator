import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, 
                             QVBoxLayout, QComboBox, QGridLayout, QMainWindow)
from PyQt5.QtGui import QPalette, QColor


class NewAntFunction(QMainWindow):
    def __init__(self, antModel, serials):
        super().__init__()
        self.serials = serials
        self.serialNumber = serials[0].serialNumber
        self.antModel = antModel

        # Call the initialization methods
        self.init_methods()
        self.initUI()

    def init_methods(self):
        self.expectedValues = ["R1", "R2", "Y1", "Y2", "Y3", "Y4", "Y5", "Y6", "B2", "B1"]
        self.usedValues = []
        self.methods = [self.method1, self.method2, self.method3, self.method4]
        self.idValue = set()
        # self.idValue.add("*Please Choose*")
        # Initialize the id_to_method dictionary
        self.id_to_method = {}  
        self.base_station_values = {
            "R1": "850",
            "R2": "700",
            "Y1": "1800",
            "Y2": "2600",
            "Y3": "GSM",
            "Y4": "2100",
            "Y5": "1800",
            "Y6": "2600",
            "B1": "1800",
            "B2": "1800",
            "a": '700+850',
            "b": '5G', 
            "c": '1800+2600',
            "d": 'GSM+1800+2100'          
        }

        self.base_station_comboboxes = {}
        self.val = list(self.base_station_values.values())
        i = 1
        for method in self.methods:
            id = method()
            if id in self.expectedValues:
                self.idValue.add(id)
                self.id_to_method[id] = str(float(i))
            i += 1
        self.idValue.add("*Please Choose*")
        self.idValue = list(self.idValue)
        # self.idValue = self.idValue[::-1]

    def method1(self):
        return self.serialNumber[-2:]

    def method2(self):
        return self.serialNumber[1:3]

    def method3(self):
        try:
            twolast = str(self.serialNumber[-2:])
            if twolast in self.expectedValues:
                return None
            self.serialDict3 = {
                "1" : "R1",
                "2" : "Y1",
                "3" : "Y2",
                "4" : "Y3"
            }
            return self.serialDict3.get(self.serialNumber[-1], None)
        except:
            return None

    def method4(self):
        return "it's a 5G Ant"

    def print_method_name(self):
        selected_id = self.idEntry.currentText()
        if not selected_id == "*Please Choose*":
            # print(str(self.id_to_method[selected_id]))
            return str(self.id_to_method[selected_id])
    
    def Change_excel_toString(self):
        xls = pd.ExcelFile('Values.xlsx')
        modified_dfs = {}
        for sheet_name in xls.sheet_names:
            df1 = xls.parse(sheet_name)
            df1 = df1.astype(str)
            modified_dfs[sheet_name] = df1
        with pd.ExcelWriter('Values.xlsx') as writer1:
            for sheet_name, df1 in modified_dfs.items():
                df1.to_excel(writer1, sheet_name=sheet_name, index=False)

    def approve_to_excel(self):
            if self.idEntry.currentText() == "*Please Choose*": 
                text_color = QColor(255, 0, 0)  # Red color, you can change it to any color you want
                self.idEntry.setStyleSheet(f"QComboBox {{ color: {text_color.name()}; }}")
            else:
            # Read the existing data from the sheet
                try:
                    df = pd.read_excel('Values.xlsx', sheet_name='antmod-baseid')
                except Exception as e:
                    # print("Sheet not found. Creating a new one.")
                    df = pd.DataFrame()
                s = set(self.usedValues)
                self.usedValues = list(s)
                for value in self.usedValues:
                    data = {
                        'antModel': self.antModel,
                        'id': value,
                        'baseStationID': self.base_station_comboboxes[value].currentText(),
                        'method': self.print_method_name()
                    }
                    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

                with pd.ExcelWriter('values.xlsx', engine='openpyxl', mode='a') as writer:
                    # Check if 'antmod-baseid' sheet exists. If it does, remove it.
                    if 'antmod-baseid' in writer.book:
                        writer.book.remove(writer.book['antmod-baseid'])
                    # Write the combined data back to the 'antmod-baseid' sheet
                    df.to_excel(writer, sheet_name='antmod-baseid', index=False)

                self.Change_excel_toString()
                self.close()
                
    
    def GetMethod(self):
        method = self.print_method_name()
        if method == '1.0':
            return self.method1()
        elif method == '2.0':
            return self.method2()
        elif method == '3.0':
            return self.method3()
        elif method == '4.0':
            return self.method4()

    def clearWidgetsFromRow(self, start_row):
        for row in range(start_row, self.grid.rowCount()):
            for col in range(self.grid.columnCount()):
                widget = self.grid.itemAtPosition(row, col)
                if widget is not None:
                    widget = widget.widget()
                    if widget is not None:
                        self.grid.removeWidget(widget)
                        widget.deleteLater()

    def uiValue(self):
        self.clearWidgetsFromRow(4)
        self.usedValues = []
        row_num = 4  # Start adding ComboBoxes from row 4
        for serial in self.serials:
            self.serialNumber = serial.serialNumber
            value = self.GetMethod()
            self.usedValues.append(value)
            label = QLabel(f"Base Station ID for {serial.serialNumber} - {value}")
            # label.set()
            self.grid.addWidget(label, row_num, 0)
            combobox = QComboBox()
            combobox.addItems(self.val)
            
            # Set the default value for the ComboBox based on the base_station_values dictionary
            default_value = self.base_station_values.get(value, None)
            if default_value is not None:
                combobox.setCurrentText(default_value)
            
            self.grid.addWidget(combobox, row_num, 1)
            self.base_station_comboboxes[value] = combobox
            row_num += 1

    def initUI(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        self.grid = QGridLayout()
        widget.setLayout(self.grid)

        # Add widgets
        description_label = QLabel("I Found This AntModel That I Can't Identify, Approve Or Edit This And I Will Add It To My Database")
        self.grid.addWidget(description_label, 0, 0, 1, 3)

        serialLabel = QLabel("Serial Number")
        self.grid.addWidget(serialLabel, 1, 0)
        self.serialEntry = QLineEdit(self.serialNumber)
        self.grid.addWidget(self.serialEntry, 2, 0)

        antLabel = QLabel("Ant Model")
        self.grid.addWidget(antLabel, 1, 1)
        self.antEntry = QLineEdit(self.antModel)
        self.grid.addWidget(self.antEntry, 2, 1)

        idLabel = QLabel("Serial ID")
        self.grid.addWidget(idLabel, 1, 2)
        self.idEntry = QComboBox()
        self.idEntry.addItems(self.idValue)
        self.idEntry.currentTextChanged.connect(self.uiValue)
        self.idEntry.setCurrentText("*Please Choose*")
        self.grid.addWidget(self.idEntry, 2, 2)

        self.uiValue()

        approve_button = QPushButton("Approve", self)
        approve_button.clicked.connect(self.approve_to_excel)
        self.grid.addWidget(approve_button, 3, 0, 1, 3)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Device Editor')
        self.show()



def NewAntApp(antModel, serials):
    app = QApplication(sys.argv)
    ex = NewAntFunction(antModel, serials)
    app.exec_()



