# AIHC示例说明

python -m sample.aihc.aihc_model_sample

## 环境准备

- 准备 Python 3.8+ 运行环境（建议使用虚拟环境）。
- 在仓库根目录执行示例，或确保已将仓库根目录加入 `PYTHONPATH`。

## 配置

编辑 `sample/aihc/aihc_sample_conf.py`，设置以下参数为你自己的值：

- `HOST`: AIHC 服务接入域名，例如 `aihc.bj.baidubce.com`
- `AK`: 访问密钥 AccessKey
- `SK`: 访问密钥 SecretKey

## 运行示例

### 推荐方式（模块方式，优先使用本地源码）

```
cd /Users/luyuchao/Documents/GitHub/bce-sdk-python
python -m sample.aihc.aihc_model_sample
```

### 备用方式（显式指定本地源码路径）

```
export PYTHONPATH=/Users/luyuchao/Documents/GitHub/bce-sdk-python
python /Users/luyuchao/Documents/GitHub/bce-sdk-python/sample/aihc/aihc_model_sample.py
```

### 其他示例

```
python -m sample.aihc.aihc_dataset_sample
python -m sample.aihc.aihc_job_sample
python -m sample.aihc.aihc_service_sample
python -m sample.aihc.aihc_devinstance_sample
python -m sample.aihc.aihc_base_sample
python -m sample.aihc.aihc_pool_sample
```

## 常见问题

- ImportError: cannot import name 'AihcClient'
  - 原因：命中了环境中已安装的旧版 `baidubce` 包（不包含 `AihcClient`），而非当前仓库源码。
  - 解决：使用“模块方式运行”或设置 `PYTHONPATH` 指向仓库根目录；或在当前环境卸载旧版包后重试：

```
pip uninstall baidubce
```

## 日志与调试

- 示例默认开启基本日志输出，可根据需要在示例文件中调整 `logging` 级别。