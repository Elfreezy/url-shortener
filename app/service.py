from pyshorteners import Shortener
from app.sqlite_repository import sqlite_repository, SqliteRepository
from loguru import logger
shortener = Shortener()

class Service():
    def __init__(self, repository: SqliteRepository):
        self.repository = repository
        
    def add_short_link(self, original_url: str):
        short_url = self.generate_short_url(original_url)
        code = self.get_code_from_short_url(short_url)
        self.repository.add_link(code, original_url, short_url)
        return short_url
    
    def get_short_link_by_code(self, code: str):
        short_link = None
        if link_row := self.repository.get_link_by_code(code):
            short_link = link_row.get("short_url")

        return short_link
    
    def get_all_links(self) -> list:
        return self.repository.get_all_links()

    def delete_link_by_code(self, code: str):
        return self.repository.delete_link(code)
    
    def generate_short_url(self, original_url: str) -> str:
        return shortener.clckru.short(original_url)
    
    def get_code_from_short_url(self, short_url: str) -> str:
        return short_url.split("/")[-1] if short_url else None
    
service = Service(sqlite_repository)