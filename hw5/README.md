Simple HTTP web server
=====================

Implement a Web server. Multithreading architecture was used.

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
  Name                | Value
----------------------|-----------------
  Server Software:    |    HTTPServer/0.1
 Server Hostname:    |    localhost
 Server Port:        |    8080

 Document Path:      |   /
 Document Length:    |    612 bytes

 Concurrency Level:  |    100
 Time taken for tests:|   138.085 seconds
 Complete requests:   |  50000
 Failed requests:     |   34

(Connect: 0, Receive: 0, Length: 34, Exceptions: 0)
                      |
 ---------------------|---------------------------
 Total transferred:   |  38473820 bytes
 HTML transferred:    |   30579192 bytes
 Requests per second: |   362.09 [#/sec] (mean)
 Time per request:    |   276.171 [ms] (mean)
 Time per request:    |   2.762 [ms] (mean, across all concurrent requests)
 Transfer rate:       |   272.09 [Kbytes/sec] received

 Connection Times (ms)
 
           |    min | mean[+/-sd]| median |  max|
 ----------|--------|------------|--------|-----|
 Connect:   |     0  | 10 407.8    |  0   |41243
 Processing: |    2  | 234 3051.9   |  34  |110021
 Waiting:    |    0  | 159 1057.0    | 33  | 54323
 Total:      |    2  | 244 3082.5   |  34  |110026

Percentage of the requests served within a certain time (ms)
       |
  -----|-----
  50%  |   34
  66%  |   38
  75%  |   42
  80%  |   44
  90%  |   68
  95%  | 1062
  98%  | 1284
  99%  | 3137
  100% | 110026 (longest request)
