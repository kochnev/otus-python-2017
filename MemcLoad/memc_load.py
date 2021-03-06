#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import gzip
import sys
import glob
import logging
import collections
from optparse import OptionParser
# brew install protobuf
# protoc  --python_out=. ./appsinstalled.proto
# pip install protobuf
import appsinstalled_pb2
# pip install python-memcached
import memcache
import multiprocessing as mp
import Queue
import time
import threading

SENTINEL = object()
WORKERS_NUM = 3
NORMAL_ERR_RATE = 0.01
AppsInstalled = collections.namedtuple("AppsInstalled", ["dev_type", "dev_id", "lat", "lon", "apps"])


class MemcacheClient(threading.Thread):
    def __init__(self, memc_addr, line_queue, result_queue, dry_run):
        threading.Thread.__init__(self)
        self.daemon = True
        self.memc_addr = memc_addr
        self.line_queue = line_queue
        self.result_queue = result_queue
        self.dry_run = dry_run
        self.processed = 0
        self.errors = 0

    def run(self):
        client = memcache.Client([self.memc_addr], socket_timeout=1)
        while True:
            try:
                key_packed = self.line_queue.get()
                if key_packed == SENTINEL:
                    self.result_queue.put((self.processed, self.errors))
                    break
                else:
                    self.processed += 1
                    ok = insert_appsinstalled(client, key_packed, self.dry_run)
                    if not ok:
                        self.errors += 1
            except Queue.Empty:
                continue


def dot_rename(path):
    head, fn = os.path.split(path)
    # atomic in most cases
    print(os.path.join(head, "." + fn))
    print(path)
    os.rename(path, os.path.join(head, "." + fn))


def insert_appsinstalled(memc, key_packed, dry_run=False):
    key, packed = key_packed
    current = 1
    allowed = 3
    timeout = 0.3
    try:
        if dry_run:
            logging.debug("%s - %s -> %s" % (memc.servers[0], key, packed))
        else:
            res = memc.set(key, packed)
            while res == 0 and (current < allowed):
                time.sleep(timeout)
                current += 1
                res = memc.set(key, packed)
            return bool(res)
    except Exception as e:
        logging.exception("Cannot write to memc %s: %s" % (memc.servers[0], e))
        return False
    return True


def parse_appsinstalled(line):
    line_parts = line.strip().split("\t")
    if len(line_parts) < 5:
        return
    dev_type, dev_id, lat, lon, raw_apps = line_parts
    if not dev_type or not dev_id:
        return
    try:
        apps = [int(a.strip()) for a in raw_apps.split(",")]
    except ValueError:
        apps = [int(a.strip()) for a in raw_apps.split(",") if a.isidigit()]
        logging.info("Not all user apps are digits: `%s`" % line)
    try:
        lat, lon = float(lat), float(lon)
    except ValueError:
        logging.info("Invalid geo coords: `%s`" % line)
    return AppsInstalled(dev_type, dev_id, lat, lon, apps)


def serialize_appsinstalled(appsinstalled):
    ua = appsinstalled_pb2.UserApps()
    ua.lat = appsinstalled.lat
    ua.lon = appsinstalled.lon
    key = "%s:%s" % (appsinstalled.dev_type, appsinstalled.dev_id)
    ua.apps.extend(appsinstalled.apps)
    packed = ua.SerializeToString()
    return (key, packed)


def process_file(opt):
    fn, device_memc, dry = opt
    result_queue = Queue.Queue()
    threads = []
    queue_dict = {}

    for dev_type, addr in device_memc.items():
        queue_dict[dev_type] = Queue.Queue()
        thread = MemcacheClient(queue_dict[dev_type], result_queue, addr, dry)
        threads.append(thread)

    for thread in threads:
        thread.start()

    processed = errors = 0
    logging.info('Pr.Name: %s. Processing %s' % (mp.current_process().name, fn))
    fd = gzip.open(fn)
    for line in fd:
        processed += 1
        logging.info('Pr. Name: %s. Processing %s' %
                     (mp.current_process().name, line))
        line = line.strip()
        if not line:
            errors += 1
            continue
        appsinstalled = parse_appsinstalled(line)
        dev_type = appsinstalled.dev_type
        if not appsinstalled:
            errors += 1
            continue
        if dev_type not in device_memc:
            errors += 1
            logging.error("Pr. Name: %s. Unknow device type: %s"
                          % (mp.current_process().name, dev_type))
            continue
        key_packed = serialize_appsinstalled(appsinstalled)
        queue_dict[dev_type].put(key_packed)

    for dev_type in device_memc:
        queue_dict[dev_type].put(SENTINEL)

    for thread in threads:
        thread.join()

    while not result_queue.empty():
        thread_processed, thread_errors = result_queue.get()
        processed += thread_processed
        errors += thread_errors

    if processed:
        err_rate = float(errors) / processed
        if err_rate < NORMAL_ERR_RATE:
            logging.info("Prn: %s. Fn: %s. Acceptable error rate (%s). \
                     Successfull load" % (mp.current_process().name, fn, err_rate))
        else:
            logging.error("Process name: %s. File name: %s. \
                          High error rate (%s> %s). \
                          Failed load" % (mp.current_process().name,
                          fn, err_rate, NORMAL_ERR_RATE))
    fd.close()
    return fn


def main(options):
    device_memc = {
        "idfa": options.idfa,
        "gaid": options.gaid,
        "adid": options.adid,
        "dvid": options.dvid,
    }
    pool = mp.Pool(WORKERS_NUM)
    func_args = []
    for fn in glob.iglob(options.pattern):
        func_args.append((fn, device_memc, options.dry))
    func_args.sort(key=lambda x: x[0])
    for fn in pool.imap(process_file, func_args):
        dot_rename(fn)


def prototest():
    sample = "idfa\t1rfw452y52g2gq4g\t55.55\t42.42\t1423,43,567,3,7,23\ngaid\t7rfw452y52g2gq4g\t55.55\t42.42\t7423,424"
    for line in sample.splitlines():
        dev_type, dev_id, lat, lon, raw_apps = line.strip().split("\t")
        apps = [int(a) for a in raw_apps.split(",") if a.isdigit()]
        lat, lon = float(lat), float(lon)
        ua = appsinstalled_pb2.UserApps()
        ua.lat = lat
        ua.lon = lon
        ua.apps.extend(apps)
        packed = ua.SerializeToString()
        unpacked = appsinstalled_pb2.UserApps()
        unpacked.ParseFromString(packed)
        assert ua == unpacked


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-t", "--test", action="store_true", default=False)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("--dry", action="store_true", default=False)
    op.add_option("--pattern", action="store", default="/data/appsinstalled/*.tsv.gz")
    op.add_option("--idfa", action="store", default="127.0.0.1:33013")
    op.add_option("--gaid", action="store", default="127.0.0.1:33014")
    op.add_option("--adid", action="store", default="127.0.0.1:33015")
    op.add_option("--dvid", action="store", default="127.0.0.1:33016")
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO if not opts.dry else logging.DEBUG,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    if opts.test:
        prototest()
        sys.exit(0)

    logging.info("Memc loader started with options: %s" % opts)
    try:
        main(opts)
    except Exception as e:
        logging.exception("Unexpected error: %s" % e)
        sys.exit(1)
