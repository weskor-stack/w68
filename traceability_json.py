import json
import conexion
import rfc3339
from datetime import datetime, timezone
import pendulum
from zoneinfo import ZoneInfo

def evaluar_codigo_defecto(val_plc, low_lim, high_lim, plc_defect_code, test_name, atributos_db):
    if low_lim in (None, "") or high_lim in (None, ""):
        return plc_defect_code
        
    try:
        val = float(val_plc)
        low = float(low_lim)
        high = float(high_lim)
        
        if not (low <= val <= high):
            for attr in atributos_db:
                if attr[0] == test_name: 
                    return attr[6] if len(attr) > 6 else plc_defect_code
            return plc_defect_code
            
    except ValueError:
        pass 
        
    return plc_defect_code

def traceability_station_30(serial_padre, defect_code_default=""):
    config_local = conexion.configuradorst30()
    
    parte = conexion.obtener_parte2(serial_padre)

    if config_local and config_local != "FAILED":
        machine_id = str(config_local[0]).strip()
        operator_id = str(config_local[1]).strip()
        process_name = str(config_local[3]).strip()
        component_name_db = str(config_local[4]).strip()
        program_version = str(config_local[2]).strip()
    else:
        machine_id = "AMC-GENLD97"
        operator_id = "9999"
        process_name = "Pressfit"
        component_name_db = "component"
        program_version = "default_program"

    now = datetime.now(ZoneInfo("America/Mexico_City"))
    now_utc = now.strftime("%d/%m/%Y %I:%M:%S %p")
    fecha = str(parte[3])
    # Convertir la cadena a datetime
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

    # Dar el formato deseado
    fecha_formateada = fecha_dt.strftime("%d/%m/%Y %I:%M:%S %p")
    
    atributos = conexion.select_attributes_st50_80()
    atributos_map = {}
    for attr in atributos:
        if len(attr) >= 7:
            nombre_atributo = str(attr[1]).lower().strip() 
            atributos_map[nombre_atributo] = {
                'defect_code_low': str(attr[5]).strip() if attr[5] is not None else "",   
                'defect_code_high': str(attr[6]).strip() if attr[6] is not None else "",  
                'name': attr[1]
            }

    part_row = conexion.pieces(serial_padre)
    all_test_rows = []
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data3(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    global_status = "PASSED"

    for row in all_test_rows:
        try:
            test_source = str(row[-1]).strip().lower() if isinstance(row[-1], str) and row[-1] in ['screwing', 'pressfit', 'inspection', 'electrical'] else ""
            
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[9]) if row[9] is not None else "Measurement"
            desc_step = str(row[9]) if row[9] is not None else "Description"
            
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'SCREWING',
                'pressfit': 'PRESSFIT', 
                'inspection': 'INSPECTION',  
                'electrical': 'ELECTRICAL'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.upper())
            
            if attr_name.lower() in atributos_map:
                defect_code_low = atributos_map[attr_name.lower()]['defect_code_low']
                defect_code_high = atributos_map[attr_name.lower()]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low if defect_code_low else defect_code_default
            elif val_medido > lim_sup:
                step_defect = defect_code_high if defect_code_high else defect_code_default
            else:
                step_defect = defect_code_high if defect_code_high else (defect_code_low if defect_code_low else defect_code_default)
        else:
            step_defect = ""

        steps_list.append({
            "name": name_step,
            "description": desc_step,
            "comparator": "GELE",
            "lowLimit": lim_inf,
            "highLimit": lim_sup,
            "units": unidad,
            "status": status_step,
            "value": val_medido,
            "defect_code": step_defect
        })

    program_version = str(program_version).strip() if program_version else "default_program"

    payload = {
        "serial": serial_padre,
        "product": parte[4],
        "station": machine_id,
        "operator": operator_id,
        "start_time": fecha_formateada,
        "end_time": now_utc,
        "process_name": process_name,
        "status": global_status,
        "commands": [
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Machine Name",
                "component_id": machine_id
            },
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Program Name version",
                "component_id": program_version   
            }
        ],
        "test_steps": {
            "AOI LIST": steps_list
        }
    }

    return payload

def traceability_station_20(serial_padre, defect_code_default=""):
    unit_information = []
    config_local = conexion.configuradorst20()
    
    parte = conexion.obtener_parte2(serial_padre)

    componente = conexion.component_data(parte[0])

    if config_local and config_local != "FAILED":
        machine_id = str(config_local[0]).strip()
        operator_id = str(config_local[1]).strip()
        process_name = str(config_local[3]).strip()
        component_name_db = str(config_local[4]).strip()
        program_version = str(config_local[2]).strip()
    else:
        machine_id = "AMC-GENLD97"
        operator_id = "9999"
        process_name = "Pressfit"
        component_name_db = "component"
        program_version = "default_program"

    unit_information.append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}_Machine Name",
        "component_id": machine_id
    })

    unit_information.append({
        "command": "ReplaceNontrackedComponent",
        "ref_designator": f"{process_name}_Program Name version",
        "component_id": program_version   
    })
    
    for x in componente:
        unit_information.append({
            "command": "ReplaceTrackedComponent",
            "ref_designator": f"{process_name}_PCB",
            "component_id": x[0]
        })

    now = datetime.now(ZoneInfo("America/Mexico_City"))
    now_utc = now.strftime("%d/%m/%Y %I:%M:%S %p")
    fecha = str(parte[3])
    # Convertir la cadena a datetime
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

    # Dar el formato deseado
    fecha_formateada = fecha_dt.strftime("%d/%m/%Y %I:%M:%S %p")
    
    atributos = conexion.select_attributes_st50_80()
    atributos_map = {}
    for attr in atributos:
        if len(attr) >= 7:
            nombre_atributo = str(attr[1]).lower().strip() 
            atributos_map[nombre_atributo] = {
                'defect_code_low': str(attr[5]).strip() if attr[5] is not None else "",   
                'defect_code_high': str(attr[6]).strip() if attr[6] is not None else "",  
                'name': attr[1]
            }

    part_row = conexion.pieces(serial_padre)
    all_test_rows = []
    
    if part_row:
        part_id = part_row[0]
        
        try:
            sr = conexion.screwing_data(part_id)
            if sr and isinstance(sr, list):
                for item in sr: all_test_rows.append(item + ('screwing',))
        except Exception: pass
        
        try:
            pr = conexion.pressfit_data(part_id)
            if pr and isinstance(pr, list):
                for item in pr: all_test_rows.append(item + ('pressfit',))
        except Exception: pass
        
        try:
            ir = conexion.inspection_data3(part_id)
            if ir and isinstance(ir, list):
                for item in ir: all_test_rows.append(item + ('inspection',))
        except Exception: pass
        
        try:
            er = conexion.electrical_data(part_id)
            if er and isinstance(er, list):
                for item in er: all_test_rows.append(item + ('electrical',))
        except Exception: pass

    steps_list = []
    global_status = "PASSED"

    for row in all_test_rows:
        try:
            test_source = str(row[-1]).strip().lower() if isinstance(row[-1], str) and row[-1] in ['screwing', 'pressfit', 'inspection', 'electrical'] else ""
            
            val_medido = float(row[1]) if row[1] is not None else 0.0
            lim_inf = float(row[2]) if row[2] is not None else 0.0
            lim_sup = float(row[3]) if row[3] is not None else 0.0
            unidad = str(row[5]) if row[5] is not None else ""
            status_step = str(row[6]).upper() if row[6] is not None else "PASSED"
            name_step = str(row[9]) if row[9] is not None else "Measurement"
            desc_step = str(row[9]) if row[9] is not None else "Description"
            
        except Exception:
            continue

        if status_step == "FAILED":
            global_status = "FAILED"
            
            defect_code_low = defect_code_default
            defect_code_high = defect_code_default
            
            source_to_attribute = {
                'screwing': 'SCREWING',
                'pressfit': 'PRESSFIT', 
                'inspection': 'INSPECTION',  
                'electrical': 'ELECTRICAL'
            }
            
            attr_name = source_to_attribute.get(test_source, name_step.upper())
            
            if attr_name.lower() in atributos_map:
                defect_code_low = atributos_map[attr_name.lower()]['defect_code_low']
                defect_code_high = atributos_map[attr_name.lower()]['defect_code_high']
            else:
                if name_step.lower() in atributos_map:
                    defect_code_low = atributos_map[name_step.lower()]['defect_code_low']
                    defect_code_high = atributos_map[name_step.lower()]['defect_code_high']
            
            if val_medido < lim_inf:
                step_defect = defect_code_low if defect_code_low else defect_code_default
            elif val_medido > lim_sup:
                step_defect = defect_code_high if defect_code_high else defect_code_default
            else:
                step_defect = defect_code_high if defect_code_high else (defect_code_low if defect_code_low else defect_code_default)
        else:
            step_defect = ""

        steps_list.append({
            "name": name_step,
            "description": desc_step,
            "comparator": "GELE",
            "lowLimit": lim_inf,
            "highLimit": lim_sup,
            "units": unidad,
            "status": status_step,
            "value": val_medido,
            "defect_code": step_defect
        })

    program_version = str(program_version).strip() if program_version else "default_program"

    payload = {
        "serial": serial_padre,
        "product": parte[4],
        "station": machine_id,
        "operator": operator_id,
        "start_time": fecha_formateada,
        "end_time": now_utc,
        "process_name": process_name,
        "status": global_status,
        "commands": unit_information,
        "test_steps": {
            "AOI LIST": steps_list
        }
    }

    return payload

def traceability_station_10(result, serial_number):
    config_local = conexion.configurador_w68_st10()
    
    parte = conexion.serial_number2(serial_number)

    if config_local and config_local != "FAILED":
        machine_id = str(config_local[0]).strip()
        operator_id = str(config_local[1]).strip()
        process_name = str(config_local[3]).strip()
        program_version = str(config_local[2]).strip()
        location = str(config_local[4]).strip()
        shop_flor = str(config_local[5]).strip()
        password = str(config_local[6]).strip()
        print_macro = str(config_local[7]).strip()


    else:
        machine_id = "AMC-GENLD97"
        operator_id = "9999"
        process_name = "Pressfit"
        program_version = "default_program"
        location = "default_location"
        shop_flor = "default_shop_floor"
        password = "default_password"
        print_macro = "default_print_macro"

    now = datetime.now(ZoneInfo("America/Mexico_City"))
    now_utc = now.strftime("%d/%m/%Y %I:%M:%S %p")
    fecha = str(parte[4])
    # Convertir la cadena a datetime
    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")

    # Dar el formato deseado
    fecha_formateada = fecha_dt.strftime("%d/%m/%Y %I:%M:%S %p")
    
    atributos = conexion.select_attributes_st50_80()
    atributos_map = {}
    for attr in atributos:
        if len(attr) >= 7:
            nombre_atributo = str(attr[1]).lower().strip() 
            atributos_map[nombre_atributo] = {
                'defect_code_low': str(attr[5]).strip() if attr[5] is not None else "",   
                'defect_code_high': str(attr[6]).strip() if attr[6] is not None else "",  
                'name': attr[1]
            }

    payload = {
        "serial": serial_number,
        "product": parte[1],
        "station": machine_id,
        "operator": operator_id,
        "start_time": fecha_formateada,
        "end_time": now_utc,
        "process_name": process_name,
        "status": result,
        "commands": [
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Machine Name",
                "component_id": machine_id
            },
            {
                "command": "ReplaceNontrackedComponent",
                "ref_designator": f"{process_name}_Program Name version",
                "component_id": program_version   
            }
        ]
    }

    return payload


# if __name__ == "__main__":
#     resultado_json = traceability_station_10(
#         serial_number = "MODEL1-001-0000003",
#         result = "PASS"
#     )
    
#     if isinstance(resultado_json, dict):
#         print(json.dumps(resultado_json, indent=4))
#     else:
#         print(f"\nError:\n{resultado_json}")