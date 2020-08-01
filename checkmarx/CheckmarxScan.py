# -*- encoding: utf-8 -*-
"""
@File    : CheckmarxScan.py
@Time    : 2020/08/01 10:08
@Author  : iicoming@hotmail.com
"""
import json

import requests

from checkmarx.CheckmarxBase import CheckmarxBase
from config.config import private_key


class CheckmarxScan(CheckmarxBase):

    def __init__(self):
        super().__init__()

    @CheckmarxBase.catch_exception
    def create_scan_project_id(self, name, git):
        """
        1、create project with default configuration, will get project id
        """
        projects_url = self.checkmarx_base_url + "/projects"
        data = {
            "name": name,
            "owningTeam": 1,
            "isPublic": True
        }
        r = requests.post(
            projects_url,
            data=json.dumps(data),
            headers=self.checkmarx_headers)
        key = name + '_' + git
        if r.status_code == 400:
            if "Project name already exists" in r.json().get('messageDetails'):
                if not self.client.hget('projects', key):
                    project_id = self.get_project_info(name)
                    self.client.hset('projects', key, project_id)
                    return project_id
                else:
                    return self.client.hget('projects', key)
        if r.status_code != 201:
            raise Exception(" create_scan_project_id Failed. ")
        self.client.hset('projects', key, r.json().get('id'))
        return r.json().get('id')

    @CheckmarxBase.catch_exception
    def set_scan_project_git(self, project_id, git, branch):
        """
        2、set remote source setting to git
        """
        remote_settings_git_url = self.checkmarx_base_url + \
                                  "/projects/{id}/sourceCode/remoteSettings/git"
        url = remote_settings_git_url.format(id=project_id)
        data = {
            "url": git,
            "branch": "refs/heads/{branch}".format(branch=branch),
            "privateKey": private_key
        }

        r = requests.post(
            url,
            data=json.dumps(data),
            headers=self.checkmarx_headers)
        if r.status_code != 204:
            raise Exception(" set_scan_project_git Failed. :" +
                            str(r.content, 'utf-8'))

    @CheckmarxBase.catch_exception
    def set_data_retention_settings_by_project_id(
            self, project_id, scans_to_keep=3):
        """
        3、set data retention settings by project id
        """
        data_retention_settings_url = self.checkmarx_base_url + \
                                      "/projects/{id}/dataRetentionSettings"
        url = data_retention_settings_url.format(id=project_id)
        data = {
            "scansToKeep": scans_to_keep
        }
        r = requests.post(
            url,
            data=json.dumps(data),
            headers=self.checkmarx_headers)
        if r.status_code != 204:
            raise Exception(
                " set_data_retention_settings_by_project_id Failed. ")

    @CheckmarxBase.catch_exception
    def set_preset_id_settings(self, project_id):
        """
        4、define SAST scan settings
        """
        presetid_settings_url = self.checkmarx_base_url + "/sast/scanSettings"

        data = {
            "projectId": project_id,
            "presetId": 100000,
            "engineConfigurationId": 1}
        r = requests.post(
            presetid_settings_url,
            data=json.dumps(data),
            headers=self.checkmarx_headers)
        if r.status_code != 200:
            raise Exception(" set_preset_id_settings Failed. ")

    @CheckmarxBase.catch_exception
    def set_project_exclude_settings_by_project_id(
            self,
            project_id,
            exclude_folders_pattern="",
            exclude_files_pattern=""):
        exclude_settings_url = self.checkmarx_base_url + \
                               "/projects/{id}/sourceCode/excludeSettings"
        url = exclude_settings_url.format(id=project_id)

        data = {
            "excludeFoldersPattern": exclude_folders_pattern,
            "excludeFilesPattern": exclude_files_pattern
        }

        r = requests.put(
            url,
            data=json.dumps(data),
            headers=self.checkmarx_headers)
        if r.status_code != 200:
            raise Exception(
                " set_project_exclude_settings_by_project_id Failed. ")

    @CheckmarxBase.catch_exception
    def create_new_scan(
            self,
            project_id,
            is_incremental=True,
            is_public=True,
            force_scan=True,
            comment=""):
        scans_url = self.checkmarx_base_url + "/sast/scans"
        data = {
            "projectId": project_id,
            "isIncremental": is_incremental,
            "isPublic": is_public,
            "forceScan": force_scan,
            "comment": comment
        }
        r = requests.post(
            scans_url,
            data=json.dumps(data),
            headers=self.checkmarx_headers)
        if r.status_code != 201:
            raise Exception(" create_new_scan Failed. ")
        return r.json().get('id')

    @CheckmarxBase.catch_exception
    def start_scan(self):
        projects=self.get_scan_projects()
        for index,value in enumerate(projects):
            git_address=value.split(':')[0]
            branch=value.split(':')[1]
            scan_result = {}
            name = git_address.split(":")[1].split(".git")[0].replace('/', '_')
            project_id = self.create_scan_project_id(name, git_address)
            self.set_scan_project_git(project_id, git_address, branch)
            self.set_data_retention_settings_by_project_id(
                project_id=project_id, scans_to_keep=3)
            self.set_preset_id_settings(project_id)
            self.set_project_exclude_settings_by_project_id(project_id)
            scanid = self.create_new_scan(project_id)
            scan_result['git_address'] = git_address
            scan_result['branch'] = branch
            scan_result['ProjectID'] = project_id
            scan_result['RunId'] = str(scanid)
            self.client.lpush('create_report', json.dumps(scan_result))

    @CheckmarxBase.catch_exception
    def get_project_info(self, name):
        project_info = self.checkmarx_base_url + \
                       '/projects?projectName={name}&teamId=1'
        url = project_info.format(name=name)
        r = requests.get(
            url,
            headers=self.checkmarx_headers)
        if r.status_code != 200:
            raise Exception(" get_project_info Failed ")
        project_id = r.json()[0].get('id') if len(r.json()) > 0 else -1
        if project_id < 0:
            raise Exception(" get_project_git Failed ")
        return project_id

    @CheckmarxBase.catch_exception
    def get_project_git(self, name, git):
        project_id = self.get_project_info(name)
        project_git = self.checkmarx_base_url + \
                      '/projects/{id}/sourceCode/remoteSettings/git'
        url = project_git.format(id=project_id)
        r = requests.get(
            url,
            headers=self.checkmarx_headers)

        if r.status_code != 200:
            raise Exception(" get_project_git Failed  ")

        if r.json().get('url') == git:
            return (True, project_id)
        else:
            return (False, project_id)

    @CheckmarxBase.catch_exception
    def start_scan_test(self,git_address,branch):
        scan_result = {}
        name = git_address.split(":")[1].split(".git")[0].replace('/', '_')
        project_id = self.create_scan_project_id(name, git_address)
        self.set_scan_project_git(project_id, git_address, branch)
        self.set_data_retention_settings_by_project_id(
            project_id=project_id, scans_to_keep=3)
        self.set_preset_id_settings(project_id)
        self.set_project_exclude_settings_by_project_id(project_id)
        scanid = self.create_new_scan(project_id)
        scan_result['git_address'] = git_address
        scan_result['branch'] = branch
        scan_result['ProjectID'] = project_id
        scan_result['RunId'] = str(scanid)
        self.client.lpush('create_report', json.dumps(scan_result))

    @CheckmarxBase.catch_exception
    def get_scan_projects(self):

        projects=[]
        """
            获取待扫描项目信息
        """

        return projects

