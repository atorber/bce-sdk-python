# -*- coding: utf-8 -*-

# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
"""
Example for eip client.
"""

import example_conf
from baidubce import exception
from baidubce.services.eip.eip_client import EipClient

def test_start_auto_renew_eip(eip_client, eip, auto_renew_time_unit, auto_renew_time):
    """
    Enable auto renew for specified EIP.

    Args:
        :type eip_client: EipClient
        :param eip_client: EipClient

        :type eip: string
        :param eip: eip address to be enable to auto-renew.

        :type auto_renew_time_unit: int
        :param auto_renew_time_unit: the unit of time for auto renew,
        default auto_renew_time_unit is 1

        :type auto_renew_time: string
        :param auto_renew_time: time unit of auto_renew_time, default 'month'.

    Return: 
        None

    Raise:
        BceHttpClientError: Http request failed
    """
    try:
        res = eip_client.start_auto_renew_eip(eip, auto_renew_time_unit, auto_renew_time)
        print(res)
    except exception.BceHttpClientError as e:
        #异常处理
        print(e.last_error)
        print(e.request_id)
        print(e.code)
        return None

if __name__ == '__main__':
    # 创建EIPClient
    eip_client = EipClient(example_conf.config)
    # 指定EIP
    eip = "x.x.x.x"
    # 自动续费一个月
    test_start_auto_renew_eip(eip_client, eip, None, None)
    # 指定续费时间单位
    auto_renew_time_unit = "month"
    # 指定续费时间
    auto_renew_time = 2
    # 指定续费参数，自动续费两个月
    test_start_auto_renew_eip(eip_client, eip, auto_renew_time_unit, auto_renew_time)