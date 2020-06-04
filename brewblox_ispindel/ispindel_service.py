"""
ISpindel http endpoint
"""

from aiohttp import web
from brewblox_service import brewblox_logger, mqtt

routes = web.RouteTableDef()

LOGGER = brewblox_logger(__name__)


def setup(app: web.Application):
    app.router.add_routes(routes)
    LOGGER.info('Setup iSpindel register endpoint')


@routes.post('/ispindel')
async def ispindel_handler(request: web.Request) -> web.Response:
    """
    This endpoint accepts request from iSpindel when configured to use the Generic HTTP POST.

    ---
    tags:
    - iSpindel
    summary: Endpoint to receive iSpindel metrics.
    description: The iSpindel wake up and send an HTTP POST request to this endpoint.
    operationId: ispindel/ispindel
    produces:
    - text/plain
    parameters:
    -
        in: body a iSpindel JSON containing current metrics
        name: body
        description: Input message
        required: true
        schema:
            type: string
    """
    body = await request.json()
    name = body.get('name')
    temperature = body.get('temperature')
    battery = body.get('battery')
    gravity = body.get('gravity')
    rssi = body.get('RSSI')
    angle = body.get('angle')
    if not name or not temperature:
        LOGGER.info(f'Bad request: "{body}"')
        return web.Response(status=400)
    topic = request.app['config']['history_topic']
    service_name = request.app['config']['name']
    await mqtt.publish(request.app,
                       topic,
                       {'key': service_name,
                        'data': {'temperature': temperature,
                                 'battery': battery,
                                 'angle': angle,
                                 'rssi': rssi,
                                 'gravity': gravity}})
    LOGGER.info(f'iSpindel {name}, temp: {temperature}, gravity: {gravity}')
    return web.Response(status=200)
