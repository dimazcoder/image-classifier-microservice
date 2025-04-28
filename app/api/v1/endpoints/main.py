from fastapi import APIRouter

router = APIRouter()

@router.post("/")
def read_root():
    return {'message': "Hello from Image Classifier."}
