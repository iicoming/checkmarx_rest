# -*- encoding: utf-8 -*-
"""
@File    : CheckmarxRedis.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""

import json

import requests

from checkmarx.CheckmarxBase import CheckmarxBase


class CheckmarxRedis(CheckmarxBase):
    def __init__(self):
        super().__init__()

    @CheckmarxBase.catch_exception
    def import_redis(self):

        total = self.client.llen('import_redis')

        for item in range(total):

            import_redis = self.client.rpop('import_redis')
            data = json.loads(import_redis)
            projectId = data.get('ProjectID')
            reportId = data.get('reportId')

            git_address = self._get_project_info(
                projectId, self.checkmarx_headers)

            if git_address:
                data['git_address'] = git_address
            flag = self._get_report_status(reportId, self.checkmarx_headers)
            if not flag:
                self.client.lpush('import_redis', import_redis)
            else:
                self._get_report_data(data, reportId, self.checkmarx_headers)

    @CheckmarxBase.catch_exception
    def _get_report_data(self, data, reportid, headers):
        checkmarx_report = self.checkmarx_base_url + \
                           '/reports/sastScan/{reportid}'

        url = checkmarx_report.format(reportid=reportid)
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return
        result = str(r.content, 'utf-8')
        vulns = result.split("\r\n")
        tmp = {}
        for index, item in enumerate(vulns):
            if index == 0:
                continue
            if not item:
                break
            values = item.replace("\"", "").split(",")
            if len(values) < 25:
                continue
            commint = values[19]
            if "To Verify" not in commint and "等待确认" not in commint:
                continue
            tmp['git'] = data.get('git_address')
            tmp['branch'] = data.get('branch')
            tmp['vuln_name'] = values[0]
            tmp['level'] = values[20]
            tmp['link'] = values[23]
            tmp['timestamp'] = self.today
            self.client.lpush('vulns', json.dumps(tmp))

    @CheckmarxBase.catch_exception
    def _get_report_status(self, reportid, headers):
        checkmarx_report_status = self.checkmarx_base_url + \
                                  "/reports/sastScan/{reportid}/status"

        url = checkmarx_report_status.format(
            reportid=reportid)

        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            raise Exception(" get Reported Status Failed. ")
        result = r.json()
        if result.get('status') and 'Created' in result.get(
                'status').get('value'):
            return True
        else:
            return False

    @CheckmarxBase.catch_exception
    def _get_project_info(self, projectId, headers):

        checkmarx_project_info = self.checkmarx_base_url + \
                                 '/sast/scans?projectId={projectId}&last=1'
        url = checkmarx_project_info.format(projectId=projectId)
        r = requests.get(url, headers=headers)
        result = r.json()
        if r.status_code != 200:
            raise Exception(" get project info Failed. ")
        if len(result) == 1:
            if result[0].get('scanState') and result[0].get(
                    'scanState').get('path'):
                return result[0].get('scanState').get('path')
        return ''
