#!/bin/bash
dpkg -i influxdb.deb
rm influxdb.deb
apt-get update
apt-get install -y python3 python3-pip postgresql postgresql-contrib mosquitto
pip install Flask psycopg2 flask-cors influxdb paho-mqtt