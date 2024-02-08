from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

app = FastAPI()


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
    authorizationUrl="http://localhost:8000/protected",  # Substitua com a URL onde você lida com a autorização
)

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


@app.get("/get_sensor_data", response_model=List[SensorData])
async def get_sensor_data():
    # Retorna os dados armazenados até agora
    return stored_sensor_data

# Função de autenticação
async def authenticate_user(username: str, password: str):
    # Adicione a lógica de autenticação aqui
    # Retorne True se a autenticação for bem-sucedida, False caso contrário
    return username == "example" and password == "example_password"
