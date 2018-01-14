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
```
erver Software:        HTTPServer/0.1
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        612 bytes

Concurrency Level:      100
Time taken for tests:   199.180 seconds
Complete requests:      50000
Failed requests:        0
Total transferred:      38500000 bytes
HTML transferred:       30600000 bytes
Requests per second:    251.03 [#/sec] (mean)
Time per request:       398.359 [ms] (mean)
Time per request:       3.984 [ms] (mean, across all concurrent requests)
Transfer rate:          188.76 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.4      0      64
Processing:    52  397 484.6    306   64937
Waiting:       51  396 484.5    306   64937
Total:         58  397 484.6    307   64937

Percentage of the requests served within a certain time (ms)
  50%    307
  66%    326
  75%    340
  80%    351
  90%    418
  95%   1313
  98%   1398
  99%   1563
 100%  64937 (longest request)
```
