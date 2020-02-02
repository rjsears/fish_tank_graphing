#!/usr/bin/python3

__author__ = 'Richard J. Sears'
VERSION = "V0.0.3 (2020-02-02)"
# richardjsears@gmail.com

# Reads fish tank data utilizing Seneye API and writes data to InfluxDB
# February 2nd, 2020

# More information about the Seneye API may be found here:
# http://answers.seneye.com/en/Seneye_Products/Seneye_hobbyist_developer_information
# and here:
# https://api.seneye.com/

# pip3 install influxdb if you have not already done so.
from influxdb import InfluxDBClient, exceptions
import requests
import json
import argparse

# Setup Argparser for Debug Mode. Run this script from the command line with "--DEBUG"
# to output data to the screen. When in DEBUG mode NO DATA will be written to the
# database.
parser = argparse.ArgumentParser()
parser.add_argument("--DEBUG", action="store_true", help="Add '--DEBUG' to run script in DUBUG mode")
args = parser.parse_args()
DEBUG = args.DEBUG

# InfluxDB connections settings
influx_host = 'my_influxdb_host'
influx_port = 8086
influx_user = 'aquaman'
influx_password = 'breathewater'
influx_dbname = 'fish_tank'

# This is useful if you have multiple tanks you want to keep track of...
tank_name = "75planted"

# Seneye API Settings
user_email = "your_email_address@gmail.com"
user_passwd = "super_secret_password"
user_device = "12345"

# If you are like me and want to see your tank water temperature in Fahrenheit, set to True
Temp_in_F = True


def write_data(measurement, value):
    client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_dbname, timeout=2)
    json_body = [
        {
            "measurement": measurement,
            "tags": {
                "tank": tank_name
            },
            "fields": {
                "value": value
            }
        }
    ]
    try:
        client.write_points(json_body)
        client.close()
    except (exceptions.InfluxDBClientError, exceptions.InfluxDBServerError) as e:
        print(e)


def get_fish_tank_data():
    url = "https://api.seneye.com/v1/devices/{}?IncludeState=1&user={}&pwd={}".format(user_device, user_email, user_passwd)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    api_request = requests.get(url, headers=headers)
    response = api_request.json()
    to_json = json.dumps(response)
    dict_json = json.loads(to_json)

    if Temp_in_F:
        keys = ['ph', 'nh3', 'nh4', 'o2', 'lux', 'par', 'kelvin']
        for key in dict_json['exps']:
            if key in keys:
                value = dict_json['exps'][key]['curr']
                if DEBUG:
                    print(key, value)
                else:
                    write_data(key, float(value))
        # Convert temperature from C to F
        temp_in_c = float(dict_json['exps']['temperature']['curr'])
        temp_in_f = (9.0 / 5.0 * temp_in_c) + 32
        if DEBUG:
            print("temperature", temp_in_f)
        else:
            write_data('temperature', temp_in_f)
    else:
        keys = ['temperature', 'ph', 'nh3', 'nh4', 'o2', 'lux', 'par', 'kelvin']
        for key in dict_json['exps']:
            if key in keys:
                value = dict_json['exps'][key]['curr']
                if DEBUG:
                    print(key, value)
                else:
                    write_data(key, float(value))


def main():
    get_fish_tank_data()


if __name__ == '__main__':
    main()
