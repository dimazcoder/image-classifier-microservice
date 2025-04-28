from jose import jwt

from app.repositories.user_repository import UserRepository

SECRET_KEY = "common_secret_key_for_all_apis"
ALGORITHM = "HS256"

class JWTService:
    def __init__(self):
        self.repository = UserRepository()

    def get_user(self, token: str):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        return self.repository.get_user(user_id)
