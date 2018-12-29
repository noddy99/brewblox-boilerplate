"""
Example of how to import and use the brewblox service
"""
from typing import Union

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
    operationId: brewblox_ispindel/ispindel
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
    input = await request.text()
    return web.Response(body=f'Hello world! (You said: "{input}")')


async def on_message(subscription: events.EventSubscription, key: str, message: Union[dict, str]):
    """Example message handler for RabbitMQ events.

    Services can choose to publish / subscribe events to communicate between them.
    These events are for loose communication: you broadcast something,
    and don't really care by whom it gets picked up.

    When subscribing to an event, you provide a callback (example: this function)
    that will be called every time a relevant event is published.

    Args:
        subscription (events.EventSubscription):
            The subscription that triggered this callback.

        key (str): The routing key of the published event.
            This will always be specific - no wildcards.

        message (dict | str): The content of the event.
            If it was a JSON message, this is a dict. String otherwise.

    """

    LOGGER.info(f'Message from {subscription}: {key} = {message} ({type(message)})')


def add_events(app: web.Application):
    """Add event handling

    Subscriptions can be made at any time using `EventListener.subscribe()`.
    They will be declared on the remote amqp server whenever the listener is connected.

    Message interest can be specified by setting exchange name, and routing key.

    For `direct` and `fanout` exchanges, messages must match routing key exactly.
    For `topic` exchanges (the default), routing keys can be multiple values, separated with dots (.).
    Routing keys can use regex and wildcards.

    The simple wildcards are `*` and `#`.

    `*` matches a single level.

    "controller.*.sensor" subscriptions will receive (example) routing keys:
    - controller.block.sensor
    - controller.container.sensor

    But not:
    - controller
    - controller.nested.block.sensor
    - controller.block.sensor.nested

    `#` is a greedier wildcard: it will match as few or as many values as it can
    Plain # subscriptions will receive all messages published to that exchange.

    A subscription of "controller.#" will receive:
    - controller
    - controller.block.sensor
    - controller.container.nested.sensor

    For more information on this, see https://www.rabbitmq.com/tutorials/tutorial-four-python.html
    and https://www.rabbitmq.com/tutorials/tutorial-five-python.html
    """

    # Enable the task scheduler
    # This is required for the `events` feature
    scheduler.setup(app)

    # Enable event handling
    # Event subscription / publishing will be enabled after you call this function
    events.setup(app)

    # No subscription needed
    # listener = events.get_listener(app)
    # listener.subscribe('brewblox', '#', on_message=on_message)


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
