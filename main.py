from fastapi import FastAPI, Request
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

@app.api_route("/locations", methods=["GET", "POST", "PUT"])
@app.api_route("/", methods=["GET", "POST", "PUT"])
async def catch_all(request: Request):
    """Catch all requests to see what Traccar actually sends"""
    
    # Log request method and URL
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Query params: {dict(request.query_params)}")
    
    # Try to get body content
    try:
        if request.method == "POST":
            content_type = request.headers.get("content-type", "")
            if "json" in content_type:
                body = await request.json()
                logger.info(f"JSON body: {body}")
            else:
                body = await request.body()
                logger.info(f"Raw body: {body}")
        else:
            logger.info("GET request - no body")
    except Exception as e:
        logger.error(f"Error reading body: {e}")
    
    return "OK"

@app.get("/ping")
def ping():
    return {"status": "ok", "message": "Diagnostic mode active"}