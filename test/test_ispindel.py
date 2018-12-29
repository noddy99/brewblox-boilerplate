"""
Checks whether we can call the hello endpoint.
"""
from unittest.mock import call

import brewblox_ispindel.__main__ as main
import pytest
from asynctest import CoroutineMock
from brewblox_service import scheduler

TESTED = main.__name__

BODY_OK = '{"name":"iSpindel000","ID":4974097,"angle":83.49442,"temperature":21.4375,"temp_units":"C",' + \
          '"battery":4.035453,"gravity":30.29128,"interval":60,"RSSI":-76}'

EVENT_OK = {"angle": 83.49442, "temperature": 21.4375, "battery": 4.035453, "gravity": 30.29128, "rssi": -76}


class DummyListener:

    def subscribe(self,
                  exchange_name=None,
                  routing=None,
                  exchange_type=None,
                  on_message=None,
                  ):
        self.exchange_name = exchange_name
        self.routing = routing
        self.exchange_type = exchange_type
        self.on_message = on_message


@pytest.fixture
async def app(app, mock_publisher, dummy_listener):
    app.router.add_routes(main.routes)
    scheduler.setup(app)
    return app


@pytest.fixture
def dummy_listener(mocker):
    m = mocker.patch(TESTED + '.events.get_listener')
    m.return_value = DummyListener()
    return m.return_value


@pytest.fixture
def mock_publisher(mocker):
    m = mocker.patch(TESTED + '.events.get_publisher')
    m.return_value.publish = CoroutineMock()
    return m.return_value


async def test_ispindel(app, client, mock_publisher):
    res = await client.post('/ispindel', data=BODY_OK)
    assert res.status == 200
    assert await res.text() == ''
    assert mock_publisher.publish.call_count > 0
    assert mock_publisher.publish.call_args_list[-1] == call(
        'brewblox',
        'iSpindel000',
        EVENT_OK)
