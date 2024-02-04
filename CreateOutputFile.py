import xml.etree.ElementTree as ET
from FindDevices import FindDevices_function

def CreateOutputFile_function(DEVICES):
    # Define the XML indentation function
    def indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    file_path = DEVICES[0].file_path
    # print(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        tree = ET.parse(file)
        root = tree.getroot()

    namespaces = {'ns': 'raml21.xsd'}

    for device in DEVICES:
        # print(device.aldNumber)

        distname = f"MRBTS-{device.mrbtsId}/EQM-1/APEQM-1/ALD-{device.aldNumber}/RETU-1"
        managed_object = root.find(f".//ns:managedObject[@distName='{distname}']", namespaces=namespaces)
        
        if managed_object:
            # Existing values within the <p> elements
            existing_values = {p.attrib['name']: p for p in managed_object.findall('ns:p', namespaces=namespaces)}

            # For the angle attribute
            if 'angle' in existing_values:
                existing_values['angle'].text = str(int(float(device.realangle)))
            else:
                new_p = ET.SubElement(managed_object, 'p', name='angle')
                new_p.text = str(int(float(device.realangle)))

            # For the baseStationID attribute
            if 'baseStationID' in existing_values:
                existing_values['baseStationID'].text = str(device.band)
            else:
                new_p = ET.SubElement(managed_object, 'p', name='baseStationID')
                new_p.text = str(device.band)

            # For the sectorID attribute
            if 'sectorID' in existing_values:
                existing_values['sectorID'].text = str(device.sector)
            else:
                new_p = ET.SubElement(managed_object, 'p', name='sectorID')
                new_p.text = str(device.sector)
            
            # Add the new list
            antlDNList = ET.SubElement(managed_object, 'list', name="antlDNList")
            if not device.antIDN:
                if device.band == "na":
                    (device.antIDN).append("external")
                else:
                    (device.antIDN).append("external")
            for tx in device.antIDN:
                ET.SubElement(antlDNList, 'p').text = tx
        

    # Format XML
    indent(root)
    filename = file_path.split('/')[-1]
    outputFilePath = fr"OutputFiles/output_{filename}"
    tree.write(outputFilePath, encoding="utf-8", xml_declaration=True)
    with open(outputFilePath, 'r', encoding='utf-8') as f:
        content = f.read()
    updated_content = content.replace("ns0:", "")
    with open(outputFilePath, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    return outputFilePath