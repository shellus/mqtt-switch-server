# MQTT开关服务端

通过MQTT控制设备开关的服务端程序。

## 安装

### Docker方式（推荐）

参考主目录的 `docker-compose.yml`

### 宿主机运行（使用venv）

```bash
cd mqtt-switch-server
python3 -m venv venv
source venv/bin/activate
PIP_INDEX_URL=https://repo.huaweicloud.com/repository/pypi/simple pip install -r requirements.txt
```

## 配置

复制示例配置文件并编辑：

```bash
cp config.yaml.example config.yaml
# 编辑 config.yaml，配置 MQTT 服务器和设备信息
```

配置说明参考 `config.yaml.example`。

## 运行

### Docker方式

```bash
docker-compose up -d
```

### 宿主机运行

```bash
source venv/bin/activate
python3 server.py
```

## MQTT主题

- 订阅：`homepage/{device_id}/set` - 接收控制命令（0/1）
- 发布：`homepage/{device_id}/state` - 发布设备状态（0/1）

## Homepage配置

在 `services.yaml` 中添加：

```yaml
- 智能控制:
    - 测试灯:
        id: test-light-control
        data-device: test-light  # 必须，对应config.yaml中的id
        icon: mdi-lightbulb-#FFD700
        href: "#"
        description: MQTT控制测试灯
```

注意：必须添加 `data-device` 属性，值为设备ID。
