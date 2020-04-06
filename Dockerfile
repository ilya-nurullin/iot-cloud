FROM python:3.8.2-alpine3.11
COPY ./server.py /iot-cloud/
COPY ./.env /iot-cloud/.env
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install Flask psycopg2 flask-cors influxdb paho-mqtt python-dotenv \
    && apk del build-deps
EXPOSE 8999
CMD [ "python3","/iot-cloud/server.py"]