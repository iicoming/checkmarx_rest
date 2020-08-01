# -*- encoding: utf-8 -*-
"""
@File    : __init_.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""
import getopt
import sys

from checkmarx.CheckmarxRedis import CheckmarxRedis
from checkmarx.CheckmarxReport import CheckmarxReport
from checkmarx.CheckmarxScan import CheckmarxScan


def main(argv):
    action = ''

    try:
        opts, args = getopt.getopt(argv, "ha:", ["action="])
    except getopt.GetoptError:
        print('main.py -a <action> scan|report|redis')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('main.py -a <action> scan|report|redis')
            sys.exit()
        elif opt in ("-a", "--action"):
            action = arg

    if not action:
        print('main.py -a <action> scan|report|redis')
        sys.exit()

    if action == 'scan':
        checkmarx = CheckmarxScan()
        checkmarx.start_scan()
    elif action == 'report':
        checkmarx = CheckmarxReport()
        checkmarx.create_report()
    elif action == 'redis':
        checkmarx = CheckmarxRedis()
        checkmarx.import_redis()


if __name__ == '__main__':
    main(sys.argv[1:])
