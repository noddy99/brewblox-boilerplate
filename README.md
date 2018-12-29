# BrewBlox iSpindel service

This a BrewBlox service to integrate [iSindel](https://github.com/universam1/iSpindel/)
an electronic hydrometer.


This project is under active development.


## Design

The iSpindel is configured to send metrics using the generic HTTP POST.
 
When the iSpindel wake up (like every 2 minutes) it submits a POST request containing the metrics to this BrewBlox service.

The service will then send an event so the history service can persist the metrics.



## Limitations

- The security is not handled so far
