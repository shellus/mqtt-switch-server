# MQTT开关服务端

简单的通过MQTT控制设备。

## 配置

复制示例配置文件并编辑：

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml，配置 MQTT 服务器和设备信息
```

## 运行

```bash
# Docker方式
docker-compose up -d

# 宿主机运行
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

## MQTT主题

- 订阅：`homepage/{device_id}/set` - 接收控制命令（0/1）
- 发布：`homepage/{device_id}/state` - 发布设备状态（0/1）
