FROM python:3.8-alpine3.11
COPY ./server.py /iot-cloud/
COPY ./.env /iot-cloud/.env
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN pip install Flask psycopg2 flask-cors influxdb paho-mqtt python-dotenv
EXPOSE 8999
CMD [ "python3","/iot-cloud/server.py"]