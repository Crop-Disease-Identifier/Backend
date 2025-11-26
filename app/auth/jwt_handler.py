
import time
import jwt
import os

JWT_SECRET = os.environ.get("SECRET")
JWT_ALGORITHM = os.environ.get("ALGORITHM", "HS256")

# Validate that SECRET is set
if not JWT_SECRET:
    raise ValueError("SECRET environment variable is not set. Please set it in your environment.")


def token_response(token: str):
    return {
        "access token": token
    }

def signJWT(userID: str):
    payload = {
        "userID": userID,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def decodeJWT(token : str):
    decode_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return decode_token if decode_token["expires"] >= time.time() else None