import pytest
from app.service import Service
from app.sqlite_repository import SqliteRepository
from pyshorteners import Shortener
import os
from loguru import logger

DB_NAME = "test.db"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

@pytest.fixture(scope="session")
def drop_db():
    yield 
    os.unlink(DB_PATH)

@pytest.fixture(scope="session", autouse=True)
def repository():
    repo = SqliteRepository(DB_PATH)
    yield repo

@pytest.fixture(scope="session", autouse=True)
def shortener():
    return Shortener()

@pytest.fixture(scope="session", autouse=True)
def service(repository):
    return Service(repository)

@pytest.fixture(scope="session")
def links():
    links = [
        "https://okko.tv/",
        "https://start.ru/",
    ]
    return links

@pytest.fixture(scope="session", autouse=True)
def add_test_links(service, links):
    for link in links:
        service.add_short_link(link)

@pytest.mark.usefixtures("drop_db")
class TestService:
    def test_generate_short_url(self, service, shortener, links):
        for link in links:
            assert service.generate_short_url(link) == shortener.clckru.short(link)

    def test_get_code_from_short_url(self, service, shortener, links):
        for link in links:
            short_link = shortener.clckru.short(link)
            assert service.get_code_from_short_url(short_link) == short_link.split("/")[-1]
    
    def test_add_short_link(self, service, shortener, links):
        for link in links:
            assert service.add_short_link(link) == shortener.clckru.short(link)

    def test_get_all_links(self, service, links):
        service_links = [row.get("original_url") for row in service.get_all_links()] 
        assert all(link in service_links for link in links) == True


