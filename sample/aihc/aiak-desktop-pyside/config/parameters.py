# config/parameters.py

# 输入参数
input_params = {
    "MODEL_NAME": "llama2-13b",
    "REPLICAS": "2",
    "VERSION": "v1",
    "TRAINING_PHASE": "pretrain",
    "TP": "",
    "PP": "",
    "DATASET_NAME": "WuDaoCorpus2.0_base_sample",
    "JSON_KEYS": "text",
    "IMAGE": "registry.baidubce.com/aihc-aiak/aiak-training-llm:ubuntu22.04-cu12.3-torch2.2.0-py310-bccl1.2.7.2_v2.1.1.5_release",
    "MOUNT_PATH": "/workspace/pfs",
    "MODEL_URL": "",
    "DATASET_URL": "",
    "OUTPUT_DIR": "",  # 新增的参数
}

model_options = [
    "llama2-7b", "llama2-13b", "llama2-70b",
    "llama3-8b", "llama3-70b",
    "qwen2-0.5b", "qwen2-1.5b", "qwen2-7b", "qwen2-72b",
    "baichuan2-7b", "baichuan2-13b",
    "qwen-1.8b", "qwen-7b", "qwen-14b", "qwen-72b",
    "qwen1.5-0.5b", "qwen1.5-1.8b", "qwen1.5-4b",
    "qwen1.5-7b", "qwen1.5-14b", "qwen1.5-32b", "qwen1.5-72b"
]

# 定义哪些字段是必填的（排除 MODEL_URL 和 DATASET_URL）
required_fields = [key for key, value in input_params.items() if value and key not in ["MODEL_URL", "DATASET_URL"]]
