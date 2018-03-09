MemcLoad
=====================

The script memc_load.py parses lines from files with logs and upload result in memcache.

## Description ##
* multiprocessing is used to create pool of process
* threading is used to create thread per memcache server connection
* queue is used to communicate between threads.

## How to run ##

python memc_load.py --pattern={root_path}/data/*.tsv.gz 

## Testing ##

python test.py

## Prerequisites

Python version 2.7.

## Installing

No special installation procedure is required. 

## License

This project is licensed under the MIT License
