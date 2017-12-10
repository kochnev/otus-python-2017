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
import time
import logging
from collections import defaultdict
from datetime import datetime as dt
from statistics import median


config = {
    "REPORT_SIZE": 500,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TS_DIR": "./ts",
    "LOGGING": "ExecutionLog"
}

logFileInfo = tuple()

def create_report_html(report_data, report_file_path):
    """function to save report in html"""
    try:
        with open('report.html', 'r', encoding='utf-8') as template:
            template_data = template.read()
    except:
        logging.error("An error occured while opening report.html")
        raise
    
    json_data = json.dumps(report_data)


    ready_data = template_data.replace('$table_json', json_data)
    try:
        with open(report_file_path, 'w', encoding='utf-8') as html_report:
            html_report.write(ready_data)
    except:
        logging.error("An error occured while opening {0}".format(report_file_path))
        raise


def get_report_data(parsed_lines):
    """function to get report data in json format"""
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
    """generator to get tuples(logdate,logpath) by splitting lines"""
    for line in lines:
        try:
            chunks = line.split()
            url = chunks[6]
            r_time = chunks[-1]
            yield url, r_time
        except:
            pass


def read_log(log_path):
    """generator for reading lines of logfile"""
    if log_path.endswith(".gz"):
        log = gzip.open(log_path,'rt')
    else:
        log = open(log_path)

    for line in log:
        yield line

    log.close()


def get_logfiles(filepat, top):
    """generator for getting logfiles"""
    for path, dirlist, filelist in os.walk(top):
        for name in fnmatch.filter(filelist,filepat):
            logfile = os.path.join(path, name)
            match = re.search('nginx-access-ui.log-(\d{4}\d{2}\d{2})\.?', name)
            day = day_of_log = dt.strptime(match.group(1),'%Y%m%d').date() 
            yield (day,logfile)

def update_ts():
    """Update timestamp of the last report"""
    ts = time.time()
    ts_str = dt.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    ts_dir = config["TS_DIR"]
    file_path = os.path.join(ts_dir, "log_analyzer.ts")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ts_str)
    except:
        logging.error("An error occured while opening {0}".format(report_file_path))
        raise
   
    os.utime(file_path,(int(ts),int(ts)))


def main():
    logging.info("search for logfiles")
    logfiles = get_logfiles("nginx-access-ui.log-*.gz", config["LOG_DIR"])
    
    logging.info("get the latest logfile") 
    latest_logfile = max(logfiles, key=lambda item:item[1])
    
    logging.info("get the attributes of the latest logfile")
    latest_logfile_name = latest_logfile[1]
    latest_log_day = latest_logfile[0]
    logging.info("the latest log file is {0}".format(latest_logfile_name))

    report_name = "report_{0}.html".format(latest_log_day)
    report_dir = config["REPORT_DIR"]
    report_file_path = os.path.join(report_dir,report_name)
    logging.info("the report name is {0}".format(report_file_path))

    if os.path.exists(report_file_path):
        logging.error("Отчет за дату  {0} уже существует".format(latest_log_day))
        return

  
    logging.info("read lines from the log file")
    lines = read_log(latest_logfile_name)
    
    logging.info("get parsed lines")
    parsed_lines = parse_log(lines)
    
    logging.info("get report data")
    report_data = get_report_data(parsed_lines)
    
    logging.info("generate html report")
    create_report_html(report_data, report_file_path) 
    
    logging.info("update timestamp")
    update_ts()


    
if __name__ == "__main__":
    logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname).1s %(message)s',
            datefmt='%Y.%m.%d %H:%M:%S',
            filename=None
        )
        
    logging.info("======start=======")
       
    main()
       
    logging.info("=====end=====")

