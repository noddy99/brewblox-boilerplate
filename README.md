# BrewBlox iSpindel service

This a BrewBlox service to support [iSpindel](https://github.com/universam1/iSpindel/)
an electronic hydrometer.


This project is under active development.


## How does it work ?

The iSpindel is configured to send metrics using the generic HTTP POST protocol.

When the iSpindel wake up (like every 2 minutes) it submits a POST request containing the metrics to the iSpindel BrewBlox service.

The service then publish metrics to the event-bus, the BrewBlox history service is in charge to persist the metrics into the InfluxDB database.

## Configuration

### iSpindel

Assuming BrewBlox is accessible at http://<BREWBLOX_IP>:9000/:

- Switch iSpindel on
- Press the reset button 3-4 times which sets up an access point
- Connect to the Wifi network "iSpindel"
- Open a browser on [http://192.168.4.1](http://192.168.4.1)
- From the "Configuration" menu, configure the Wifi access, then
  - Service Type: `HTTP`
    - Token:
    - Server Address: `<BREWBLOX_IP>`
    - Server Port: `9000`
    - Server URL: `/ispindel/ispindel`



### Deploy on the BrewBlox stack

Docker images are available on docker hub, you need to add the service to your docker compose file:
```yaml
  ispindel:
    image: bdelbosc/brewblox-ispindel:rpi-latest
    depends_on:
      - history
    labels:
      - "traefik.port=5000"
      - "traefik.frontend.rule=PathPrefix: /ispindel"
```

Note that the image tag to use is:
- `rpi-latest` for the `arm` architecture (when deploying on a RaspberryPi)
- `latest` for the `amd` architecture

### Add Graph to your dashboard

From your dashboard add "ACTIONS" > "New Widget" 
Select a Graph widget type, give it a title and Create.

Then configure Metrics you should see something like that:

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
curl -XPOST http://localhost:9000/ispindel/ispindel
-d'{"name":"iSpindel000","ID":4974097,"angle":83.49442,"temperature":21.4375,"temp_units":"C","battery":4.035453,"gravity":30.29128,"interval":60,"RSSI":-76}'
```

### View influxdb data

This is assuming a BrewBlox system is active in the current directory.

```sql
docker-compose exec influx influx
> USE brewblox
> SELECT * FROM "iSpindel000"
name: iSpindel000
time                angle    battery  gravity   rssi temperature
----                -----    -------  -------   ---- -----------
1546121491626257000 83.49442 4.035453 30.29128  -76  21.4375
1546121530861939000 84.41665 4.035453 30.75696  -75  19.125

```

## Limitations

- There is no security on the ispindel endpoint
