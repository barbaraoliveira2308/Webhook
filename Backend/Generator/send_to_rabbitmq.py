import pika
import json
from generate_sensor_data import generate_sensor_data

def send_to_rabbitmq(data, queue_name='sensor_data'):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)

    for record in data:
        message = json.dumps(record)
        channel.basic_publish(exchange='',
                              routing_key=queue_name,
                              body=message,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # torna a mensagem persistente
                              ))
    connection.close()

# Uso do script
if __name__ == "__main__":
    sensor_data = generate_sensor_data(5)
    send_to_rabbitmq(sensor_data)
