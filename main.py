import uvicorn
from fastapi import FastAPI

sinac_turismo_api = FastAPI()

@sinac_turismo_api.get("/")
async def root():
    return {'message':"Hello World"}