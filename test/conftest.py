"""
Master file for pytest fixtures.
Any fixtures declared here are available to all test functions in this directory.
"""


import logging

import pytest
from brewblox_service import service, brewblox_logger, features

LOGGER = brewblox_logger(__name__)


@pytest.fixture(scope='session', autouse=True)
def log_enabled():
    """Sets log level to DEBUG for all test functions.
    Allows all logged messages to be captured during pytest runs"""
    logging.getLogger().setLevel(logging.DEBUG)
    logging.captureWarnings(True)


@pytest.fixture
def app_config() -> dict:
    return {
        'name': 'test_app',
        'host': 'localhost',
        'port': 1234,
        'debug': True,
    }


@pytest.fixture
def sys_args(app_config) -> list:
    return [
        'app_name',
        '--name', app_config['name'],
        '--host', app_config['host'],
        '--port', str(app_config['port']),
    ]


@pytest.fixture
def app(sys_args):
    app = service.create_app('default', raw_args=sys_args[1:])
    return app


@pytest.fixture
def client(app, aiohttp_client, loop):
    """Allows patching the app or aiohttp_client before yielding it.

    Any tests wishing to add custom behavior to app can override the fixture
    """
    LOGGER.info('Available features:')
    for name, impl in app.get(features.FEATURES_KEY, {}).items():
        LOGGER.info(f'Feature "{name}" = {impl}')

    return loop.run_until_complete(aiohttp_client(app))
