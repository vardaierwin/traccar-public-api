from fastapi import FastAPI, Request
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os
import logging

# --- Logger ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI ---
app = FastAPI()

# --- DB setup ---
DATABASE_URL = os.getenv("DATABASE_URL")  # pl. Neon DB connection string
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- DB model ---
class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True, index=True)
    imei = Column(Integer)       # device identifier hash
    lat = Column(Float)
    lon = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# --- Endpoint ---
@app.post("/locations")
async def receive_position(request: Request):
    """
    Fogadja a Traccar Client JSON-t.
    Példa JSON:
    {
        "device_id": "Erwin",
        "location": {
            "coords": {
                "latitude": 46.77,
                "longitude": 23.58
            }
        }
    }
    """
    try:
        data = await request.json()
        logger.info(f"Received data: {data}")

        device_id = data.get("device_id", "unknown")
        coords = data.get("location", {}).get("coords", {})
        lat = coords.get("latitude")
        lon = coords.get("longitude")

        if lat is not None and lon is not None:
            imei = abs(hash(device_id)) % 2147483647  # biztos integer
            with SessionLocal() as db:
                pos = Position(imei=imei, lat=float(lat), lon=float(lon))
                db.add(pos)
                db.commit()
                db.refresh(pos)
            logger.info(f"Position saved: imei={imei}, lat={lat}, lon={lon}")
            return "OK"  # Traccar ACK
        else:
            logger.warning("Missing latitude or longitude in received data")
            return "ERROR: Missing data"
    except Exception as e:
        logger.error(f"Error saving position: {str(e)}")
        return f"ERROR: {str(e)}"

# --- Health checks ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "FastAPI Traccar-compatible API is running!"}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "FastAPI Traccar-compatible API is alive!"}
