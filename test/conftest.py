import pytest
import config
from pymongo import MongoClient


@pytest.fixture
def db():
    conn = MongoClient(config.uri)
    return conn.invoice
