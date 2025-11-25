from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import os

import sqlite3

DB_PATH = "database.db"

app = FastAPI()


def connectToDB():
    try:
        connection = sqlite3.connect(DB_PATH)
    except sqlite3.Error:
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error: Database failed to connect.",
        )
    return connection

def CreateDB():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS TickSightings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            dueDate DATETIME NOT NULL,
            taskImportance INTEGER NOT NULL,
            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME NOT NULL,

            UNIQUE(task, createdAt)
        );
        """
    )
    conn.commit()
    conn.close()

    print("DB successfully created")

def loadSeedData():
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    if not os.path.exists(DB_PATH):
        print("DB not found, Creating DB")
        CreateDB()
        loadSeedData()

    else:
        print("DB exists. Skipping data load")

    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}
