import os
import uvicorn

from dotenv import load_dotenv
from fastapi import FastAPI

from fastapi_sqlalchemy import DBSessionMiddleware

from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from src.user import user

sinac_turismo_api = FastAPI()

load_dotenv('.env')

sinac_turismo_api.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
sinac_turismo_api.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sinac_turismo_api.include_router(user)


if __name__ == "__main__":
    uvicorn.run(sinac_turismo_api, host="0.0.0.0", port=8000, reload=True)
