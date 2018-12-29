"""
Example of how to import and use the brewblox service
"""
from aiohttp import web
from brewblox_service import brewblox_logger, events, scheduler, service

routes = web.RouteTableDef()
LOGGER = brewblox_logger(__name__)


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
    name = body.get("name")
    temperature = body.get("temperature")
    battery = body.get("battery")
    gravity = body.get("gravity")
    rssi = body.get("RSSI")
    angle = body.get("angle")
    if not name or not temperature:
        LOGGER.info("Bad request: " + str(request.text()))
        return web.Response(status=400)
    publisher = events.get_publisher(request.app)
    await publisher.publish('brewblox', name, {'temperature': temperature,
                                               'battery': battery,
                                               'angle': angle,
                                               'rssi': rssi,
                                               'gravity': gravity})
    LOGGER.info(f'iSpindel {name}, temp: {temperature}, gravity: {gravity}')
    return web.Response(status=200)


def add_events(app: web.Application):
    # Enable the task scheduler
    # This is required for the `events` feature
    scheduler.setup(app)

    # Enable event handling
    # Event subscription / publishing will be enabled after you call this function
    events.setup(app)


def main():
    app = service.create_app(default_name='ispindel')

    # Init events
    add_events(app)

    # Register routes
    app.router.add_routes(routes)

    # Add all default endpoints, and adds prefix to all endpoints
    #
    # Default endpoints are:
    # {prefix}/api/doc (Swagger documentation of endpoints)
    # {prefix}/_service/status (Health check: this endpoint is called to check service status)
    #
    # The prefix is automatically added for all endpoints. You don't have to do anything for this.
    # To change the prefix, you can use the --name command line argument.
    #
    # See brewblox_service.service for more details on how arguments are parsed.
    #
    # The default value is "YOUR_PACKAGE" (provided in service.create_app()).
    # This means you can now access the example/endpoint as "/YOUR_PACKAGE/example/endpoint"
    service.furnish(app)

    # service.run() will start serving clients async
    service.run(app)


if __name__ == '__main__':
    main()
