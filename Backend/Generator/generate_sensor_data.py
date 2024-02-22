import random
import time
from datetime import datetime
from influxdb_client import InfluxDBClient
import requests
import os
from dotenv import load_dotenv


#Variaveis de ambiente 

load_dotenv(dotenv_path="Backend\\Generator\\Influx_var.env")

host=os.getenv("INFLUXDB_HOST")
port=int(os.getenv("INFLUXDB_PORT", 8086))
username=os.getenv("INFLUXDB_USER")
password=os.getenv("INFLUXDB_PASSWORD")
influx_db=os.getenv('INFLUXDB_DB')
influx_token=os.getenv('INFLUXDB_TOKEN')
org=os.getenv('INFLUX_ORG')

  

    # Configuração do cliente InfluxDB

 #Configuração do cliente InfluxDB
url = "http://localhost:8086"  # Substitua pela URL correta
influx_token = "zXEZuTeOyF-J46ppqJpxQckwvKuRmi7DHqFZsh-KXRVrnTJ9OYKPi9dEDSb-bxfaY1v3IIwXZvziCprXo2_UYw=="  # Substitua pelo token correto
org = "Evoleo"  # Substitua pela organização correta

client = InfluxDBClient(url=url, token=influx_token, org=org)

def send_sensor_data_to_webhook(sensor_data):
    webhook_url = "http://localhost:8000/webhook"  # Substitua pela URL correta

    # Extrai os campos necessários do sensor_data
    timestamp = sensor_data["time"]
    antenna = sensor_data["tags"]["antenna"]
    latitude = sensor_data["tags"]["latitude"]
    longitude = sensor_data["tags"]["longitude"]
    temperature = sensor_data["fields"]["temperature"]
    wind_speed = sensor_data["fields"]["wind_speed"]
    incline_angle = sensor_data["fields"]["incline_angle"]

    # Cria o payload para o webhook
    payload = {
        "timestamp": timestamp,
        "antenna": antenna,
        "latitude": latitude,
        "longitude": longitude,
        "temperature": temperature,
        "wind_speed": wind_speed,
        "incline_angle": incline_angle
    }

    response = requests.post(webhook_url, json=payload)  # Use o payload criado, não sensor_data

    if response.status_code == 200:
        print("Sensor data sent successfully.")
    else:
        print(f"Failed to send sensor data. Status code: {response.status_code}, Response: {response.text}")


def write_sensor_data_to_influxdb(client, sensor_data):
    client.write_api().write([sensor_data], database="Bucket02", time_precision='s')
    # Escreve os dados do sensor no InfluxDB
    #client.write_points([sensor_data], database="Bucket02", time_precision='s')

def generate_sensor_data(num_records):
    # Lista de nomes fictícios de antenas
    antennas = ["Antenna1", "Antenna2", "Antenna3", "Antenna4", "Antenna5"]
    
    # Dicionário com informações de localização para cada antena
    locations = {
        "Antenna1": {"latitude": -23.550520, "longitude": -46.633308},
        "Antenna2": {"latitude": -23.551032, "longitude": -46.631909},
        "Antenna3": {"latitude": -23.550123, "longitude": -46.632555},
        "Antenna4": {"latitude": -23.549764, "longitude": -46.632112},
        "Antenna5": {"latitude": -23.550987, "longitude": -46.631234}
    }

    


    # Lista para armazenar os dados gerados
    data = []

    # Loop para gerar dados para o número especificado de registros
    for _ in range(num_records):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        antenna = random.choice(antennas)
        gps_data = locations[antenna]
        temperature = random.uniform(20.0, 30.0)
        wind_speed = random.uniform(0.0, 10.0)
        incline_angle = random.uniform(-10.0, 10.0)

        # Cria um dicionário com todas as informações do sensor para o ponto atual
        sensor_data = {
            "measurement": "sensor_data",
            "time": timestamp,
            "tags": {
                "antenna": antenna,
                "latitude": gps_data["latitude"],
                "longitude": gps_data["longitude"]
            },
            "fields": {
                "temperature": temperature,
                "wind_speed": wind_speed,
                "incline_angle": incline_angle
            }
        }

        # Chama a função para enviar os dados do sensor para o InfluxDB
        write_sensor_data_to_influxdb(client, sensor_data)

        # Adiciona os dados à lista
        data.append(sensor_data)

        # Chama a função para enviar os dados do sensor para o webhook
        send_sensor_data_to_webhook(sensor_data)

        # Simula um atraso de 1 segundo entre registros de dados
        time.sleep(1)

    return data

# Exemplo de uso
if __name__ == "__main__":
    # Gera dados de sensor para x registros
    sensor_data = generate_sensor_data(10)

    # Exibe os dados gerados
    for data_point in sensor_data:
        print(data_point)







































'''import random
import time
from datetime import datetime
import requests

def send_sensor_data_to_webhook(sensor_data):
    webhook_url = "http://localhost:8000/webhook"  # Substitua pela URL correta
    response = requests.post(webhook_url, json=sensor_data)
    if response.status_code == 200:
        print("Sensor data sent successfully.")
    else:
        print(f"Failed to send sensor data. Status code: {response.status_code}, Response: {response.text}")

def generate_sensor_data(num_records):
    """
    Gera dados fictícios de séries temporais para um sensor.

    :param num_records: Número de registros de dados a serem gerados.
    :return: Uma lista de registros de dados, cada registro é um dicionário contendo informações do sensor.
    """
    # Lista de nomes fictícios de antenas
    antennas = ["Antenna1", "Antenna2", "Antenna3", "Antenna4", "Antenna5"]
    
    # Dicionário com informações de localização para cada antena
    locations = {
        "Antenna1": {"latitude": -23.550520, "longitude": -46.633308},
        "Antenna2": {"latitude": -23.551032, "longitude": -46.631909},
        "Antenna3": {"latitude": -23.550123, "longitude": -46.632555},
        "Antenna4": {"latitude": -23.549764, "longitude": -46.632112},
        "Antenna5": {"latitude": -23.550987, "longitude": -46.631234}
    }

    # Lista para armazenar os dados gerados
    data = []

    # Loop para gerar dados para o número especificado de registros
    for _ in range(num_records):
        # Obtenção do timestamp atual
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Seleção aleatória de uma antena
        antenna = random.choice(antennas)
        
        # Obtém dados de localização (latitude e longitude) da antena
        gps_data = locations[antenna]
        
        # Gera dados de temperatura, velocidade do vento e ângulo de inclinação de forma aleatória
        temperature = random.uniform(20.0, 30.0)
        wind_speed = random.uniform(0.0, 10.0)
        incline_angle = random.uniform(-10.0, 10.0)
        
        # Cria um dicionário com todas as informações do sensor para o ponto atual
        sensor_data = {
            "timestamp": timestamp,
            "antenna": antenna,
            "latitude": gps_data["latitude"],
            "longitude": gps_data["longitude"],
            "temperature": temperature,
            "wind_speed": wind_speed,
            "incline_angle": incline_angle
        }

        # Adiciona os dados à lista
        data.append(sensor_data)
        
        # Chama a função para enviar os dados do sensor para o webhook
        send_sensor_data_to_webhook(sensor_data)
        
        # Simula um atraso de 1 segundo entre registros de dados
        time.sleep(1)

    return data

# Exemplo de uso
if __name__ == "__main__":
    # Gera dados de sensor para 20 registros
    sensor_data = generate_sensor_data(50)
    
    # Exibe os dados gerados
    for data_point in sensor_data:
        print(data_point)
    

























import random
import time
from datetime import datetime
import requests

def generate_sensor_data(num_records):
    """
    Gera dados fictícios de séries temporais para um sensor.

    :param num_records: Número de registros de dados a serem gerados.
    :return: Uma lista de registros de dados, cada registro é uma tupla (timestamp, valor_do_sensor).
    """
    data = []
    for _ in range(num_records):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sensor_value = random.uniform(10.0, 100.0)  # Valor do sensor aleatório entre 10 e 100
        data.append((timestamp, sensor_value))
        time.sleep(1)  # Simula um atraso de 1 segundo entre registros de dados
    return data

# Exemplo de uso
if __name__ == "__main__":
    # Gera dados de sensor para 10 registros
    sensor_data = generate_sensor_data(50)
    
    # Exibe os dados gerados
    print(sensor_data)

   '''