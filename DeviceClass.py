import pandas as pd
import re
import pandas as pd
import xml.etree.cElementTree as et

class Device:
    def __init__(self, firstEndPoint, aldNumber, mrbtsId, serialNumber, antModel, minAngle, file_path):
        self.addedRmodValue = ""
        self.firstEndPoint = firstEndPoint
        self.aldNumber = aldNumber
        self.mrbtsId = mrbtsId
        self.serialNumber = serialNumber
        self.antModel = antModel
        self.serialID = self.FindSerialID()
        # self.serialID = "serialID"
        self.rmod = self.FindRmod()
        self.sector = self.FindSector()
        self.band = self.FindBand()
        self.bandArr = self.band.split('+')
        self.cellid = self.FindCellId()
        self.cellidArr = self.cellid.split(',')
        # print(minAngle)
        self.angle = str(float(minAngle)/10)
        self.realangle = str(float(self.angle) * 10)
        self.file_path = file_path
        self.antIDN = self.FindAntIDN()
        self.antIdnShortcut = self.FindAntShortcut()
        # self.antIDN = "antidn"
    
    def FindSerialID(self):
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
        serialNumber = self.serialNumber
        antModel = self.antModel
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



    def FindRmod(self):
        input_string = self.firstEndPoint
        pattern = r'RMOD-(\d+)'
        match = re.search(pattern, input_string)
        rmodNumber = f"RMOD-{match.group(1)}"
        try: 
            pattern1= rf'RMOD-{match.group(1)}/ANTL-(\d+)'
            match1 = re.search(pattern1, input_string)
            newPattern = f"/ANTL-{match1.group(1)}"
            rmodNumber = rmodNumber + newPattern
        except:
            pass
        return rmodNumber
    
    def FindSector(self):
        df = pd.read_excel('Values.xlsx', sheet_name='rmod-sector')
        desired_rmod = self.rmod + self.addedRmodValue
        sec = df[df['RMOD'] == desired_rmod]['SECTOR'].values[0]
        return str(sec)
    
    def FindBand(self):
        df = pd.read_excel('Values.xlsx', sheet_name='antmod-baseid')
        desired_ant_model = str(self.antModel)
        desired_id = self.serialID
        filtered_df = df[(df['antModel'] == desired_ant_model) & (df['id'] == desired_id)]
        base_station_id = filtered_df.iloc[0]['baseStationID']
        return base_station_id
    
    def FindCellId(self):
        df = pd.read_excel('Values.xlsx', sheet_name='band-cellid')
        band = str(self.band)
        sector = int(self.sector)
        filtered_df = df[(df['band'] == band) & (df['sector'] == sector)]
        cellId = filtered_df.iloc[0]['cellid']
        return cellId
    
    def FindAntIDN(self):
        antlDN_set = set()
        numbers = self.cellidArr
        xml_file_path = self.file_path
        tree = et.parse(xml_file_path)
        root = tree.getroot()
        namespace = {"ns": "raml21.xsd"}
        counter = 0
        for number in numbers:
            sector_distname = f"MRBTS-{self.mrbtsId}/MNL-1/MNLENT-1/CELLMAPPING-1/LCELL-{number}/CHANNELGROUP-1/CHANNEL-"
            if self.bandArr[counter] == "GSM":
                sector_distname = f"MRBTS-{self.mrbtsId}/MNL-1/MNLENT-1/CELLMAPPING-1/LCELC-{number}/CHANNELGROUP-1/CHANNEL-"
            if "092502A" in self.antModel:
                sector_distname = f"MRBTS-{self.mrbtsId}/MNL-1/MNLENT-1/CELLMAPPING-1/LCELNR-{number}/CHANNELGROUP-1/CHANNEL-"
            for managed_object in root.findall(".//ns:managedObject", namespace):
                dist_name = managed_object.get("distName")
                if sector_distname in dist_name:
                    antlDN_element = managed_object.find(".//ns:p[@name='antlDN']", namespace)
                    if "092502A" in self.antModel:
                        antlDN_element = managed_object.find(".//ns:p[@name='resourceDN']", namespace)
                    if antlDN_element is not None:
                        antlDN_text = antlDN_element.text
                        antlDN_set.add(antlDN_text)  # Add to the set to ensure uniqueness
            counter = counter + 1
        return list(antlDN_set)
    
    def FindAntShortcut(self):
        original_array = self.antIDN
        pattern_array = []
        pattern = r"/RMOD-\d+/ANTL-\d+"
        for value in original_array:
            matches = re.findall(pattern, value)
            if matches:
                pattern_array.append(matches[0])
        return pattern_array

    
    def Update(self):
        df = pd.read_excel('Values.xlsx', sheet_name='band-cellid')
        band = str(self.band)
        self.bandArr = self.band.split('+')
        sector = int(self.sector)
        filtered_df = df[(df['band'] == band) & (df['sector'] == sector)]
        cellId = filtered_df.iloc[0]['cellid']
        self.cellid = cellId
        self.cellidArr = self.cellid.split(',')
        self.antIDN = self.FindAntIDN()
        self.antIdnShortcut = self.FindAntShortcut()
        self.realangle = str(float(self.angle) * 10)
        self.sector = str(self.sector)

# L = Device("RMOD-4", "2", "2", "s","80010992", "input.xml")
# print(L.antIDN)