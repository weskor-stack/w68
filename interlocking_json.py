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
        "name": "Machine_ID",
        "value": machine_id
    })
    unit_information.append({
        "name": "Program name + version",
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

def interlocking_station_20(serial_number):
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

    piece_id = conexion.serial_number_component(serial_number)
    componente = conexion.component_data(piece_id[0])

    valores_vistos = set()

    indice = 1
    for x in componente:
        valor = x[1]
        if valor not in valores_vistos:
            unit_information.append({
                "name": "pcb"+str(indice)+"_part_number",
                "value": valor
            })
            valores_vistos.add(valor)
            indice+=1

    interlocking_station_20 = {
        "serial": serial_number,
        "product": piece_id[2],
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
        "name": "Machine_ID",
        "value": machine_id
    })
    unit_information.append({
        "name": "Program name + version",
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

def interlocking_station_20_v2(serial_number):
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

    piece_id = conexion.serial_number_component(serial_number)

    componente = conexion.component_data(piece_id[0])

    if componente == []:
        pcba_data = conexion.pcba_select()
        if pcba_data == "FAILED":
            return None
        else:
            indice = 1
            for x in pcba_data:
                valor = x[1]
                componente_actualizado = conexion.component_store(x[0],x[1],serial_number)
                # print(f"Component store result for {x[0]}: {componente_actualizado}")
                actualizar_status = conexion.pcba_update_status_single(x[0])
                # print(f"Status update result: {actualizar_status}")
                unit_information.append({
                    "name": "pcb"+str(indice)+"_part_number",
                    "value": valor
                })
                indice+=1


    else:
        pcba_data = conexion.pcba_select_all()
        if pcba_data == "FAILED":
            valores_vistos = set()
            
            indice = 1
            for x in componente:
                valor = x[1]
                if valor not in valores_vistos:
                    unit_information.append({
                        "name": "pcb"+str(indice)+"_part_number",
                        "value": valor
                    })
                    valores_vistos.add(valor)
                    indice+=1
        else:
            valores_vistos = set()

            indice = 1
            for x in componente:
                nombre = x[0]
                valor = x[1]
                for y in pcba_data:
                    if nombre == y[0]:
                        conexion.pcba_update_status_single(nombre)
                if valor not in valores_vistos:
                    unit_information.append({
                        "name": "pcb"+str(indice)+"_part_number",
                        "value": valor
                    })
                    valores_vistos.add(valor)
                    indice+=1
    

    interlocking_station_20 = {
        "serial": serial_number,
        "product": piece_id[2],
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

# interlocking_station_20_v2("P1472635-61-G:SE4A22172000000")