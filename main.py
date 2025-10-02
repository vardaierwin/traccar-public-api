from fastapi import FastAPI, Request
import logging
import os
from sqlalchemy import create_engine, text
from datetime import datetime
import pytz

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# DB kapcsolat (Render / Neon PostgreSQL)
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

@app.post("/locations")
async def save_location(request: Request):
    """Fogadja az OwnTracks JSON-t és DB-be menti"""
    try:
        data = await request.json()
        logger.info(f"JSON body: {data}")

        # Mezők kiszedése
        user_id = data.get("tid", "unknown")
        device_id = data.get("_type", "unknown")
        lat = data.get("lat")
        lon = data.get("lon")
        tst_raw = data.get("tst")  # Unix timestamp (UTC)
        batt = data.get("batt")
        acc = data.get("acc")
        alt = data.get("alt")
        speed = data.get("vel")

        # Idő konvertálása UTC → Europe/Bucharest
        utc_dt = datetime.utcfromtimestamp(tst_raw)
        local_tz = pytz.timezone("Europe/Bucharest")
        tst_local = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz).replace(tzinfo=None)

        # DB insert
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO locations (
                        user_id, device_id, lat, lon, tst, batt, acc, alt, speed
                    ) VALUES (
                        :user_id, :device_id, :lat, :lon, :tst, :batt, :acc, :alt, :speed
                    )
                """),
                {
                    "user_id": user_id,
                    "device_id": device_id,
                    "lat": lat,
                    "lon": lon,
                    "tst": tst_local,
                    "batt": batt,
                    "acc": acc,
                    "alt": alt,
                    "speed": speed
                }
            )
            conn.commit()

        return {"status": "ok", "message": "Location saved"}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Diagnostic mode active"}
