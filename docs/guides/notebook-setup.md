# Notebook Remote Setup Guide

为了在远程服务器上运行 Jupyter Notebook 并正常查看交互式地图（geemap/ipyleaflet），请遵循以下步骤。

## 1. 端口转发 (SSH Tunneling)

交互式地图依赖于服务器上的动态瓦片服务。在本地启动 SSH 连接时，请务必转发 Jupyter 端口（默认 8888）：

```bash
ssh -L 8888:localhost:8888 user@remote_server_ip
```

## 2. 启动 Jupyter

在服务器端，启动 Jupyter Lab 时确保其监听在 localhost：

```bash
jupyter lab --no-browser --ip=127.0.0.1 --port=8888
```

## 3. 代理配置

本库中的 Notebook 已内置了针对 `jupyter-server-proxy` 的配置。如果发现地图无法加载，请检查 Notebook 开头是否包含：

```python
import os
os.environ['LOCALTILESERVER_CLIENT_PREFIX'] = 'proxy/{port}'
```

## 4. 依赖检查

确保已安装以下关键组件：
- `geemap` & `ipyleaflet`: 核心交互绘图
- `jupyter-server-proxy`: 端口代理
- `localtileserver`: 栅格瓦片服务
