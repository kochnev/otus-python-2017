Simple HTTP web server
=====================

Implementation of Simple HTTP Web server. Multithreading architecture was used. Python3.6.

## Description ##

* Respond to `GET` with status code in `{200,404}`
* Respond to `HEAD` with status code in `{200,404}`
* Respond to all other request methods with status code `405`
* Directory index file name `index.html`
* Respond to requests for `/<file>.html` with the contents of `DOCUMENT_ROOT/<file>.html`
* Requests for `/<directory>/` should be interpreted as requests for `DOCUMENT_ROOT/<directory>/index.html`
* Respond with the following header fields for all requests:
  * `Server`
  * `Date`
  * `Connection`
* Respond with the following additional header fields for all `200` responses to `GET` and `HEAD` requests:
  * `Content-Length`
  * `Content-Type`
* Respond with correct `Content-Type` for `.html, .css, js, jpg, .jpeg, .png, .gif, .swf`
* Respond to percent-encoding URLs

## Testing ##

* `httptest` folder from `http-test-suite` repository should be copied into `DOCUMENT_ROOT`
* Your HTTP server should listen `localhost:80`
* `http://localhost/httptest/wikipedia_russia.html` must been shown correctly in browser
* Lowest-latency response (tested using `ab`, ApacheBench) in the following fashion: `ab -n 50000 -c 100 -r http://localhost:8080/`

## Prerequisites

Python version 3.6.

## Installing

No special installation procedure is required. 

## License

This project is licensed under the MIT License

## Result of ab test ##
For testing in docker container at first you should:
1. Create an image:
   `docker build -t httpserver `
2. Create and run conatainer:
   `docker run -it -v [full path to direcotry with httpd.py]:/app -p 8080:80 httpserver /bin/sh`
3. Run the server:
   python httpd.py [options]
4. Run command from host os: `ab -n 50000 -c 100 -r http://localhost:8080/`
   If your host OS is Mac OS then you should run ab in docker container, for example https://hub.docker.com/r/jordi/ab/
   `docker run --rm jordi/ab ab -n 50000 -c 100 -r http://172.17.0.1:8080/`

```
Server Software:        HTTPServer/0.1
Server Hostname:        172.17.0.1
Server Port:            8080

Document Path:          /
Document Length:        612 bytes

Concurrency Level:      100
Time taken for tests:   162.639 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      38500000 bytes
HTML transferred:       30600000 bytes
Requests per second:    307.43 [#/sec] (mean)
Time per request:       325.279 [ms] (mean)
Time per request:       3.253 [ms] (mean, across all concurrent requests)
Transfer rate:          231.17 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.4      0      14
Processing:    73  325  96.9    315    1464
Waiting:       73  324  96.8    314    1464
Total:         81  325  96.9    315    1464

Percentage of the requests served within a certain time (ms)
  50%    315
  66%    329
  75%    338
  80%    344
  90%    362
  95%    380
  98%    407
  99%    446
 100%   1464 (longest request)
```
