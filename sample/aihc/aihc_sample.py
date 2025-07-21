# -*- coding: UTF-8 -*-
# Copyright 2014 Baidu, Inc.
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
Samples for AIHC client.
"""

from baidubce.services.aihc.aihc_client import AIHCClient
import aihc_sample_conf
import json
from tabulate import tabulate
import yaml

def expando_to_dict(obj):
    if isinstance(obj, dict):
        return {k: expando_to_dict(v) for k, v in obj.items()}
    elif hasattr(obj, '__dict__'):
        return {k: expando_to_dict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [expando_to_dict(item) for item in obj]
    else:
        return obj

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    __logger = logging.getLogger(__name__)

    aihc_client = AIHCClient(aihc_sample_conf.config)
    client_token = "client_token"

    # print("job_chain_info:")
    # job_chain_info = ''
    # print(json.dumps(job_chain_info, indent=4, ensure_ascii=False))

    res = aihc_client.get_all_pools()
    pool_list = []
    for pool in res.result.resourcePools:
        # 格式化输出pool核心信息，每个pool一行，表头为pool.name, pool.resourcePoolId, pool.status, pool.createdAt
        # pool_info = f"{pool.metadata.name} {pool.metadata.id} {pool.status.phase} {pool.status.nodeCount.used}/{pool.status.nodeCount.total} {pool.status.gpuCount.used}/{pool.status.gpuCount.total} {pool.metadata.createdAt}"
        # print(pool_info)
        pool_dic = {
            'NAME': pool.metadata.name,
            'ID': pool.metadata.id,
            'STATUS': pool.status.phase,
            'NODE_COUNT': f"{pool.status.nodeCount.used}/{pool.status.nodeCount.total}",
            'GPU_COUNT': f"{pool.status.gpuCount.used}/{pool.status.gpuCount.total}",
            'CREATED_AT': pool.metadata.createdAt
        }
        pool_list.append(pool_dic)
        
        # 将 Expando 对象转换为字典
        resource_pool_dict = expando_to_dict(pool)
        # print('资源池详情', json.dumps(resource_pool_dict, indent=4, ensure_ascii=False))

    
    # 打印为无网格表格
    print('资源池列表:')
    print(tabulate(pool_list, headers="keys", tablefmt="plain"))

    # create aijob
    resourcePoolId = 'cce-e0isdmib'
    # payload = {}
    # create_response = aihc_client.create_aijob(
    #     client_token=client_token,
    #     resourcePoolId=resourcePoolId,
    #     payload=payload
    # )
    # __logger.debug("[Sample AIHC] create_response:%s", create_response)

    # ai_jobs = aihc_client.get_all_aijobs(resourcePoolId=resourcePoolId)
    # __logger.debug("[Sample AIHC] ai_jobs:%s", ai_jobs)
    # print(ai_jobs)

    # chain_job_config = "/Users/luyuchao/Documents/GitHub/bce-sdk-python/sample/aihc"
    # aiak_job_config = "/Users/luyuchao/Documents/GitHub/bce-sdk-python/sample/aihc/aiak_pretrain_job_info.json"
    # aiak_job_config = "/Users/luyuchao/Documents/GitHub/bce-sdk-python/sample/aihc/aiak_sft_job_info.json"
    # aiak_job_config = json.dumps({
    #     "MODEL_NAME": "llama2-70b",
    #     "REPLICAS": "4",
    #     "VERSION": "v1",
    #     "TRAINING_PHASE": "sft",
    #     "TP": "",
    #     "PP": "",
    #     "DATASET_NAME": "alpaca_zh-llama3-train",
    #     "IMAGE": "registry.baidubce.com/aihc-aiak/aiak-training-llm:ubuntu22.04-cu12.3-torch2.2.0-py310-bccl1.2.7.2_v2.1.1.5_release",
    #     "MOUNT_PATH": "/workspace/pfs",
    #     "MODEL_URL": "",
    #     "DATASET_URL": "",
    #     "JSON_KEYS": ""
    # })
    # chain_job_config = "/Users/zhangsan/Documents/GitHub/bce-sdk-python/sample/aihc"
    # aiak_job_config = "/Users/zhangsan/Documents/GitHub/bce-sdk-python/sample/aihc/aiak_pretrain_job_info.json"
    # job_chain_info = aihc_client.generate_aiak_parameter(chain_job_config, aiak_job_config)
    # print(job_chain_info)

    # job_chain_info = aihc_client.generate_aiak_parameter(chain_job_config, aiak_job_config)
    # print(job_chain_info)

    # job_info_config = "/Users/luyuchao/Documents/GitHub/bce-sdk-python/sample/aihc/sft-llama2-7b-train-v1.json"
    # job_info = aihc_client.create_job_chain(job_info_config, 1)
    res = aihc_client.get_pool(resourcePoolId)
    resource_pool = expando_to_dict(res.result)
    print('资源池详情:')
    print(yaml.dump(resource_pool, allow_unicode=True))

    res = aihc_client.get_all_nodes(resourcePoolId=resourcePoolId)
    nodes = res.result.nodes
    node_list = []
    for node in nodes:
        # print(node.name, node.nodeId, node.status, node.createdAt)
        # 格式化输出 node.name, node.nodeId, node.status, node.createdAt
        # print(node)
        node = expando_to_dict(node)
        node = {k.strip(): v for k, v in node.items()}
        node_info = {
            'nodeName': node['nodeName'],
            'statusPhase': node['statusPhase'],
            'instanceName': node['instanceName'],
            'instanceId': node['instanceId'],
            'gpuTotal': node['gpuTotal'],
            'gpuAllocated': node['gpuAllocated'],
            'region': node['region'],
            'zone': node['zone'],
        }
        node_list.append(node_info)
    
    # 打印为无网格表格
    print('节点列表:')
    print(tabulate(node_list, headers="keys", tablefmt="plain"))

    res = aihc_client.get_all_queues(resourcePoolId=resourcePoolId)
    queues = res.result.queues
    queue_list = []
    for queue in queues:
        # print(queue.name, queue.queueId, queue.status, queue.createdAt)
        # 格式化输出 queue.name, queue.queueId, queue.status, queue.createdAt
        queue_info = {
            'name': queue.name,
            'state': queue.state,
            'queueType': queue.queueType,
            'reclaimable': queue.reclaimable,
            'disableOversell': queue.disableOversell,
            'createdTime': queue.createdTime
        }
        queue_list.append(queue_info)
    
    # 打印为无网格表格
    print('队列列表:')
    print(tabulate(queue_list, headers="keys", tablefmt="plain"))

    res = aihc_client.get_queue(resourcePoolId, queueName="default")
    queue_info = expando_to_dict(res.result)
    print('队列详情:')
    print(yaml.dump(queue_info, allow_unicode=True))

    res = aihc_client.get_all_aijobs(resourcePoolId=resourcePoolId)
    jobs = res.result.jobs
    job_list = []
    for job in jobs:
        # print(job.name, job.jobId, job.status, job.createdAt)
        # 格式化输出 job.name, job.jobId, job.status, job.createdAt
        job_info = {
            'NAME': job.name,
            'ID': job.jobId,
            'STATUS': job.status,
            'CREATED_AT': job.createdAt
        }
        job_list.append(job_info)
    
    # 打印为无网格表格
    print('任务列表:')
    print(tabulate(job_list, headers="keys", tablefmt="plain"))

    # print(json.dumps(res.result, indent=4, ensure_ascii=False))
    # aihc_client.get_webterminal(resourcePoolId=resourcePoolId)

    jobId = "pytorchjob-8455f882-09dd-4c9e-9893-901fc4f5ac9e"
    res = aihc_client.get_aijob(resourcePoolId, jobId)
    job_info = expando_to_dict(res.result)

    print('任务详情:')
    print(yaml.dump(job_info, allow_unicode=True))

    pods = res.result.podList.pods
    pod_list = []
    for pod in pods:
        pod_info = {
            'replicaType': pod.replicaType,
            'name': pod.objectMeta.name,
            'namespace': pod.objectMeta.namespace,
            'podPhase': pod.podStatus.podPhase,
            'status': pod.podStatus.status,
            'creationTimestamp': pod.objectMeta.creationTimestamp
        }
        pod_list.append(pod_info)
    print('任务Pod列表:')
    print(tabulate(pod_list, headers="keys", tablefmt="plain"))

    job_status = [{
        'name': job_info['name'],
        'priority': job_info['priority'],
        'pool/queue': f"{job_info['resourcePoolId']}/{job_info['queue']}",
        'replicas': job_info['replicas'],
        'status': job_info['status'],
        'runningAt': job_info['runningAt'],
        'scheduledAt': job_info['scheduledAt'],
       'createdAt': job_info['createdAt'],
    }]
    print('任务状态:')
    print(tabulate(job_status, headers="keys", tablefmt="plain"))
    
    # print(json.dumps(job_info, indent=4, ensure_ascii=False))

    jobFramework = 'PyTorchJob'
    events_res = aihc_client.get_aijob_events(resourcePoolId, jobId, jobFramework)
    events = expando_to_dict(events_res.result)
    print(events)
    print('任务事件:')
    print(yaml.dump(events, allow_unicode=True))
    
    podName = "pxy-moe-48hours-cpu-master-0"

    logs_res = aihc_client.get_aijob_logs(resourcePoolId, jobId, podName)
    logs = expando_to_dict(logs_res.result)
    print(logs)
    print('任务实例日志:')
    print(yaml.dump(logs, allow_unicode=True))

    res = aihc_client.get_aijob_pod_events(resourcePoolId, jobId, podName, jobFramework)
    pod_events = expando_to_dict(res.result)
    print(pod_events)
    print('任务实例事件:')
    print(yaml.dump(pod_events, allow_unicode=True))

    wss_res = aihc_client.get_webterminal(resourcePoolId, jobId, podName)
    webterminal = expando_to_dict(wss_res.result)
    print('Web Terminal信息:')
    print(yaml.dump(webterminal, allow_unicode=True))

    jobId = "pytorchjob-b4970686-6133-4137-949d-e12564e22d62"
    res = aihc_client.stop_aijob(resourcePoolId, jobId)
    print(res)
    print(res.message)
    print('停止任务成功:')
    print(yaml.dump(res.result, allow_unicode=True))

    # res = aihc_client.delete_aijob(resourcePoolId, jobId)
    # print(res.result)
    # print('删除任务成功:')
    # print(yaml.dump(res.result, allow_unicode=True))
