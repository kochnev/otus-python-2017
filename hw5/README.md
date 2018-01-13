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


## Result of ab test ##
```
Server Software:        HTTPServer/0.1
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        612 bytes

Concurrency Level:      100
Time taken for tests:   184.631 seconds
Complete requests:      50000
Failed requests:        55
   (Connect: 0, Receive: 0, Length: 55, Exceptions: 0)
Total transferred:      38457650 bytes
HTML transferred:       30566340 bytes
Requests per second:    270.81 [#/sec] (mean)
Time per request:       369.263 [ms] (mean)
Time per request:       3.693 [ms] (mean, across all concurrent requests)
Transfer rate:          203.41 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    2 196.8      0   22571
Processing:     4  314 3773.9     30  109882
Waiting:        0  196 1338.9     29   64928
Total:          5  316 3779.5     30  109882

Percentage of the requests served within a certain time (ms)
  50%     30
  66%     33
  75%     35
  80%     37
  90%     51
  95%   1064
  98%   1733
  99%   3362
 100%  109882 (longest request)
```
