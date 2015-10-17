## Installation

    pip install -r requirements.txt

## The "service":

Run with:

    twistd -y service.py --pidfile service.pid --logfile service.log

Stop with:

    kill $(cat service.pid)

Logs are in ```service.log```

It will start daemon on port 8080 and export two resources:

    http://127.0.0.1:8080/service/method
    http://127.0.0.1:8080/callback.service/method

Any arguments to `service/method` will be forwarded to corresponding backend service (see `The "backend"`).
Backend method URL is hardcoded to be:

    http://localhost:8081/backend-service/method

## The "backend":

Run with:

    twistd -y backend.py --pidfile backend.pid --logfile backend.log

Stop with:

    kill $(cat backend.pid)

Logs are in `backend.log`

It will start a daemon on port 8081 in foreground and export one resource:

    http://127.0.0.1:8081/backend-service/method?delay=5

"delay" is optional, specifies number of seconds until backend will do a POST to callback url.
Callback url is hardcoded to be:

    http://localhost:8080/callback.service/method

Backend will continue POST'ing there until it will succeed (with 10 seconds delay between tries)

## Sample requests

###### Success

    http://127.0.0.1:8080/service/method

Will immediately produce correct output, i.e:

    HTTP/1.1 200 OK
    {"timestamp": "2015-10-17T19:31:37.889072", "response": "dummy data for request f4403754-c6cc-41ba-a8ed-aebaf7fc515d"}

###### Timeout or backend unavailable

    http://127.0.0.1:8080/service/method?delay=10

Any delay bigger than 5 (hardcoded TIMEOUT value) would result in:

    HTTP/1.1 503 Service Unavailable
    Response took longer than 5 sec, cancelled. Please try again later.

If backend is not running or unreachable, then any requests would produce something like:

    HTTP/1.1 503 Service Unavailable
    Backend failed with: Connection was refused by other side: 61: Connection refused.

###### Error

    http://127.0.0.1:8080/service/method?delay=xyz

Specifying non-integer value for delay would make backend fail:

    HTTP/1.1 502 Bad Gateway
    Backend failed with: Delay is not a number

## Performance

On my MacBook Pro, its something around 320 requests per second with 50 threads concurrency.
Transport turnaround time ranges from 50 to 500 ms.

Memory usage never exceeds 25 mb per process.

    $ ab -c 50 -t 15 http://127.0.0.1:8080/service/method?delay=0
    This is ApacheBench, Version 2.3 <$Revision: 1663405 $>
    Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
    Licensed to The Apache Software Foundation, http://www.apache.org/

    Benchmarking 127.0.0.1 (be patient)
    Finished 4871 requests


    Server Software:        TwistedWeb/15.4.0
    Server Hostname:        127.0.0.1
    Server Port:            8080

    Document Path:          /service/method?delay=0
    Document Length:        118 bytes

    Concurrency Level:      50
    Time taken for tests:   15.017 seconds
    Complete requests:      4871
    Failed requests:        0
    Total transferred:      1100846 bytes
    HTML transferred:       574778 bytes
    Requests per second:    324.37 [#/sec] (mean)
    Time per request:       154.147 [ms] (mean)
    Time per request:       3.083 [ms] (mean, across all concurrent requests)
    Transfer rate:          71.59 [Kbytes/sec] received

    Connection Times (ms)
                  min  mean[+/-sd] median   max
    Connect:        0    0   0.3      0       2
    Processing:    35  153  49.8    164     549
    Waiting:       35  153  49.6    164     549
    Total:         35  154  49.9    164     549

    Percentage of the requests served within a certain time (ms)
      50%    164
      66%    171
      75%    175
      80%    177
      90%    183
      95%    189
      98%    199
      99%    438
     100%    549 (longest request)
