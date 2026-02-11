from abc import ABC, abstractmethod
from loguru import logger
import sqlite3
from contextlib import contextmanager
from app.config import settings
from fastapi import HTTPException, status

class BaseRepository(ABC):
    @abstractmethod
    def add_link(self, code: str, original_url: str, short_url: str,):
        pass

    @abstractmethod
    def delete_link(self, code: str):
        pass
    
    @abstractmethod
    def get_all_links(self):
        pass


class SqliteRepository(BaseRepository):
    def __init__(self, db_name):
        super().__init__()
        self.db_name = db_name
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as session:
            session.execute(
                """
                    CREATE TABLE IF NOT EXISTS short_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL UNIQUE,
                    original_url TEXT NOT NULL,
                    short_url TEXT NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                    );
                """
            )
            session.commit()
    
    def add_link(
            self, 
            code: str, 
            original_url: str,
            short_url: str,
    ):
        with self._get_connection() as session:
            try:
                cursor = session.execute(
                """
                    select id
                    from short_links
                    where code = ?
                """,
                (code,)
                )

                if cursor and cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"'{code}' is already in DB"
                    )

                session.execute(
                """
                    INSERT INTO short_links 
                    (code, original_url, short_url) 
                    VALUES (?, ?, ?)
                """,
                (code, original_url, short_url),
                )
                session.commit()
                logger.debug(f"'{code}' added success")
            except Exception as e:
                logger.exception(e)
        
    def get_link_by_code(self, code: str):
        with self._get_connection() as session:
            cursor = session.execute(
                """
                    SELECT id, code, original_url, short_url, created_at 
                    FROM short_links 
                    WHERE code = ?
                """, 
                (code,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_link(self, code: str):
        with self._get_connection() as session:
            try:
                session.execute(
                    """
                        DELETE FROM short_links WHERE code = ?
                    """,
                    (code,)
                )
                logger.debug(f"'{code}' drop success")
                session.commit()
            except Exception as e:
                logger.exception(e)
    
    def get_all_links(self) -> list:
        with self._get_connection() as session:
            try:
                cursor = session.execute(
                    """ 
                        SELECT * FROM short_links;
                    """
                )
                return [dict(row) for row in cursor.fetchall()]
            except Exception as e:
                logger.exception(e)

sqlite_repository = SqliteRepository(settings.DB_NAME)