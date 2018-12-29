"""
Checks whether we can call the hello endpoint.
"""

import pytest

import brewblox_ispindel.__main__ as main


@pytest.fixture
async def app(app):
    app.router.add_routes(main.routes)
    return app


async def test_hello(app, client):
    res = await client.post('/ispindel', data='hello')
    assert res.status == 200
    assert await res.text() == 'Hello world! (You said: "hello")'
