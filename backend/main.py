#!/usr/bin/env python
"""
(C)Copyright 2023, PROJECT
Guy Ahonakpon GBAGUIDI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers import auth

from logger import uvicorn_access_logger, uvicorn_errors_logger

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.AUTH)


@app.get("/")
def read_main():
    """default function"""
    return {"message": "Welcome to CLEANCOMM REST API development"}
