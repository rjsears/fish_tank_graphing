#!/usr/bin/python3
  
## Reads fish tank data utilizing Seneye API and writes data to InfluxDB
## January 31, 2020

## In order to use this script you need to have the Seneye Reef Monitoring system and have setup API access
## to it. You can then use something like GRafana to graph the results. I run this once every ten minutes
## from a cron entry.

# */10 * * * * /root/fish_tank_monitoring/update_fish_tank_data.py >/dev/null 2>&1

## Also make sure you have the influxdb client installed: pip install influxdb

## You will need to setup API access on the Seneye website and get your device_id and creds to use the API. 
## Be sure to replace the word "device_id" in the https request below with your actual device_id as well as
## your email address and password otherwise this will fail.

from influxdb import InfluxDBClient
import requests
import json

# InfluxDB connections settings
influx_host = 'my_influxdb_host'
influx_port = 8086
influx_user = 'aquaman'
influx_password = 'breathewater!'
influx_dbname = 'fish_tank'

def write_data(measurement, value):
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname)
    json_body = [
            {
                "measurement": measurement,
                "tags": {
                    "tank": "75planted"
                        },
                "fields": {
                    "value" : value
                }
            }
        ]

    client.write_points(json_body)

def get_fish_tank_data():
    api_request = requests.get(
        'https://api.seneye.com/v1/devices/device_id?IncludeState=1&user=your_email_address@somewhere.com&pwd=letmein',
        headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
    )
    response = api_request.json()
    to_json = json.dumps(response)
    dict_json = json.loads(to_json)

    keys = ['ph', 'nh3', 'nh4', 'o2', 'lux', 'par', 'kelvin']
    for key in dict_json['exps']:
        if key in keys:
            value = dict_json['exps'][key]['curr']
            write_data(key, float(value))
    # Convert temperature from C to F
    temp_in_c = float(dict_json['exps']['temperature']['curr'])
    temp_in_f = (9.0/5.0 * temp_in_c) + 32
    write_data('temperature', temp_in_f)


def main():
        get_fish_tank_data()

if __name__ == '__main__':
    main()
