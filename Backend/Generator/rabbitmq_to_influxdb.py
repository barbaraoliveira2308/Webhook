import pika
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# Inicialize o cliente InfluxDB
token = "zXEZuTeOyF-J46ppqJpxQckwvKuRmi7DHqFZsh-KXRVrnTJ9OYKPi9dEDSb-bxfaY1v3IIwXZvziCprXo2_UYw=="
org = "Evoleo"
bucket = "Bucket02"

client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f"Received data: {data}")

        tags = data.get("tags", {})
        fields = data.get("fields", {})

        antenna_value = tags.get("antenna")
        temperature_value = fields.get("temperature")
        wind_speed_value = fields.get("wind_speed")
        incline_angle_value = fields.get("incline_angle")
        timestamp_value = data.get("time")

        if antenna_value is not None and temperature_value is not None and wind_speed_value is not None and incline_angle_value is not None and timestamp_value is not None:
            point = Point("sensor_data")\
                .tag("sensor", antenna_value)\
                .field("temperature", temperature_value)\
                .field("wind_speed", wind_speed_value)\
                .field("incline_angle", incline_angle_value)\
                .time(timestamp_value, WritePrecision.NS)
            write_api.write(bucket, org, point)
        else:
            print("Campos ausentes nos dados.")
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        print(f"Erro durante o processamento: {e}")



# Conecte-se ao RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='sensor_data', durable=True)
channel.basic_consume(queue='sensor_data', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
