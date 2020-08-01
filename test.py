# -*- encoding: utf-8 -*-
"""
@File    : __init_.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""

from checkmarx.CheckmarxScan import CheckmarxScan

checkmarx = CheckmarxScan()
checkmarx.start_scan_test("git@github.com:iicoming/oxpecker.git", "branch")
