FROM ubuntu:latest
COPY iot-cloud ./iot-cloud
COPY iot-web-ui ./iot-web-ui
COPY influxdb.deb ./influxdb.deb
COPY ./install.sh ./install.sh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN "./install.sh"
EXPOSE 8080
CMD [ "./iot-web-ui/!runlocalhost.bat & python3 ./iot-cloud/server.py" ]