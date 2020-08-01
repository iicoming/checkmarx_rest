# -*- encoding: utf-8 -*-
"""
@File    : CheckmarxReport.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""
import json

import requests

from checkmarx.CheckmarxBase import CheckmarxBase


class CheckmarxReport(CheckmarxBase):
    def __init__(self):
        super().__init__()

    @CheckmarxBase.catch_exception
    def create_report(self):
        checkmarx_scan_status = self.checkmarx_base_url + \
                                '/reports/sastScan/{reportid}/status'
        total = self.client.llen('create_report')
        for item in range(total):
            create_report = self.client.rpop('create_report')
            data = json.loads(create_report)
            projectid = data.get('ProjectID')
            runid = str(data.get('RunId'))
            url = checkmarx_scan_status.format(reportid=runid)
            r = requests.get(url, headers=self.checkmarx_headers)
            status = r.json()
            if r.status_code == 200:
                if status.get('stage') and status.get(
                        "stage").get('value') == "Failed":
                    continue
                if status.get("stage") and status.get(
                        "stage").get('value') == "Finished":
                    reportId = self._get_report_id(
                        runid, self.checkmarx_headers)
                    data['reportId'] = reportId
                    self.client.lpush('import_redis', json.dumps(data))
                    continue
            elif r.status_code == 404:
                flag = self._get_last_finished(
                    projectid, runid, self.checkmarx_headers)
                if not flag:
                    self.client.lpush('create_report', create_report)
                    continue
                else:
                    reportId = self._get_report_id(
                        runid, self.checkmarx_headers)
                    data['reportId'] = reportId
                    self.client.lpush('import_redis', json.dumps(data))
                    continue
            else:
                raise Exception(" create data Failed. ")

    @CheckmarxBase.catch_exception
    def _get_last_finished(self, projectid, runid, headers):
        checkmarx_last_finished = self.checkmarx_base_url + \
                                  '/sast/scans?projectId={projectid}&Last=3&scanStatus=Finished'
        url = checkmarx_last_finished.format(
            projectid=projectid)
        r = requests.get(url, headers=headers)
        result = str(r.content, 'utf-8')
        if r.status_code != 200:
            raise Exception(" get Last Finished Failed. ")
        if runid in result:
            return True
        else:
            return False

    @CheckmarxBase.catch_exception
    def _get_report_id(self, runid, headers):

        checkmarx_create_report = self.checkmarx_base_url + \
                                  '/reports/sastScan'
        data = {"reportType": "CSV", "ScanId": runid}
        r = requests.post(
            checkmarx_create_report,
            data=json.dumps(data),
            headers=headers)
        result = r.json()
        if r.status_code != 202:
            raise Exception(" get Report ID Failed. ")

        return result.get('reportId')
