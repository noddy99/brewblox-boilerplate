# BrewBlox Service for the iSpindel Hydrometer

The [iSpindel](https://github.com/universam1/iSpindel/) is a DIY wireless hydrometer and thermometer used to gather live readings of specific gravity and temperature when brewing beer.

[BrewBlox](https://brewpi.com/) is a modular brewery control system design to work with the BrewPi controller.


This brewblox service integrates the iSpindel hydrometer into BrewBlox.


## How does it work?

The iSpindel is configured to send metrics using HTTP.

When the iSpindel wake up (like every minute) it submits an HTTP POST request to the iSpindel BrewBlox service.

The metrics are then published to the event-bus, the BrewBlox history service persists the metrics into the InfluxDB database.

A Graph widget can be added in the BrewBlox UI to display the persisted metrics.

## Usage

### Deploy the iSpindel service in the BrewBlox stack

You need to add the service to your existing BrewBlox docker compose file:

```yaml
  ispindel:
    image: bdelbosc/brewblox-ispindel:rpi-develop
    restart: unless-stopped
    depends_on:
      - history
    ports:
      - "5080:5000"
    labels:
      - "traefik.port=5000"
      - "traefik.frontend.rule=PathPrefix: /ispindel"
```

The `brewblox-ispindel` docker images are available on [Docker Hub](https://cloud.docker.com/repository/docker/bdelbosc/brewblox-ispindel).

The image tag to use is:
- `rpi-develop` for the `arm` architecture (when deploying on a RaspberryPi)
- `develop` for the `amd` architecture

Note that this will expose an `HTTP` endpoint on port `5080` from your RaspberryPi,
this is needed because the iSpindel does not handle HTTPS.

Start your BrewBlox stack using `brewblox-ctl up`.

Check that the service is running:
```bash
# Run the docker-compose command from the directory holding the brewblox docker-compose file
$ docker-compose ps ispindel
       Name                     Command              State           Ports         
-----------------------------------------------------------------------------------
brewblox_ispindel_1   python3 -m brewblox_ispindel   Up      0.0.0.0:5080->5000/tcp

$ docker-compose logs ispindel
...
ispindel_1   | ======== Running on http://0.0.0.0:5000 ========
...
```


### Configure the iSpindel

First find the `IP` address of your BrewBlox server then check that:
[http://IP:5080/ispindel/_service/status](http://IP:5080/ispindel/_service/status)
replies with a:
```json
{"status": "ok"}
```

Note the port `5080` is the exposed port in the `docker-compose.yml` file.

Then:
- Switch the iSpindel on
- Press the reset button 3-4 times which sets up an access point
- Connect to the Wifi network "iSpindel"
- Open a browser on [http://192.168.4.1](http://192.168.4.1)
- From the "Configuration" menu, configure the Wifi access, then
  - Service Type: `HTTP`
    - Token:
    - Server Address: `<IP>`
    - Server Port: `5080`
    - Server URL: `/ispindel/ispindel`


Double check that your are using an **HTTP** service type (and not a TCP).

### Add Graph to your dashboard

From your dashboard `ACTIONS > New Widget` then select and create a `Graph` widget.

Once the iSpindel is configured to send data to BrewBlox, you should see its metrics when configuring the widget:

![graph-ispindel](./graph-ispindel.png)

  
## Development

### Run tests

```bash
# install pip3 if not already done
sudo pip3 install pipenv

# init the env
pipenv lock
pipenv sync -d

# Run the tests
pipenv run pytest
```

### Build a docker image

1. Install the [brewblox-tools](https://github.com/BrewBlox/brewblox-tools)

2. Go into the brewblox-ispindel directory and build the `rpi-latest` image
```bash
bbt-localbuild -r bdelbosc/brewblox-ispindel --tags latest -a arm
```

Use `-a amd` to build the `latest` image for amd architecture.

### Simulate iSpindel request

From the BrewBlox host:

```bash
curl -XPOST http://localhost:5080/ispindel/ispindel -d'{"name":"iSpindel000","ID":4974097,"angle":83.49442,"temperature":21.4375,"temp_units":"C","battery":4.035453,"gravity":30.29128,"interval":60,"RSSI":-76}'

# or using https
curl --insecure -XPOST https://localhost/ispindel/ispindel -d'{"name":"iSpindel000","ID":4974097,"angle":83.49442,"temperature":21.4375,"temp_units":"C","battery":4.035453,"gravity":30.29128,"interval":60,"RSSI":-76}'

```

### Check iSpindel service logs

Each time the service receive a request there is a log showing the temperature and gravity.
To run from the directory containing the `docker-compose.yml` file.

```bash
docker-compose logs ispindel
...
ispindel_1 | 2019/04/12 14:18:34 INFO __main__ iSpindel iSpindel000, temp: 21.75, gravity: 22.63023
ispindel_1 | 2019/04/12 14:19:05 INFO __main__ iSpindel iSpindel000, temp: 21.6875, gravity: 22.69526
```

### View iSpindel metrics persisted in the influxdb database

To run from the directory containing the `docker-compose.yml` file.

```sql
docker-compose exec influx influx
> USE brewblox
> SHOW SERIES
key
---
iSpindel000 -- This is the name given to the iSpindel
sparkey
spock

> SELECT * FROM "iSpindel000"
name: iSpindel000
time                angle    battery  gravity   rssi temperature
----                -----    -------  -------   ---- -----------
1546121491626257000 83.49442 4.035453 30.29128  -76  21.4375
1546121530861939000 84.41665 4.035453 30.75696  -75  19.125

> -- Latest metrics  
> PRECISION rfc3339
> SELECT * FROM "iSpindel000" WHERE time > now() -5m ORDER BY time DESC LIMIT 10
time                         Combined Influx points angle    battery  gravity  rssi temperature
----                        ----------------------- -----    -------  -------  ---- -----------
2019-04-12T14:15:29.715678Z 1                       71.6947  4.233577 22.67045 -68  21.9375
2019-04-12T14:14:58.997279Z 1                       71.58447 4.233577 22.51496 -67  21.9375

```

### Continuous integration pipeline

Using [Azure](https://dev.azure.com), the [pipeline](./azure-pipelines.yml) automatically test and deploy all commits
pushed on the GitHub repository.

This means that docker images for `arm` and `amd` are published on [Docker Hub](https://hub.docker.com/) and the python package is deployed on [PyPi](https://pypi.org/).

## TODO

- Debug mode where the service subscribes to the `brewcast` channel to debug what is published.
- Support an HTTP token that can be set in the docker-compose file.

## Limitations

- There is no security on the iSpindel endpoint
