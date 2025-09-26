from fastapi import FastAPI, Request
from pydantic import BaseModel
import psycopg2
import os

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

class Location(BaseModel):
    device_id: str
    latitude: float
    longitude: float
    # Extra adatok, ha szükségesek (pl. időbélyeg vagy sebesség)
    timestamp: str = None
    speed: float = None

@app.post("/locations")
async def receive_location(loc: Location):
    # Csak Neon DB-be mentés
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # Ha speed nincs megadva, NULL-t használunk
        speed_value = loc.speed if loc.speed is not None else None
        cur.execute(
            "INSERT INTO locations (device_id, latitude, longitude, timestamp, speed) VALUES (%s, %s, %s, %s, %s)",
            (loc.device_id, loc.latitude, loc.longitude, loc.timestamp, speed_value)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "ok", "device_id": loc.device_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Public FastAPI is running!"}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Public FastAPI is running!"}