import pika
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# Inicialize o cliente InfluxDB
token = "wWyXRgFFj4qz4lYXB0kkklA2Dczvyb-SRd4xirPgIabTdFCM_28YOPhPWcLf6okqsqJCwLS9NL0aQPsq9GUyYQ=="
org = "Evoleo"
bucket = "Bucket02"

client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def callback(ch, method, properties, body):
    data = json.loads(body)
    point = Point("sensor_data")\
        .tag("sensor", data["antenna"])\
        .field("temperature", data["temperature"])\
        .field("wind_speed", data["wind_speed"])\
        .field("incline_angle", data["incline_angle"])\
        .time(data["timestamp"], WritePrecision.NS)
    write_api.write(bucket, org, point)

# Conecte-se ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='sensor_data', durable=True)
channel.basic_consume(queue='sensor_data', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
