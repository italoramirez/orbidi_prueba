# app = FastAPI()

# @app.get('/')
# def hello():
#    return {"response": "hllo world"}

from fastapi import FastAPI, BackgroundTasks
import uvicorn
from pydantic import BaseModel
import requests
import psycopg2
from datetime import datetime
from sqlalchemy import create_engine, Column, DateTime, String, JSON, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_HOST = "db"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASS = "1234"
DB_NAME = "orbidi"

Base = declarative_base()


class APICall(Base):
    __tablename__ = "api_calls"

    id = Column(Integer, primary_key=True, autoincrement=True)
    call_datetime = Column(DateTime)
    params = Column(JSON)
    result = Column(String)

    def __init__(self, call_datetime, params, result):
        self.call_datetime = call_datetime
        self.params = params
        self.result = result


HUBSPOT_API_KEY = "pat-na1-bfa3f0c0-426b-4f0e-b514-89b20832c96a"
HUBSPOT_CREATE_CONTACT_URL = "https://api.hubapi.com/crm/v3/objects/contacts"

CLICKUP_API_KEY = "pk_3182376_Q233NZDZ8AVULEGGCHLKG2HFXWD6MJLC"
CLICKUP_LIST_ID = "900200532843"
CLICKUP_CREATE_TASK_URL = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"

app = FastAPI()


class ContactCreate(BaseModel):
    email: str
    firstname: str
    lastname: str
    phone: str
    website: str


def log_api_call(call_datetime: datetime, params: dict, result: str):
    # Conexión a la base de datos
    engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    Session = sessionmaker(bind=engine)
    session = Session()

    # Creación de un nuevo registro en la tabla api_calls
    api_call = APICall(call_datetime=call_datetime, params=params, result=result)
    session.add(api_call)
    session.commit()


@app.post("/create_contact")
async def create_contact(contact: ContactCreate, background_tasks: BackgroundTasks):
    # Llamada a la API de HubSpot para crear el contacto
    headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}"}
    data = {
        "properties": [
            {"property": "email", "value": contact.email},
            {"property": "firstname", "value": contact.firstname},
            {"property": "lastname", "value": contact.lastname},
            {"property": "phone", "value": contact.phone},
            {"property": "website", "value": contact.website},
        ]
    }
    response = requests.post(HUBSPOT_CREATE_CONTACT_URL, headers=headers, json=data)

    log_api_call(datetime.now(), contact.dict(), response.text)
