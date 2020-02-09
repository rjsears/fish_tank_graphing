#!/usr/bin/python3

__author__ = 'Richard J. Sears'
VERSION = "V0.0.1 (2020-02-08)"
# richardjsears@gmail.com

# This is part of my fish tank monitoring system. I purchased and installed 
# the WiFi Hydroponics Kit from Atlas Scientific which uses (out of the box)
# ThingSpeak to store date. I wanted to take this data and store it locally 
# in my Influx database for graphing and monitoring.

# https://www.atlas-scientific.com/product_pages/kits/wifi.html

# This requires a free Thingspeak account. 



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

# Here you can set DEBUG2 to True or False to override the argparse default. This is so you can set
# DEBUG mode on permanently for repeated testing without having to pass "--DEBUG" on the command line.
DEBUG2 = False

# InfluxDB connections settings
influx_host = 'my_influxdb_host'
influx_port = 8086
influx_user = 'aquaman'
influx_password = 'breathewater'
influx_dbname = 'fish_tank'

# This is useful if you have multiple tanks you want to keep track of...
tank_name = "75planted"

# ThingSpeak API Settings
api_key = "xxxxxxxxxxxxxxxxx"
channel = "1234567"

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


def get_fish_tank_data_thingspeak():
    url = "https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=2".format(channel, api_key)
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    api_request = requests.get(url, headers=headers)
    response = api_request.json()
    to_json = json.dumps(response)
    dict_json = json.loads(to_json)

    feeds = dict_json["feeds"]
    for feed in feeds[0:1]:
        pH_thingspeak = (feed['field1'])
        if DEBUG or DEBUG2:
            print ("pH = {}".format(pH_thingspeak))
        else:
            write_data("pH_thingspeak", float(pH_thingspeak))
    for feed in feeds[0:1]:
        EC_thingspeak = (feed['field2'])
        if DEBUG or DEBUG2:
            print("EC = {}".format(EC_thingspeak))
        else:
            write_data("EC_thingspeak", float(EC_thingspeak))
    for feed in feeds[0:1]:
        temp_in_C_thingspeak = (float(feed['field3']))
        if DEBUG or DEBUG2:
            print("Temp in C = {}".format(temp_in_C_thingspeak))
        else:
            write_data("Temp_in_C_thingspeak", (temp_in_C_thingspeak))
        if Temp_in_F:
            temp_in_F_thingspeak = (9.0 / 5.0 * temp_in_C_thingspeak) + 32
            if DEBUG or DEBUG2:
                print("Temp in F = {}".format(temp_in_F_thingspeak))
            else:
                write_data("Temp_in_F_thingspeak", (temp_in_F_thingspeak))


def main():
    get_fish_tank_data_thingspeak()


if __name__ == '__main__':
    main()
