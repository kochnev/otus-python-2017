#!/usr/bin/env python
# -*- coding: utf-8 -*-


# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_USER" '
#                     '$request_time';

import os
import fnmatch
import gzip
import re
from collections import defaultdict
from datetime import datetime

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

logFileInfo = tuple()


def get_report(parsed_lines):
    grouped_urls = defaultdict(list)
    for url, r_time in parsed_lines:
        grouped_urls[url].append(r_time)

    return grouped_urls



def parse_log(lines):
    for line in lines:
        try:
            chunks = line.split()
            url = chunks[6]
            r_time = chunks[-1]
            yield url, r_time
        except:
            pass


def read_log(log_path):
    if log_path.endswith(".gz"):
        log = gzip.open(log_path,'r')
    else:
        log = open(log_path)

    for line in log:
        yield line

    log.close()


def get_logfiles(filepat, top):
    for path, dirlist, filelist in os.walk(top):
        for name in fnmatch.filter(filelist,filepat):
            logfile = os.path.join(path, name)
            match = re.search('nginx-access-ui.log-(\d{4}\d{2}\d{2})\.?', name)
            day = day_of_log = datetime.strptime(match.group(1),'%Y%m%d').date() 
            yield (day,logfile)


def main():
    logfiles = get_logfiles("nginx-access-ui.log-*.gz", config["LOG_DIR"])
    latest_logfile = max(logfiles, key=lambda item:item[1])[1]
    lines = read_log(latest_logfile)
    parsed_lines = parse_log(lines)
    
    report = get_report(parsed_lines)

    for url, times in report.items():
        print url 
        print times
        break
        
if __name__ == "__main__":
    main()
