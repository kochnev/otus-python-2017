#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# log_format ui_short
#     '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#     '$status $body_bytes_sent "$http_referer" '
#     '"$http_user_agent" "$http_x_forwarded_for"'
#     '"$http_X_REQUEST_ID" "$http_X_USER" '
#     '$request_time';

import os
import gzip
import re
import json
import time
import logging
import argparse
import shutil
from collections import defaultdict, namedtuple
from datetime import datetime as dt
from statistics import median

primary_config = {
    "REPORT_SIZE": 100,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TS_DIR": "./ts",
    "THRESHOLD_ERR": 0.3
}

config_path = '/usr/local/etc/log_analyzer.conf'

LogInfo = namedtuple('LogInfo', 'date, path')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JS_NAME = 'jquery.tablesorter.min.js'


def create_report_html(report_data, report_dir, report_name):
    """function to save report in html"""
    try:
        with open('report.html', 'r', encoding='utf-8') as template:
            template_data = template.read()
    except Exception:
        logging.error("An error occured while opening report.html")
        raise

    json_data = json.dumps(report_data)

    ready_data = template_data.replace('$table_json', json_data)

    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    if not os.path.exists(os.path.join(report_dir, JS_NAME)):
        shutil.copy(os.path.join(BASE_DIR, JS_NAME), report_dir)

    report_path = os.path.join(report_dir, report_name)
    try:
        with open(report_path, 'w', encoding='utf-8') as html_report:
            html_report.write(ready_data)
    except Exception:
        logging.error("An error occured while opening {0}".
                      format(report_path))
        raise


def get_report_data(config, parsed_lines):
    """function to get report data in json format"""
    all_count = 0
    all_time = 0
    report_size = config["REPORT_SIZE"]

    grouped_urls = defaultdict(list)
    for url, r_time in parsed_lines:
        grouped_urls[url].append(r_time)
        all_time += r_time
        all_count += 1
    table = []
    for url, time_col in grouped_urls.items():
        time_sum = sum(time_col)
        count = len(time_col)
        time_avg = time_sum / count
        count_p = (count / all_count) * 100
        time_max = max(time_col)
        time_med = median(time_col)
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

    sorted_table = sorted(table, key=lambda k: k['time_sum'], reverse=True)

    return sorted_table[:report_size]


def parse_log(config, lines):
    """generator to get tuples(logdate,logpath) by splitting lines"""
    threshold_err = config["THRESHOLD_ERR"]
    total = error = 0
    pat = '.+"(GET|POST)\s(?P<url>\S+)\sHTTP.+(?P<t_request>\d+\.\d+)$'
    patc = re.compile(pat)

    for line in lines:
        total += 1
        try:
            m = patc.search(line)
            if not m:
                raise Exception
            url = m.group('url')
            r_time = float(m.group('t_request'))
            yield url, r_time
        except Exception:
            error += 1

    ftotal = float(total)
    rate = error/ftotal
    if rate > threshold_err:
        logging.error("Percent of lines parsed \
                            with errors exceed the threshold")
        raise Exception


def read_log(log_path):
    """generator for reading lines of logfile"""
    if log_path.endswith(".gz"):
        log = gzip.open(log_path, 'rt')
    else:
        log = open(log_path)

    for line in log:
        yield line

    log.close()


def get_latest_logfiles(log_folder):
    """generator for getting logfiles"""
    patc = re.compile('^nginx-access-ui.log-(\d{8})(\.gz)?$')
    log_files = os.listdir(log_folder)
    filtered = []
    for name in log_files:
        match = patc.search(name)
        if match:
            path = os.path.join(log_folder, name)
            date = dt.strptime(match.group(1), '%Y%m%d').date()
            filtered.append(LogInfo(date, path))

    if not filtered:
        msg = "There are not logfiles in {0}".format(log_folder)
        logging.error(msg)
        raise Exception(msg)

    return max(filtered, key=lambda log: log.date)


def update_ts(config):
    """Update timestamp of the last report"""
    ts = time.time()
    ts_str = dt.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    ts_dir = config["TS_DIR"]
    file_path = os.path.join(ts_dir, "log_analyzer.ts")

    if not os.path.exists(ts_dir):
        os.makedirs(ts_dir)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(ts_str)
    except Exception:
        logging.error("An error occured while opening {0}"
                      .format(file_path))
        raise

    os.utime(file_path, (int(ts), int(ts)))


def get_config_dict(path_to_config):
    try:
        with open(path_to_config, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error("please, check your config file")
        raise Exception("please, check your config file")


def main(config):
    logging.info("search for logfiles")
    log_folder = config["LOG_DIR"]
    if not os.path.exists(log_folder):
        logging.error("Folder {0} does not exist!".format(log_folder))

    logging.info("get the latest logfile")
    latest_logfile = get_latest_logfiles(log_folder)

    logging.info("the latest log file is {0}".format(latest_logfile.path))
    report_name = "report_{0}.html".format(latest_logfile.date)
    report_dir = config["REPORT_DIR"]
    report_path = os.path.join(report_dir, report_name)

    logging.info("report name is {0}".format(report_path))

    if os.path.exists(report_path):
        logging.info("Report for date  {0} already exists"
                     .format(latest_logfile.date))
        update_ts(config)
        return

    logging.info("read lines from the log file")
    lines = read_log(latest_logfile.path)

    logging.info("get parsed lines")
    parsed_lines = parse_log(config, lines)

    logging.info("get report data")
    report_data = get_report_data(config, parsed_lines)

    logging.info("generating html report...")
    create_report_html(report_data, report_dir, report_name)
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
