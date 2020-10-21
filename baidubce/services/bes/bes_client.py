# Copyright 2014 Baidu, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

"""
This module provides a client class for BES.
"""

import copy
import json
import logging
import sys

from baidubce import bce_base_client
from baidubce import compat
from baidubce.auth import bce_v1_signer
from baidubce.http import bce_http_client
from baidubce.http import handler
from baidubce.http import http_methods
from baidubce.services.bes import bes_model
from baidubce.utils import required

_logger = logging.getLogger(__name__)

if sys.version_info[0] == 2:
    value_type = (str, unicode)
else:
    value_type = (str, bytes)


class BesClient(bce_base_client.BceBaseClient):
    """
    Bes sdk client
    """
    prefix = b'/api/bes/cluster'

    def __init__(self, config=None):
        bce_base_client.BceBaseClient.__init__(self, config)

    @required(name=value_type,
              password=value_type,
              modules=list,
              version=value_type,
              slot_type=value_type,
              is_open_service=bool,
              available_zone=value_type,
              security_group_id=value_type,
              subnet_uuid=value_type,
              vpc_id=value_type,
              billing=bes_model.Billing)
    def create_cluster(self,
                       name,
                       password,
                       modules,
                       version,
                       slot_type,
                       is_open_service,
                       available_zone,
                       security_group_id,
                       subnet_uuid,
                       vpc_id,
                       billing,
                       client_token=None):
        """
        Create cluster

        :param name: The parameter to specify es cluster name.
        :type name: string

        :param password: The parameter to specify password for manage cluster.
        :type password: string

        :param modules: The parameter to specify modules for cluster.
        :type modules: array

        :param version: The parameter to specify es cluster version.
        :type version: string

        :param slot_type: The parameter to specify the type of es cluster node resource.
        :type slot_type: string

        :param is_open_service: The parameter to specify es cluster enabled
        :type is_open_service: bool

        :param available_zone: he parameter to specify security zone.
        :type available_zone: string

        :param security_group_id: The parameter to specify id of the securityGroup.
        :type security_group_id: string

        :param subnet_uuid: The parameter to specify id of the subnet.
        :type subnet_uuid: string

        :param vpc_id: The parameter to specify id of the vpc.
        :type vpc_id: string

        :param billing: The parameter to specify id of billing info.
        :type billing: xxx

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/create'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        module_json_array = []
        for module in modules:
            module_json_array.append(module.__dict__)
        body = {
            'name': name,
            'password': password,
            'modules': module_json_array,
            'version': version,
            'slotType': slot_type,
            'isOpenService': is_open_service,
            'availableZone': available_zone,
            'securityGroupId': security_group_id,
            'subnetUuid': subnet_uuid,
            'vpcId': vpc_id,
            'billing': billing.__dict__
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(name=value_type,
              product_type=value_type,
              cluster_id=value_type,
              region=value_type,
              modules=list)
    def resize_cluster(self,
                       name,
                       product_type,
                       cluster_id,
                       region,
                       modules,
                       client_token=None):
        """
        resize cluster

        :param name: The parameter to specify es cluster name.
        :type name: string

        :param product_type: The parameter to specify mode of payment.
        :type product_type: string

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: array

        :param region: The parameter to specify region.
        :type region: string

        :param modules: The parameter to specify the type of es cluster node resource.
        :type modules: list

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/resize'
        params = {
            'orderType': "RESIZE"
        }
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        # if client_token is not None:
        #     params = {
        #         'clientToken': client_token
        #     }
        module_json_array = []
        for module in modules:
            module_json_array.append(module.__dict__)
        body = {
            'name': name,
            'productType': product_type,
            'modules': module_json_array,
            'clusterId': cluster_id,
            'region': region
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(page_no=int,
              page_size=int)
    def get_cluster_list(self,
                         page_no,
                         page_size,
                         client_token=None):
        """
        get es cluster list
        :param page_no: The parameter to specify cluster list pageNo.
        :type page_no: int

        :param page_size: The parameter to specify cluster list pageSize.
        :type page_size: int

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/list'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'pageNo': page_no,
            'pageSize': page_size
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(cluster_id=value_type)
    def get_cluster_detail(self,
                           cluster_id,
                           client_token=None):
        """
        get cluster detail info

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: string

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/detail'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'clusterId': cluster_id
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(cluster_id=value_type)
    def start_cluster(self,
                      cluster_id,
                      client_token=None):
        """
        start es cluster

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: string

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/start'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'clusterId': cluster_id
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(cluster_id=value_type)
    def stop_cluster(self,
                     cluster_id,
                     client_token=None):
        """
        stop es cluster

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: string

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/stop'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'clusterId': cluster_id
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(cluster_id=value_type)
    def delete_cluster(self,
                       cluster_id,
                       client_token=None):
        """
        delete es cluster

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: string

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/delete'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'clusterId': cluster_id
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(cluster_id=value_type,
              instance_id=value_type)
    def start_instance(self,
                       cluster_id,
                       instance_id,
                       client_token=None):
        """
        start instance of es cluster

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: string

        :param instance_id: The parameter to specify cluster id.
        :type instance_id: string

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/instance/start'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'clusterId': cluster_id,
            'instanceId': instance_id,
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    @required(cluster_id=value_type,
              instance_id=value_type)
    def stop_instance(self,
                      cluster_id,
                      instance_id,
                      client_token=None):
        """
        stop instance of es cluster

        :param cluster_id: The parameter to specify cluster id.
        :type cluster_id: string

        :param instance_id: The parameter to specify cluster id.
        :type instance_id: string

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = b'/instance/stop'
        params = None
        # if client_token is None:
        #     params['clientToken'] = generate_client_token()
        # else:
        #     params['clientToken'] = client_token

        if client_token is not None:
            params = {
                'clientToken': client_token
            }
        body = {
            'clusterId': cluster_id,
            'instanceId': instance_id,
        }
        region = self.config.region
        headers = {b'x-Region': region,
                   b'content-type': b'application/json;charset=UTF-8'}
        return self._send_request(http_methods.POST, path, params=params, body=json.dumps(body), headers=headers)

    def _merge_config(self, config=None):
        if config is None:
            return self.config
        else:
            new_config = copy.copy(self.config)
            new_config.merge_non_none_values(config)
            return new_config

    def _send_request(self, http_method, path,
                      body=None, headers=None, params=None,
                      config=None, body_parser=None):
        config = self._merge_config(config)
        if body_parser is None:
            body_parser = handler.parse_json

        config.endpoint = compat.convert_to_bytes(config.endpoint)
        # return bce_http_client.send_request(
        #     config, sign_wrapper([b'host', b'x-bce-date']), [handler.parse_error, body_parser],
        #     http_method, compat.convert_to_bytes(BesClient.prefix + path), body, headers, params)

        return bce_http_client.send_request(
            config, bce_v1_signer.sign, [handler.parse_error, body_parser],
            http_method, BesClient.prefix + path, body, headers, params)
