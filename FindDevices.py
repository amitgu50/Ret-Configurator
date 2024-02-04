import re
import xml.etree.cElementTree as et
import pandas as pd
from DeviceClass import Device
from collections import namedtuple
from NewAnt import NewAntApp
DEVICES = []

def FindSerialID(serialNumber, antModel):
    def method1():
        return serialNumber[-2:]
    def method2():
        return serialNumber[1:3]
    def method3():
        lastDigit = serialNumber[-1]
        serialDict3 = {
            "1" : "R1",
            "2" : "Y1",
            "3" : "Y2",
            "4" : "Y3"
        }
        return serialDict3[lastDigit]
    def method4():
        return "abc"
    ## Get the method ##
    serialID = ""
    df = pd.read_excel("Values.xlsx", sheet_name='antmod-baseid')
    # print(serialNumber, antModel)
    method = str(df.loc[df['antModel'] == antModel, 'method'].iloc[0])
    if method == '1.0':
        serialID = method1()
    elif method == '2.0':
        serialID = method2()
    elif method == '3.0':
        serialID = method3()
    elif method == '4.0':
        serialID = method4()
    else:
        return "didn't found serial ID"

    return(str(serialID))

def CheckAnt(serialNumber, antModel):
    try:
        df = pd.read_excel('Values.xlsx', sheet_name='antmod-baseid')
        serialID = FindSerialID(serialNumber, antModel)
        desired_ant_model = str(antModel)
        filtered_df = df[(df['antModel'] == desired_ant_model) & (df['id'] == serialID)]
        base_station_id = filtered_df.iloc[0]['baseStationID']
        return True
    except:
        return False

def FindDevices_function(file_path):
    ModifiedDevice = namedtuple('ModifiedDevice', ['firstEndPoint', 'secondEndPoint', 'mrbtsId', 'serialNumber', 'antModel', 'minAngle', 'file_path'])
    list_modifiedDevices = {}
    xml_file_path = file_path
    tree = et.parse(xml_file_path)
    root = tree.getroot()
    namespace = {"ns": "raml21.xsd"}

    #### Find FirstEndPoint and ALD number ####
    firstEndPoint = []
    secondEndPoint = []
    namesToSearch = ["firstEndpointDN", "secondEndpointDN"]
    for name in namesToSearch:
        elements = root.findall(".//ns:p[@name='{}']".format(name), namespace)
        if elements:
            for element in elements:
                text = element.text
                if name == "firstEndpointDN":
                    if "RMOD" in text:
                        firstEndPoint.append(text)
                if name == "secondEndpointDN":
                    if "ALD" in text:
                        text = text.split("ALD-")[1]
                        secondEndPoint.append(text)

    for random in range(len(firstEndPoint)):
        #### Find MrbtsID ####
        mrbtsId = ""
        input_string = firstEndPoint[random]
        parts = input_string.split('/')
        for part in parts:
            if part.startswith('MRBTS-'):
                # Extract the number after 'MRBTS-'
                number_after_mrbts = part.split('-')[1]
                mrbtsId =  number_after_mrbts
        # print(mrbtsId)

        #### Find SerialNumber ####
        serialNumber = ""
        aldNumber = secondEndPoint[random]
        sector_distname = f"MRBTS-{mrbtsId}/EQM-1/APEQM-1/ALD-{aldNumber}"
        for managed_object in root.findall(".//ns:managedObject", namespace):
            dist_name = managed_object.get("distName")
            if sector_distname == dist_name:
                serial_element = managed_object.find(".//ns:p[@name='serialNumber']", namespace)
                if serial_element is not None:
                    serial_text = serial_element.text
                    serialNumber = serial_text  
        # print(serialNumber)

        #### Find MinAngle ####
        minAngle = ""
        aldNumber = secondEndPoint[random]
        sector_distname = f"MRBTS-{mrbtsId}/EQM-1/APEQM-1/ALD-{aldNumber}/RETU-1"
        for managed_object in root.findall(".//ns:managedObject", namespace):
            dist_name = managed_object.get("distName")
            if sector_distname == dist_name:
                minAngle_element = managed_object.find(".//ns:p[@name='minAngle']", namespace)
                if minAngle_element is not None:
                    minAngle_text = minAngle_element.text
                    minAngle = minAngle_text 
        # print(minAngle)


        #### Find antModel ####
        antModel = ""
        sector_distname = f"MRBTS-{mrbtsId}/EQM-1/APEQM-1/ALD-{aldNumber}/RETU-1"
        for managed_object in root.findall(".//ns:managedObject", namespace):
            dist_name = managed_object.get("distName")
            if sector_distname == dist_name:
                antModel_element = managed_object.find(".//ns:p[@name='antModel']", namespace)
                if antModel_element is not None:
                    antModel_text = antModel_element.text
                    antModel = antModel_text  
        
        if antModel == '':
            sector_distname = f"MRBTS-{mrbtsId}/EQM-1/APEQM-1/ALD-{aldNumber}"
            for managed_object in root.findall(".//ns:managedObject", namespace):
                dist_name = managed_object.get("distName")
                if sector_distname == dist_name:
                    antModel_element = managed_object.find(".//ns:p[@name='productCode']", namespace)
                    if antModel_element is not None:
                        antModel_text = antModel_element.text
                        antModel = antModel_text  
        # print(antModel)

        mha = ""
        try: 
            sector_distname = f"MRBTS-{mrbtsId}/EQM-1/APEQM-1/ALD-{aldNumber}"
            for managed_object in root.findall(".//ns:managedObject", namespace):
                dist_name = managed_object.get("distName")
                if sector_distname == dist_name:
                    mha_element = managed_object.find(".//ns:p[@name='mhaType']", namespace)
                    if mha_element is not None:
                        mha_text = mha_element.text
                        mha = antModel_text 
        except:
            mha = "" 
        if mha == "":
            if not CheckAnt(serialNumber, antModel):
                try:
                    list_modifiedDevices[f"{antModel}"].append(ModifiedDevice(firstEndPoint[random], secondEndPoint[random], mrbtsId, serialNumber, antModel, minAngle, file_path))
                except:
                    list_modifiedDevices[f"{antModel}"] = []
                    list_modifiedDevices[f"{antModel}"].append(ModifiedDevice(firstEndPoint[random], secondEndPoint[random], mrbtsId, serialNumber, antModel, minAngle, file_path))
                    # NewAntApp(serialNumber, antModel)
            else:
                DEVICES.append(Device(firstEndPoint[random], secondEndPoint[random], mrbtsId, serialNumber, antModel, minAngle, file_path))
        else:
            print(f"mhaType found, not adding: {mha}")
    for ant in list_modifiedDevices:
        NewAntApp(ant, list_modifiedDevices[ant])
        for d in list_modifiedDevices[ant]:
            DEVICES.append(Device(d.firstEndPoint, d.secondEndPoint, d.mrbtsId, d.serialNumber, d.antModel, d.minAngle, d.file_path))
    return DEVICES







