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
This module provides general http handler functions for processing http responses from BCE services.
"""

import httplib
import json
from baidubce.exception import BceClientError
from baidubce.exception import BceServerError
from baidubce import utils


def parse_json(http_response, response):
    """If the body is not empty, convert it to a python object and set as the value of
    response.body. http_response is always closed if no error occurs.

    :param http_response: the http_response object returned by HTTPConnection.getresponse()
    :type http_response: httplib.HTTPResponse

    :param response: general response object which will be returned to the caller
    :type response: baidubce.BceResponse

    :return: always true
    :rtype bool
    """
    body = http_response.read()
    if body:
        response.__dict__.update(json.loads(body, object_hook=dict_to_python_object).__dict__)
    http_response.close()
    return True


def parse_error(http_response, response):
    """If the body is not empty, convert it to a python object and set as the value of
    response.body. http_response is always closed if no error occurs.

    :param http_response: the http_response object returned by HTTPConnection.getresponse()
    :type http_response: httplib.HTTPResponse

    :param response: general response object which will be returned to the caller
    :type response: baidubce.BceResponse

    :return: false if http status code is 2xx, raise an error otherwise
    :rtype bool

    :raise baidubce.exception.BceClientError: if http status code is NOT 2xx
    """
    if http_response.status / 100 == httplib.OK / 100:
        return False
    if http_response.status / 100 == httplib.CONTINUE / 100:
        raise BceClientError('Can not handle 1xx http status code')
    bse = None
    body = http_response.read()
    if body:
        d = json.loads(body)
        if 'code' in d:
            bse = BceServerError(d['message'], code=d['code'], request_id=d['requestId'])
        else:
            bse = BceServerError(d['Message'], code=d['Code'], request_id="")

    if bse is None:
        bse = BceServerError(http_response.reason, request_id=response.metadata.bce_request_id)
    bse.status_code = http_response.status
    raise bse


def dict_to_python_object(d):
    """

    :param d:
    :return:
    """
    attr = {}
    for k, v in d.items():
        k = (str(k))
        attr[k] = v
    return utils.Expando(attr)