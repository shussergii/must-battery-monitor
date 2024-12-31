# must-battery-monitor
Monitoring script for Must LiFePO4 Battery via RS485 and send the stats to InfluxDB.

Protocol info in 72651-11624-PACE-BMS-Modbus-Protocol-for-RS485-V1.32017-06-27.pdf

**Settings for RS485 Protocol:MSL-485**

Script based on Monitor a MUST inverter


Original code from [andremiller/must-inverter-python-monitor](https://github.com/andremiller/must-inverter-python-monitor)

## Requirements

- Python
- InfluxDB

## Installation

Install python dependencies

```
pip install -r requirements.txt
```

Create a .env file

```
cp .env .env.sample
```
