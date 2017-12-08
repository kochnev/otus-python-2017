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
from datetime import datetime

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

logFileInfo = tuple()


def gen_find(filepat, top):
    for path, dirlist, filelist in os.walk(top):
        for name in fnmatch.filter(filelist,filepat):
            logfile = os.path.join(path, name)
            match = re.search('nginx-access-ui.log-(\d{4}\d{2}\d{2})\.?', name)
            day = day_of_log = datetime.strptime(match.group(1),'%Y%m%d').date() 
            yield (day,logfile)


def main():
    logfiles = gen_find("nginx-access-ui.log-*.gz", config["LOG_DIR"])
    print max(logfiles, key=lambda item:item[1])

if __name__ == "__main__":
    main()
