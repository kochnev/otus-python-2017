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
import json
from collections import defaultdict
from datetime import datetime
from statistics import median

config = {
    "REPORT_SIZE": 500,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

logFileInfo = tuple()

def create_report_html(report_data, log_day):
    report_name = 'report_' + str(log_day) +'.html'
    report_dir = config["REPORT_DIR"]

    with open('report.html', 'r', encoding='utf-8') as template:
        template_data = template.read()
    
    json_data = json.dumps(report_data)


    ready_data = template_data.replace('$table_json', json_data)
    with open(os.path.join(report_dir,  report_name), 'w', encoding='utf-8') as html_report:
        html_report.write(ready_data)

def get_report_data(parsed_lines):
    all_count = 0
    all_time = 0
    report_size = config["REPORT_SIZE"]

    grouped_urls = defaultdict(list)
    for url, r_time in parsed_lines:
        grouped_urls[url].append(r_time)
        all_time += float(r_time)
        all_count += 1

    table = []
    for url, time_col in grouped_urls.items():
        times_float= [float(x) for x in time_col]
        time_sum = sum(times_float)
        if time_sum>report_size:
            count = len(time_col)
            count_p = (count/all_count)*100
            time_avg = time_sum/count
            time_max = max(times_float)
            time_med = median(times_float)
            time_perc = (time_sum/all_count)*1
            
            row = { 
                "url": url,
                "count": count,
                "count_perc": round(count_p, 3),
                "time_avg": round(time_avg, 3),
                "time_max": round(time_max, 3),
                "time_med": round(time_med, 3),
                "time_perc": round(time_perc, 3),
                "time_sum": round(time_sum, 3)
            }
            
            table.append(row)

    return sorted(table, key=lambda k: k['time_sum'], reverse=True)


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
        log = gzip.open(log_path,'rt')
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
    latest_logfile = max(logfiles, key=lambda item:item[1])
    latest_logfile_name = latest_logfile[1]
    latest_log_day = latest_logfile[0]
    lines = read_log(latest_logfile_name)
    parsed_lines = parse_log(lines)
    
    report_data = get_report_data(parsed_lines)
    
    create_report_html(report_data, latest_log_day)  

if __name__ == "__main__":
    main()
