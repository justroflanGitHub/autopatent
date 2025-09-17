# tests/unit/test_settings.py

import os
from unittest.mock import patch

import pytest

from src.infrastructure.config.settings import Settings


def test_settings_from_env():
    with patch.dict(os.environ, {
        'BOT_TOKEN': 'test_bot_token',
        'ROSPATENT_JWT': 'test_jwt',
        'GIGACHAT_CLIENT_ID': 'test_client_id',
        'GIGACHAT_CLIENT_SECRET': 'test_client_secret',
        'LOG_LEVEL': 'INFO'
    }, clear=True):
        settings = Settings.from_env()
        assert settings.bot_token == 'test_bot_token'
        assert settings.rospatent_jwt == 'test_jwt'
        assert settings.gigachat_client_id == 'test_client_id'
        assert settings.gigachat_client_secret == 'test_client_secret'


def test_settings_missing_bot_token():
    with patch.dict(os.environ, {'ROSPATENT_JWT': 'test_jwt'}, clear=True):
        with pytest.raises(ValueError, match="BOT_TOKEN is not set in environment variables"):
            Settings.from_env()


def test_settings_missing_rospatent_jwt():
    with patch.dict(os.environ, {'BOT_TOKEN': 'test_bot_token'}, clear=True):
        with pytest.raises(ValueError, match="ROSPATENT_JWT is not set in environment variables"):
            Settings.from_env()