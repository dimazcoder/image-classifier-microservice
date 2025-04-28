from fastapi import APIRouter, Request
from datetime import datetime
import socket

router = APIRouter()

@router.get("/")
def read_root():
    return {'status': "ok"}

@router.get("/status")
def read_root(request: Request):
    current_time = datetime.now().isoformat()
    # hostname = socket.gethostname()
    hostname = request.url.hostname

    return {
        "service_name": "Image Classifier",
        "status": "ok",
        "datetime": current_time,
        "node_name": hostname
    }
