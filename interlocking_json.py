import json
import conexion

def interlocking_station_30(parent_serial_number, parent_part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    program_id = configurador[4]

    unit_information.append({
        "name": "machine_name",
        "value": machine_id
    })
    unit_information.append({
        "name": "program_name_version",
        "value": program_id
    })

    interlocking_station_30 = {
        "serial": parent_serial_number,
        "product": parent_part_number,
        "station": machine_id,
        "operator": operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_station_30, indent=4))
    return interlocking_station_30

def interlocking_station_20(serial_number, parent_part_number, pcb_part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    program_id = configurador[4]

    unit_information.append({
        "name": "machine_name",
        "value": machine_id
    })
    unit_information.append({
        "name": "program_name_version",
        "value": program_id
    })
    unit_information.append({
        "name": "pcb_part_number",
        "value": pcb_part_number
    })

    interlocking_station_20 = {
        "serial": serial_number,
        "product": parent_part_number,
        "station": machine_id,
        "operator": operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_station_20, indent=4))
    return interlocking_station_20

def interlocking_station_10(serial_number, parent_part_number):
    unit_information = []
    configurador = conexion.configurador()
    machine_id = configurador[0]
    process_name = configurador[1]
    operator = configurador[2]
    program_id = configurador[4]

    unit_information.append({
        "name": "machine_name",
        "value": machine_id
    })
    unit_information.append({
        "name": "program_name_version",
        "value": program_id
    })

    interlocking_station_10 = {
        "serial": serial_number,
        "product": parent_part_number,
        "station": machine_id,
        "operator": operator,
        "process_name": process_name,
        "location": "",
        "test_steps": {
            "unit_information": unit_information
        }
        
    }
    # print(json.dumps(interlocking_station_10, indent=4))
    return interlocking_station_10

# interlocking_station_20("AABB-parent_serial_number","CCGG02-parent_part_number","ZZXX01-heater_part_number")
# interlocking_station_50_80("MODEL1-001-0000015", "2102110-00-C", "COMPONENT-1")
# interlocking_station_40_empty_data("MODEL1-001-0000015", "2102110-00-C", "HEATSINK-1")
# interlocking_station_100("P2034365-C0-B:SFY0000TEST001", "HS-2026")