import minimalmodbus
import time
import requests
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler(
            filename="logs/must_batt_monitor.log",
            maxBytes=1_000_000,
            backupCount=10,
        ),
    ],
)

SERPORT = os.getenv("SERPORT")
SERTIMEOUT = float(os.getenv("SERTIMEOUT"))
SERBAUD = int(os.getenv("SERBAUD"))

INTERVAL = int(os.getenv("INTERVAL"))

INFLUX_HOST = os.getenv("INFLUX_HOST")
INFLUX_ORGID = os.getenv("INFLUX_ORGID")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")

# Registers to retrieve data for
register_map = {

    0: ["Current", "Positive: charging, Negative: discharging", 10, "mA"],
    1: ["Voltage_of_pack", "Voltage of pack", 10, "mV"],
    2: ["SOC", "SOC", 1, "%"],
    3: ["SOH", "SOH", 1, "%"],

    4: ["RemainCapacity", "Remain capacity", 10, "mAH"],
    5: ["FullCapacity", "Full capacity", 10, "mAH"],
    6: ["DesignCapacity", "Design capacity", 10, "mAH"],

    7: ["BatteryCycleCounts", "Battery cycle counts", 1, ""],

    9: ["Warning_flag", "Warning flag", 1, ""],
    10: ["Protection_flag", "Protection flag", 1, ""],
    11: ["Status_Fault_flag", "Status/Fault flag", 1, ""],
    12: ["Balance_status", "Balance status", 1, ""],

    15: ["Cell_voltage_1", "Cell voltage", 1, "mV"],
    16: ["Cell_voltage_2", "Cell voltage", 1, "mV"],
    17: ["Cell_voltage_3", "Cell voltage", 1, "mV"],
    18: ["Cell_voltage_4", "Cell voltage", 1, "mV"],
    19: ["Cell_voltage_5", "Cell voltage", 1, "mV"],
    20: ["Cell_voltage_6", "Cell voltage", 1, "mV"],
    21: ["Cell_voltage_7", "Cell voltage", 1, "mV"],
    22: ["Cell_voltage_8", "Cell voltage", 1, "mV"],
    23: ["Cell_voltage_9", "Cell voltage", 1, "mV"],
    24: ["Cell_voltage_10", "Cell voltage", 1, "mV"],
    25: ["Cell_voltage_11", "Cell voltage", 1, "mV"],
    26: ["Cell_voltage_12", "Cell voltage", 1, "mV"],
    27: ["Cell_voltage_13", "Cell voltage", 1, "mV"],
    28: ["Cell_voltage_14", "Cell voltage", 1, "mV"],
    29: ["Cell_voltage_15", "Cell voltage", 1, "mV"],
    30: ["Cell_voltage_16", "Cell voltage", 1, "mV"],

    31: ["Cell_temp_1_4", "Cell temperature 1-4", 0.1, "C"],
    32: ["Cell_temp_5_8", "Cell temperature 5-8", 0.1, "C"],
    33: ["Cell_temp_9_12", "Cell temperature 9-12", 0.1, "C"],
    34: ["Cell_temp_13_16", "Cell temperature 13-16", 0.1, "C"],

    35: ["MOSFET_temperature", "MOSFET temperature", 0.1, "C"],
    36: ["Environment_temperature", "Environment temperature", 0.1, "C"]

}




def read_register_values(i, startreg, count):
    stats_line = ""

    register_id = startreg
    results = i.read_registers(startreg, count)
    for r in results:
        if register_id in register_map:
            r_key = register_map[register_id][0]
            r_unit = register_map[register_id][2]

            if register_map[register_id][3] == "map":
                r_value = '"' + register_map[register_id][4][r] + '"'
            else:
                r_value = str(round(r * r_unit, 2))

            # convert from offset val
            if register_id == 0  :
                if float(r_value) > 32000 :
                   r_value = -abs(float(r_value)- 655360)
                else:
                   r_value = float(r_value)

            stats_line += r_key + "=" + str(r_value) + ","

        register_id += 1

    # Remove comma at the end
    stats_line = stats_line[:-1]

    return stats_line


def send_data(stats):
    url = "{}/api/v2/write?orgID={}&bucket={}".format(
        INFLUX_HOST, INFLUX_ORGID, INFLUX_BUCKET
    )
    data = "inverter " + stats + " " + str(time.time_ns())

    logging.info(data)
    r = requests.post(
        url,
        data=data,
        headers={
            "content-type": "text/plain",
            "Authorization": "Token " + INFLUX_TOKEN,
        },
    )
    logging.info(f"{r.status_code} {r.text}")


infinite = True

while infinite:
    i = minimalmodbus.Instrument(SERPORT, 1)
    i.serial.timeout = SERTIMEOUT
    i.serial.baudrate = SERBAUD
    stats_line_all = read_register_values(i, 0, 37)
    send_data(stats_line_all)


    # infinite = False

    if infinite:
        time.sleep(INTERVAL)
