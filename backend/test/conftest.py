"""
Conftest file for pytest.
"""
import os
import json

import pytest
from unittest import mock

with open(os.getcwd() + "/test/config.json", "r", encoding="utf-8") as config_file:
    TEST_CONFIG = json.load(config_file)


@pytest.fixture(autouse=True)
def mock_encoding_vars(monkeypatch):
    """
    Mock the variables ALGORITHM, SECRET_KEY and salt.
    """
    monkeypatch.setenv("SECRET_KEY", "secret-key")
    monkeypatch.setenv("ALGORITHM", "HS256")
    monkeypatch.setenv("salt", "$2b$12$dMDN8PpZYSUQmCh.dM3euO")
    monkeypatch.setenv("SERVER_URL", "http://localhost")
    monkeypatch.setenv("DB_USER", "cleancommtest")
    monkeypatch.setenv("DB_PASSWORD", "cleancommtest_pwd")
    monkeypatch.setenv("DB_HOST", "localhost")
    monkeypatch.setenv("DB_NAME", "cleancommtestdb")
    monkeypatch.setenv("DB_PORT", "5432")
    

    yield

@pytest.fixture(autouse=True)
def connect(mocker):
    import psycopg2
    mocker.patch.object(psycopg2, "connect")
    yield
