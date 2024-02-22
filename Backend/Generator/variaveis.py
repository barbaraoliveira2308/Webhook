import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="Backend\Generator\Influx_var.env")

host=os.getenv("INFLUXDB_HOST")
port=int(os.getenv("INFLUXDB_PORT", 8086))
username=os.getenv("INFLUXDB_USER")
password=os.getenv("INFLUXDB_PASSWORD")
influx_db=os.getenv('INFLUXDB_DB')

print(f"InfluxDB Host: {username}")