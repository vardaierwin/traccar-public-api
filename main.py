from fastapi import FastAPI, Request
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")  # Ezt később a DB-hez használjuk

@app.api_route("/locations", methods=["GET", "POST", "PUT"])
@app.api_route("/", methods=["GET", "POST", "PUT"])
async def catch_all(request: Request):
    """Catch all requests to see what Traccar actually sends"""

    # Log request method, URL és query params
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Query params: {dict(request.query_params)}")

    # Log body, ha van
    try:
        body_bytes = await request.body()
        if body_bytes:
            # Próbáljuk dekódolni UTF-8-ként
            try:
                body_text = body_bytes.decode("utf-8")
                logger.info(f"Body: {body_text}")
            except UnicodeDecodeError:
                logger.info(f"Body (raw bytes): {body_bytes}")
        else:
            logger.info("No body sent")
    except Exception as e:
        logger.error(f"Error reading body: {e}")

    return "OK"

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Diagnostic mode active"}
