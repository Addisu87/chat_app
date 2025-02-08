import asyncio
import sqlite3
from concurrent.futures.thread import ThreadPoolExecutor
from typing import TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


class Database:
    """Redimentary database to store chat messages in SQLite.
    use a thread pool executor to run queries asynchronously.
    """

    conn: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor
