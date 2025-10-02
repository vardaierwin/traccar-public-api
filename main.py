from fastapi import FastAPI, Request
import logging
import os
from sqlalchemy import create_engine, text

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
        lat = data.get("lat")
        lon = data.get("lon")
        tst = data.get("tst")   # timestamp
        batt = data.get("batt")
        acc = data.get("acc")
        alt = data.get("alt")

        # DB insert
        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO locations (lat, lon, tst, batt, acc, alt)
                    VALUES (:lat, :lon, to_timestamp(:tst), :batt, :acc, :alt)
                """),
                {"lat": lat, "lon": lon, "tst": tst, "batt": batt, "acc": acc, "alt": alt}
            )
            conn.commit()

        return {"status": "ok", "message": "Location saved"}

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"status": "error", "message": str(e)}

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Diagnostic mode active"}
