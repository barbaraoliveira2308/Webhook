from fastapi import FastAPI, Query
from pydantic import BaseModel, ValidationError
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Adicione o URL do seu frontend aqui
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SensorData(BaseModel):
    timestamp: str
    antenna: str
    latitude: float
    longitude: float
    temperature: float
    wind_speed: float
    incline_angle: float


# Lista para armazenar dados simulados (você pode substituir por seus dados reais do sensor)
stored_sensor_data: List[SensorData] = []

# Configurando OAuth2 com tokenUrl e authorizationUrl
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl="OAuth2AuthorizationCodeBearer",  # Substitua com a URL onde você lida com a obtenção do token
    authorizationUrl="hhttp://127.0.0.1:8000/protected", # Substitua com a URL onde você lida com a autorização
    # Substitua com a URL onde você lida com a autorização
)
'''

'''
@app.post("/login", response_model=dict)

async def login_page(username: str, password: str):
    if username == "usario" and password == "password":
    # Lógica de autenticação, se necessário, pode ser adicionada aqui
      return {"mensagem": "login bem sucedido"}

    else: 
        raise HTTPException(status_code=401, detail= "credenciais invalidas")
    
@app.get("/login/username/password", response_model= login_page)
async def login_page(username: str, password: str):
    if username == "usario" and password == "password":
    # Lógica de autenticação, se necessário, pode ser adicionada aqui
      return {"mensagem": "login bem sucedido"}

    else: 
        raise HTTPException(status_code=401, detail= "credenciais invalidas")
    


@app.post("/webhook")
async def receive_sensor_data(sensor_data: SensorData):
    # Lógica para processar os dados recebidos, como salvar no banco de dados, etc.
    # Você pode acessar os dados através de sensor_data.timestamp, sensor_data.antenna, etc.
    stored_sensor_data.append(sensor_data)
    return {"status": "Data received successfully"}

# Rota protegida que usa o esquema OAuth2
@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    return {"token": token}


@app.get("/sensor_data", response_model=List[SensorData])
async def get_sensor_data():
    # Retorna os dados armazenados até agora
    return stored_sensor_data 



@app.get("/sensor_data/", response_model=List[SensorData])
async def get_sensor_data(
    antenna: str = Query(None, description="Filtrar por antena"),
    latitude: float = Query(None, description="Filtrar por latitude"),
    longitude: float = Query(None, description="Filtrar por longitude"),
    temperature_gt: float = Query(None, description="Filtrar por temperatura maior que"),
    temperature_lt: float = Query(None, description="Filtrar por temperatura menor que"),
):
    filtered_data = []

    for data in stored_sensor_data:
        # Aplicar filtros
        if antenna and data.antenna != antenna:
            continue
        if latitude and data.latitude != latitude:
            continue
        if longitude and data.longitude != longitude:
            continue
        if temperature_gt and data.temperature <= temperature_gt:
            continue
        if temperature_lt and data.temperature >= temperature_lt:
            continue

        # Se todos os filtros passarem, adiciona aos dados filtrados
        filtered_data.append(data)

    # Retorna os dados após o loop
    return filtered_data
    print(filtered_data)


# Função de autenticação
async def authenticate_user(username: str, password: str):
    # Adicione a lógica de autenticação aqui
    # Retorne True se a autenticação for bem-sucedida, False caso contrário
    return username == "example" and password == "example_password"


from flask import Flask, request, jsonify
from influxdb_client import InfluxDBClient
 
app = Flask(__name__)
 
# InfluxDB configurations
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "BPONyOJnBJ22j42ZD43RFUJcboxD_xwW6gkgNulUUFXGYUcOdYLpVZSL1HNYQIcCPgcjb5RiQ--rdtwKgTw2Jw=="
INFLUXDB_ORG = "evoleo"
INFLUXDB_BUCKET = "Bucket01"
 
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
 
API_ACCESS_TOKEN = "ABCD123456"  
 
@app.route('/fetch-data', methods=['GET'])
def fetch_data():
    # Authenticate request
    auth_token = request.headers.get('Authorization')
    if auth_token != API_ACCESS_TOKEN:
        return jsonify({"error": "Unauthorized access"}), 403
 
    # Define the Flux query
    query = '''
        from(bucket: "Bucket01")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "sensor_info")
        |> filter(fn: (r) =>
            r["_field"] == "gps_latitude" or
            r["_field"] == "gps_longitude" or
            r["_field"] == "humidity" or
            r["_field"] == "inclinometer_x" or
            r["_field"] == "inclinometer_y" or
            r["_field"] == "temperature" or
            r["_field"] == "wind_speed")
        |> filter(fn: (r) =>
            r["sensor"] == "antenna_0" or
            r["sensor"] == "antenna_1" or
            r["sensor"] == "antenna_2" or
            r["sensor"] == "antenna_4")
        |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
        |> yield(name: "mean")
    '''
 
    # Fetch data from InfluxDB
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    data = []
    for table in result:
        for record in table.records:
            tags = {key: value for key, value in record.values.items() if key not in ['_start', '_stop', '_time', '_value', '_field', '_measurement']}
            data.append({
                'time': record.get_time().isoformat(),
                'measurement': record.get_measurement(),
                'field': record.get_field(),
                'value': record.get_value(),
                'tags': tags
            })
 
    return jsonify(data)
 
if __name__ == '__main__':
    app.run(debug=True)
 



@app.route('/fetch-data-by-antenna', methods=['GET'])
def fetch_data_by_antenna():
    auth_token = request.headers.get('Authorization')
    if auth_token != API_ACCESS_TOKEN:
        return jsonify({"error": "Unauthorized access"}), 403
 
    # Get the antenna parameter from the query string
    antenna = request.args.get('antenna')
    if not antenna:
        return jsonify({"error": "Antenna parameter is required"}), 400
 
    query = f'''
        from(bucket: "Bucket01")
        |> range(start: -1h)
        |> filter(fn: (r) => r["_measurement"] == "sensor_info")
        |> filter(fn: (r) =>
            r["_field"] == "gps_latitude" or
            r["_field"] == "gps_longitude" or
            r["_field"] == "humidity" or
            r["_field"] == "inclinometer_x" or
            r["_field"] == "inclinometer_y" or
            r["_field"] == "temperature" or
            r["_field"] == "wind_speed")
        |> filter(fn: (r) => r["sensor"] == "{antenna}")
        |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
        |> yield(name: "mean")
    '''
 
    result = client.query_api().query(org=INFLUXDB_ORG, query=query)
    data = []
    for table in result:
        for record in table.records:
            tags = {key: value for key, value in record.values.items() if key not in ['_start', '_stop', '_time', '_value', '_field', '_measurement']}
            data.append({
                'time': record.get_time().isoformat(),
                'measurement': record.get_measurement(),
                'field': record.get_field(),
                'value': record.get_value(),
                'tags': tags
            })
 
    return jsonify(data)




"from fastapi import FastAPI, Header, Depends
from pydantic import BaseModel
 
app = FastAPI()
 
# Define a custom class for the parameters
class User(BaseModel):
    name: str
    age: int
 
# Define a function to verify the token in the header
def verify_token(token: str = Header(None)):
    # Here you can write your code to check the validity of the token
    # For example, you can use jwt.decode() to decode the token and verify the claims
    # If the token is invalid, you can raise an HTTPException with status code 401
    # If the token is valid, you can return the user_id or any other information
    return user_id
 
# Define a method that depends on the token verification
@app.post("/users")
async def create_user(user: User, user_id: str = Depends(verify_token)):
    # Here you can write your code to create a new user with the given parameters
    # You can also use the user_id from the token verification function
    # For example, you can insert the user data into a database
    # You can return a response with a status code and a message
    return {"status": 201, "message": f"Created user {user.name} with id {user_id}"}
""


           '''
@app.get("/sensor_data/")
async def read_items(meutoken: str = Header(default=None)):
    if meutoken is None or meutoken != meutoken:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return {"message": "Authorized access", "token_value": meutoken}
'''







@app('/sensor_data', response_model=list[SensorData])
async def get_sensor_data (
     antenna: str = Query(None, description="Filtrar por antena"),
    latitude: float = Query(None, description="Filtrar por latitude"),
    longitude: float = Query(None, description="Filtrar por longitude"),
    temperature_gt: float = Query(None, description="Filtrar por temperatura maior que"),
    temperature_lt: float = Query(None, description="Filtrar por temperatura menor que"),
)
    








    @app.get("/sensor_data")
async def verify_token(meutoken: str = Header(default=None)):
    if meutoken is None or meutoken != API_ACCESS_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    return {"message": "Authorized access", "token_value": meutoken}



verify_token(meutoken