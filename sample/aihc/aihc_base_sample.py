'''
基础客户端示例
'''

# !/usr/bin/env python
# coding=utf-8

from baidubce.exception import BceHttpClientError, BceServerError
from baidubce.services.aihc.aihc_client import AihcClient
from baidubce.http import http_methods

import sample.aihc.aihc_sample_conf as aihc_sample_conf
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("baidubce").setLevel(logging.INFO)
__logger = logging.getLogger(__name__)
__logger.setLevel(logging.INFO)

aihc_client = AihcClient(aihc_sample_conf.config)

def main():
    '''
    基础客户端示例
    '''
    try:
        response = aihc_client.base_client._send_request(http_methods.GET, b'/', params={'action': 'DescribeDatasets'})
        print(response)
    except BceHttpClientError as e:
        if isinstance(e.last_error, BceServerError):
            __logger.error('BceServerError: %s', e.last_error.message)
        else:
            __logger.error('BceHttpClientError: %s', e.last_error.message)

if __name__ == '__main__':
    main()
