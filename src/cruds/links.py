import logging
from typing import Optional
import sqlite3
from src.database import Database

logger = logging.getLogger(__name__)


def create_link(db: Database, original_url: str, short_code: str) -> int:
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO urls (original_url, short_code) VALUES (?, ?)",
                (original_url, short_code)
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        logger.error(f"Ошибка целостности при создании ссылки {short_code}: {str(e)}")
        raise ValueError(f"Код '{short_code}' уже существует")
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка БД при создании ссылки: {str(e)}")
        raise


def get_link_by_code(db: Database, short_code: str) -> Optional[dict]:
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT original_url FROM urls WHERE short_code = ?",
                (short_code,)
            )
            row = cursor.fetchone()
            return {"original_url": row["original_url"]} if row else None
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка БД при получении ссылки {short_code}: {str(e)}")
        raise


def code_exists(db: Database, short_code: str) -> bool:
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM urls WHERE short_code = ? LIMIT 1",
                (short_code,)
            )
            return cursor.fetchone() is not None
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка БД при проверке существования кода {short_code}: {str(e)}")
        raise


def delete_link(db: Database, short_code: str) -> bool:
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM urls WHERE short_code = ?",
                (short_code,)
            )
            return cursor.rowcount > 0
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка БД при удалении ссылки {short_code}: {str(e)}")
        raise


def get_stats(db: Database, short_code: str) -> Optional[dict]:
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, original_url, short_code, created_at FROM urls WHERE short_code = ?",
                (short_code,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "original_url": row["original_url"],
                    "short_code": row["short_code"],
                    "created_at": row["created_at"]
                }
            return None
    except sqlite3.OperationalError as e:
        logger.error(f"Ошибка БД при получении статистики {short_code}: {str(e)}")
        raise
