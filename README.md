tcp-bottle
==========

Simple tcpdump web interface for traffic monitoring.

Runs out of the box:

```tcpdump -i eth0 -qtvn > python server.py```

Then point your browser at ```http://localhost:8002``` or whatever host you started the script on.


Dependencies
------------

Python 2.7 with
* bottle.py >= 0.11
* apscheduler

tcpdump
libpcap

Configuration
-------------

The last line contains interface and port. You may want to change this or uncomment the line when importing server.py as module:
```run(host='0.0.0.0', port=8002)```

Changing ```DEBUG = False``` to ```DEBUG = True``` causes random data to be generated instead of reading from stdin. (That's the only way to run this script on Windows)
