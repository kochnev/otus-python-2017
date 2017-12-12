# Log Analyzer

This log analyzer works by this way:
1. Search for the latest log file in the folder with log files.
2. Parsing the latest log file.
3. Creating statistic using urls and time requests.

According nginx log format (http://nginx.org/en/docs/http/ngx_http_log_module.html#log_format) the structure of log file is:
* '$remote_addr 
* $remote_user 
* $http_x_real_ip [$time_local] "
* $request" '
* '$status $body_bytes_sent "
* $http_referer" '
* '"$http_user_agent" 
* "$http_x_forwarded_for" 
* "$http_X_REQUEST_ID" 
* "$http_X_RB_USER" '
* '$request_time';

## Getting Started

To run test, please type: python3 test_log_analyzer.py
To generate report with statstic, please type: python log_analyzer.py

Optional parameters:
--config path_to_config_file  Exmaple of config file you can find in log_analyzer.conf

## Prerequisites

Python version 3.6 and above

## Installing

No special installation procedure is required. 

## License

This project is licensed under the MIT License
