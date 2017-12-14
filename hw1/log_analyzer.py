#!/usr/bin/env python3
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
import argparse
from collections import defaultdict, namedtuple
from datetime import datetime as dt
from statistics import median



primary_config = {
    "REPORT_SIZE": 500,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TS_DIR": "./ts",
    "THRESHOLD_ERR": 0.3
}

config_path = '/usr/local/etc/log_analyzer.conf'

LogInfo = namedtuple('LogInfo', 'date, path')


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


def get_report_data(config, parsed_lines):
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
        times_float = [float(x) for x in time_col]
        time_sum = sum(times_float)
        if time_sum > report_size:
            count = len(time_col)
            count_p = (count / all_count) * 100
            time_avg = time_sum / count
            time_max = max(times_float)
            time_med = median(times_float)
            time_perc = (time_sum / all_count) * 1

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


def parse_log(config, lines):
    """generator to get tuples(logdate,logpath) by splitting lines"""
    threshold_err = config["THRESHOLD_ERR"]
    total = error = 0
    for line in lines:
        total+=1
        try:
            chunks = line.split()
            url = chunks[6]
            r_time = chunks[-1]
            yield url, r_time
        except:
            error+=1
    
    rate = error/float(total)

    if rate > threshold_err:
        logging.error("Percent of lines parsed with errors exceed the threshold")
        sys.exit()

def read_log(log_path):
    """generator for reading lines of logfile"""
    if log_path.endswith(".gz"):
        log = gzip.open(log_path, 'rt')
    else:
        log = open(log_path)

    for line in log:
        yield line

    log.close()


def get_logfiles(log_folder):
    """generator for getting logfiles"""
    patc = re.compile('^nginx-access-ui.log-(\d{8})(\.gz)?$')
    log_files = os.listdir(log_folder)
    for name in log_files:
        match = patc.search(name)
        if match:
            path = os.path.join(log_folder, name)
            date = dt.strptime(match.group(1), '%Y%m%d').date()
            yield LogInfo(date, path)


def update_ts(config):
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

    os.utime(file_path, (int(ts), int(ts)))


def get_config_dict(path_to_config):
    try:
        with open(path_to_config, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error("please, check your config file")
        raise Exception("please, check your config file")


def check_config(config):
    try:
        report_size = int(config["REPORT_SIZE"]),
        report_dir = config["REPORT_DIR"],
        log_dir = config["LOG_DIR"],
        ts_dir = config["TS_DIR"],
    except:
        logging.error("please, check your config file")
        raise Exception("please, check your config file")


def main(config):
    logging.info("search for logfiles")
    
    log_folder = config["LOG_DIR"]
    if not os.path.exists(log_folder):
        logging.error("Folder {} does not exist!".format(log_folder))
        return 

    logfiles = get_logfiles(log_folder)

    logging.info("get the latest logfile")
    latest_logfile = max(logfiles, key=lambda log: log.date)

    logging.info("get the attributes of the latest logfile")
    latest_logfile_name = latest_logfile[1]
    latest_log_day = latest_logfile[0]
    logging.info("the latest log file is {0}".format(latest_logfile_name))

    report_name = "report_{0}.html".format(latest_log_day)
    report_dir = config["REPORT_DIR"]
    report_file_path = os.path.join(report_dir, report_name)
    logging.info("report name is {0}".format(report_file_path))

    if os.path.exists(report_file_path):
        logging.info("Report for date  {0} already exists".format(latest_log_day))
        return

    logging.info("read lines from the log file")
    lines = read_log(latest_logfile_name)

    logging.info("get parsed lines")
    parsed_lines = parse_log(config, lines)

    logging.info("get report data")
    report_data = get_report_data(config, parsed_lines)

    logging.info("generating html report...")
    create_report_html(report_data, report_file_path)
    logging.info("report html has created successfully!")
    update_ts(config)
    logging.info("timestamp has updated")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        "-c",
        type=str,
        help="Path for configuration file.",
        default=config_path
    )

    args = parser.parse_args()
    arg_config = get_config_dict(args.config)
    
    primary_config.update(arg_config)

    check_config(primary_config)
    print(primary_config.get("LOGGING","none"))
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname).1s %(message)s',
        datefmt='%Y.%m.%d %H:%M:%S',
        filename=primary_config.get("LOGGING")
    )

    logging.info("======start=======")

    try:
        main(primary_config)
    except Exception as e:
        logging.exception(e)

    logging.info("=====end=====")
