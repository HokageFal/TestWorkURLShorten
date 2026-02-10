import pytest
import sqlite3
from src.database import Database


class InMemoryDatabase(Database):
    def __init__(self):
        self.db_path = ":memory:"
        self._conn = sqlite3.connect(":memory:", check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        cursor = self._conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_code TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_short_code 
            ON urls(short_code)
        """)
        self._conn.commit()
    
    def get_connection(self):
        from contextlib import contextmanager
        
        @contextmanager
        def connection():
            try:
                yield self._conn
                self._conn.commit()
            except Exception:
                self._conn.rollback()
                raise
        
        return connection()


@pytest.fixture
def in_memory_db():
    db = InMemoryDatabase()
    yield db
    db._conn.close()
