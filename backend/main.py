from contextlib import asynccontextmanager
from pathlib import path

import logfire
import uvicorn
from chat.core.config import settings
from chat.db.base import Database
from fastapi import FastAPI
from fastapi.responses import FileResponse

logfire.configure(token=settings.LOGFIRE_WRITE_TOKEN)
logfire.info("Hello, {place}!", place="World")

app = FastAPI()
THIS_DIR = path(__file__).parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with Database.connect() as db:
        yield {"db": db}


app = FastAPI(lifespan=lifespan)
logfire.instrument_fastapi(app)


@app.get("/")
async def index() -> FileResponse:
    return FileResponse((THIS_DIR / "chat_app.html"), media_type="text/html")


@app.get("/chat_app.ts")
async def main_ts() -> FileResponse:
    """Get the raw typescript code, it's compiled in the browser, forgive me."""
    return FileResponse((THIS_DIR / "chat_app.ts"), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("chat.chat_app:app", reload=True, reload_dirs=[str[THIS_DIR]])
