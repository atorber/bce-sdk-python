# Copyright 2014 Baidu, Inc.

"""
This module provides a client class for TSDB.
"""

import copy
import json
import os
import time
import logging
from baidubce.auth import bce_v1_signer
from baidubce.bce_base_client import BceBaseClient
from baidubce.http import bce_http_client
from baidubce.http import handler
from baidubce.http import http_content_types
from baidubce.http import http_headers
from baidubce.http import http_methods
from baidubce.services.aihc import aihc_handler
from baidubce.services.aihc import chain_info_temp

cur_path = os.path.dirname(os.path.realpath(__file__))

# _logger = logging.getLogger(__name__)
# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def generate_aiak_parameter(chain_job_config=None, aiak_job_config=None):
    ak = ''
    sk = ''
    host = ''
    chain_info_temp.write_chain_info(ak, sk, host)
    # print(ak, sk, host)
    return chain_info_temp.generate_aiak_parameter(chain_job_config, aiak_job_config)


class AIHCClient(BceBaseClient):
    """
    sdk client
    """

    def __init__(self, config=None):
        BceBaseClient.__init__(self, config)

    def generate_aiak_parameter(self, chain_job_config=None, aiak_job_config=None):
        ak = self.config.credentials.access_key_id.decode('utf-8')
        sk = self.config.credentials.secret_access_key.decode('utf-8')
        host = self.config.endpoint.decode('utf-8')
        chain_info_temp.write_chain_info(ak, sk, host)
        # print(ak, sk, host)
        return chain_info_temp.generate_aiak_parameter(chain_job_config, aiak_job_config)

    def create_job_chain(self, config_file=None, index=None):
        # 接收参数或配置文件路径
        try:
            job_chain_info = chain_info_temp.load_config(config_file)
            jobs = job_chain_info['jobs']
            resourcePoolId = job_chain_info['resourcePoolId']

            chain_info_temp.validate_index(index, len(jobs))

            config_dir = os.path.dirname(config_file)
            command = chain_info_temp.build_command(job_chain_info, config_dir,
                                                    index)
            cur_job_info = jobs[index]
            cur_job_info['jobSpec']['command'] = command

            if 'scriptFile' in cur_job_info['jobSpec']:
                del cur_job_info['jobSpec']['scriptFile']

            logging.info("Job info at index retrieved successfully.")
            logging.info('payload:%s', json.dumps(cur_job_info))

            logging.info("Creating AI job using openapi...")

            client_token = 'test-aihc-' + str(int(time.time()))
            logging.info('client_token: %s', client_token)

            result = self.create_aijob(client_token=client_token,
                                       resourcePoolId=resourcePoolId,
                                       payload=cur_job_info)
            tasks_url = 'https://console.bce.baidu.com/aihc/tasks'
            print('====================================\n')
            print('任务创建结果: ', result)
            print('查看任务列表: https://console.bce.baidu.com/aihc/tasks')
            print('\n====================================')
            return {
                result: result,
                tasks_url: tasks_url
            }
        except (FileNotFoundError, IndexError, json.JSONDecodeError) as e:
            logging.error("Error: %s", e)
        except Exception as e:
            logging.error("An unexpected error occurred: %s", e)

    def create_aijob(
            self,
            client_token,
            resourcePoolId,
            payload):
        # print('create_aijob is called')
        path = b"/api/v1/aijobs"
        params = {
            "clientToken": client_token,
            "resourcePoolId": resourcePoolId
        }

        body = json.dumps(payload).encode('utf-8')
        return self._send_request(http_methods.POST, path=path, body=body,
                                  params=params,
                                  body_parser=aihc_handler.parse_json)

    def delete_aijob(self, aijob_id):
        """
        delete job

        :param job_id: job id to delete
        :type job_id: string

        :return: bce_request_id
        :rtype: baidubce.bce_response.BceResponses
        """
        path = b'/api/v1/aijobs/' + aijob_id
        return self._send_request(http_methods.DELETE, path,
                                  body_parser=aihc_handler.parse_json)

    def get_aijob(self, aijob_id):
        """
        get aijob

        :param aijob_id: aijob id to delete
        :type aijob_id: string

        :return: aijob info
        :rtype: baidubce.bce_response.BceResponse
        """

        path = b'/api/v1/aijobs/' + aijob_id
        return self._send_request(http_methods.GET, path,
                                  body_parser=aihc_handler.parse_json)

    def get_all_aijobs(self, resourcePoolId):
        """
        get all aijobs

        :return: aijob dict
        :rtype: baidubce.bce_response.BceResponse
        """
        params = {
            "resourcePoolId": resourcePoolId
        }
        path = b'/api/v1/aijobs'
        return self._send_request(http_methods.GET, path,
                                  params=params,
                                  body_parser=aihc_handler.parse_json)

    def _merge_config(self, config):
        if config is None:
            return self.config
        else:
            new_config = copy.copy(self.config)
            new_config.merge_non_none_values(config)
            return new_config

    def _send_request(
            self, http_method, path,
            body=None,
            params=None,
            headers=None,
            config=None,
            body_parser=None):
        config = self._merge_config(config)
        if headers is None:
            headers = {http_headers.CONTENT_TYPE: http_content_types.JSON}
        if body_parser is None:
            body_parser = handler.parse_json
        return bce_http_client.send_request(
            config, bce_v1_signer.sign, [handler.parse_error, body_parser],
            http_method, path, body, headers, params)
