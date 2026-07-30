from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Any

app = FastAPI(title="Security & Auth Service", version="1.0.0")

SECRET_KEY = "enterprise-super-secret-key"
ALGORITHM = "HS256"
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/security/token")
async def generate_token(role: str = "executive"):
    # In production, this would validate username/password against a DB/LDAP
    token_payload = {"sub": "user123", "role": role}
    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/security/verify")
async def verify_access(payload: dict = Depends(verify_token)):
    return {"status": "authorized", "role": payload.get("role")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8105, reload=True)
