import json
import conexion

def conduit_st10(parent_serial_number):
    configurador     = conexion.configurador()

    workstation_id = configurador[0]          # station  → worStation_ID
    operator_id    = configurador[2]          # operator → Operator_ID
    sf_id          = configurador[12]   
    password       = configurador[7]  
    print_macro    = configurador[10] 
    location     = configurador[11]

    commands = []

    conduit_json = {
        "version":      "1.0",
        "keep_alive":   False,
        "refresh_unit": True,
        "source": {
            "workstation": {
                "station": location,
                "type":    "location"
            },
            "client_id": sf_id,
            "employee":  operator_id,
            "password":  password
        },
        "transactions": [
            {
                "unit": {
                    "unit_id": parent_serial_number
                },
                "commands": [{
                    "command": print_macro
                }]
            }
        ]
    }
    # print(json.dumps(conduit_json, indent=4))
    return conduit_json


# conduit_st10("MODEL1-001-0000015")
