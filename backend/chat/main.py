from contextlib import asynccontextmanager
from pathlib import Path

import logfire
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from chat.db.base import Database

# 'if-token-present' means nothing will be sent (and the example will work) if you don't have logfire configured
logfire.configure(send_to_logfire="if-token-present")
logfire.info("Hello, {place}!", place="World")

app = FastAPI()
THIS_DIR = Path(__file__).parent

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with Database.connect() as db:
        yield {"db": db}


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse((THIS_DIR / "chat/chat_app.html"), media_type="text/html")


@app.get("/chat_app.ts")
async def main_ts() -> FileResponse:
    """Get the raw typescript code, it's compiled in the browser, forgive me."""
    return FileResponse((THIS_DIR / "chat/chat_app.ts"), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("chat.chat_app:app", reload=True, reload_dirs=[str(THIS_DIR)])  # type: ignore
