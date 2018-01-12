# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
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
This module provides a client class for SUBNET.
"""

import copy
import json
import logging
import uuid

from baidubce import bce_base_client
from baidubce.auth import bce_v1_signer
from baidubce.http import bce_http_client
from baidubce.http import handler
from baidubce.http import http_methods

from baidubce.utils import required

_logger = logging.getLogger(__name__)


class SubnetClient(bce_base_client.BceBaseClient):
    """
    Subnet base sdk client
    """
    prefix = '/v1'

    def __init__(self, config=None):
        bce_base_client.BceBaseClient.__init__(self, config)

    def _merge_config(self, config=None):
        """
        :param config:
        :type config: baidubce.BceClientConfiguration
        :return:
        """
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
        if headers is None:
            headers = {'Accept': '*/*', 'Content-Type': 'application/json;charset=utf-8'}
        return bce_http_client.send_request(
            config, bce_v1_signer.sign, [handler.parse_error, body_parser],
            http_method, SubnetClient.prefix + path, body, headers, params)

    @required(name=(str, unicode),
              zone_name=(str, unicode),
              cidr=(str, unicode),
              vpc_id=(str, unicode))
    def create_subnet(self, name, zone_name, cidr, vpc_id, subnet_type=None, description=None,
                      client_token=None, config=None):
        """
        Create a subnet with the specified options.

        :param name:
            The name of subnet that will be created.
        type name: string

        :param zone_name:
            The name of available zone which the subnet belong
            through listZones, we can get all available zone info at current region
            ee.g. "cn-gz-a"  "cn-gz-b"
        type zone_name: string

        :param cidr:
            The CIDR of this subnet.
        type cidr: string

        :param vpc_id:
            The id of vpc which this subnet belongs.
        type vpc_id: string

        :param subnet_type:
            The option param to describe the type of subnet create
        type subnet_type: string

        :param description:
            The option param to describe the subnet
        type description: string

        :param client_token:
            An ASCII string whose length is less than 64.
            The request will be idempotent if clientToken is provided.
            If the clientToken is not specified by the user, a random String
            generated by default algorithm will be used.
        type client_token: string

        :param config:
        :type config: baidubce.BceClientConfiguration

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = '/subnet'
        params = {}

        if client_token is None:
            params['clientToken'] = generate_client_token()
        else:
            params['clientToken'] = client_token

        body = {
            'name': name,
            'zoneName': zone_name,
            'cidr': cidr,
            'vpcId': vpc_id
        }

        if subnet_type is not None:
            body['subnetType'] = subnet_type
        if description is not None:
            body['description'] = description

        return self._send_request(http_methods.POST, path, body=json.dumps(body), params=params,
                                  config=config)

    def list_subnets(self, marker=None, max_keys=None, vpc_id=None,
                     zone_name=None, subnet_type=None, config=None):
        """
        Return a list of subnets owned by the authenticated user.

        :param marker:
            The optional parameter marker specified in the original request to specify
            where in the results to begin listing.
            Together with the marker, specifies the list result which listing should begin.
            If the marker is not specified, the list result will listing from the first one.
        :type marker: string

        :param max_keys:
            The optional parameter to specifies the max number of list result to return.
            The default value is 1000.
        :type max_keys: int

        :param vpc_id:
            The id of the vpc
        :type vpc_id: string

        :param zone_name:
            The name of available zone which the subnet belong
            through listZones, we can get all available zone info at current region
            ee.g. "cn-gz-a"  "cn-gz-b"
        :type zone_name: string

        :param subnet_type:
            The option param to describe the type of subnet to be created
        :type subnet_type: string

        :param config:
        :type config: baidubce.BceClientConfiguration

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = '/subnet'
        params = {}
        if marker is not None:
            params['marker'] = marker
        if max_keys is not None:
            params['maxKeys'] = max_keys
        if vpc_id is not None:
            params['vpcId'] = vpc_id
        if zone_name is not None:
            params['zoneName'] = zone_name
        if subnet_type is not None:
            params['subnetType'] = subnet_type

        return self._send_request(http_methods.GET, path, params=params, config=config)

    @required(subnet_id=(str, unicode))
    def get_subnet(self, subnet_id, config=None):
        """
        Get the detail information of a specified subnet.

        :param subnet_id:
            The id of the subnet.
        :type subnet_id: string

        :param config:
        :type config: baidubce.BceClientConfiguration

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = '/subnet/%s' % subnet_id

        return self._send_request(http_methods.GET, path, config=config)

    @required(subnet_id=(str, unicode))
    def delete_subnet(self, subnet_id, client_token=None, config=None):
        """
        Delete the specified subnet owned by the user.
        :param subnet_id:
            The id of the subnet to be deleted.
        :type subnet_id: string

        :param client_token:
            An ASCII string whose length is less than 64.
            The request will be idempotent if clientToken is provided.
            If the clientToken is not specified by the user, a random String generated by
            default algorithm will be used.
        :type client_token: string

        :param config:
        :type config: baidubce.BceClientConfiguration

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = '/subnet/%s' % subnet_id
        params = {}

        if client_token is None:
            params['clientToken'] = generate_client_token()
        else:
            params['clientToken'] = client_token

        return self._send_request(http_methods.DELETE, path, params=params, config=config)

    @required(subnet_id=(str, unicode), name=(str, unicode))
    def update_subnet(self, subnet_id, name, description=None, client_token=None, config=None):
        """
        Modify the special attribute to new value of the subnet owned by the user.

        :param subnet_id:
            The id of the specific subnet to be updated.
        :type subnet_id: string

        :param name:
            The name of the subnet
        :type name: string

        :param description:
            The option param to describe the subnet
        :type description: string

        :param client_token:
            An ASCII string whose length is less than 64.
            The request will be idempotent if clientToken is provided.
            If the clientToken is not specified by the user, a random String generated
            by default algorithm will be used.
        :type client_token: string

        :param config:
        :type config: baidubce.BceClientConfiguration

        :return:
        :rtype baidubce.bce_response.BceResponse
        """
        path = '/subnet/%s' % subnet_id
        params = {
            'modifyAttribute': None
        }
        body = {
            'name': name
        }

        if client_token is None:
            params['clientToken'] = generate_client_token()
        else:
            params['clientToken'] = client_token

        if description is not None:
            body['description'] = description

        return self._send_request(http_methods.PUT, path, json.dumps(body),
                                  params=params, config=config)


def generate_client_token_by_uuid():
    """
    The default method to generate the random string for client_token
    if the optional parameter client_token is not specified by the user.

    :return:
    :rtype string
    """
    return str(uuid.uuid4())
generate_client_token = generate_client_token_by_uuid



