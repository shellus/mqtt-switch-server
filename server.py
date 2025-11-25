#!/usr/bin/env python3
"""
MQTT开关服务端
订阅 homepage/{device_id}/set 控制设备
发布 homepage/{device_id}/state 报告状态
"""
import os
import sys
import yaml
import subprocess
import signal
import paho.mqtt.client as mqtt

class MQTTSwitchServer:
    def __init__(self, config_file='config.yaml'):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)

        self.mqtt_config = self.config['mqtt']
        self.devices = {d['id']: d for d in self.config['devices']}
        self.client = None
        self.running = True

    def execute_command(self, command):
        """执行shell命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0, result.stdout.strip()
        except Exception as e:
            print(f"执行命令失败: {e}")
            return False, str(e)

    def get_device_state(self, device_id):
        """获取设备状态"""
        device = self.devices.get(device_id)
        if not device:
            return '0'

        success, output = self.execute_command(device['state_command'])
        return output if success else '0'

    def set_device_state(self, device_id, state):
        """设置设备状态"""
        device = self.devices.get(device_id)
        if not device:
            print(f"设备不存在: {device_id}")
            return False

        command = device['enable_action'] if state == '1' else device['disable_action']
        success, output = self.execute_command(command)

        if success:
            print(f"设备 {device['name']} 已{'开启' if state == '1' else '关闭'}")
            # 立即发布新状态
            self.publish_state(device_id)
        else:
            print(f"设备 {device['name']} 操作失败: {output}")

        return success

    def publish_state(self, device_id):
        """发布设备状态"""
        state = self.get_device_state(device_id)
        topic = f"{self.mqtt_config['base_topic']}/{device_id}/state"
        self.client.publish(topic, state, qos=1, retain=True)
        print(f"发布状态: {topic} = {state}")

    def on_connect(self, client, userdata, flags, rc, properties=None):
        """MQTT连接回调 (API v2)"""
        if rc == 0:
            print("✅ 已连接到MQTT Broker")
            # 订阅所有设备的控制主题
            for device_id in self.devices:
                topic = f"{self.mqtt_config['base_topic']}/{device_id}/set"
                client.subscribe(topic, qos=1)
                print(f"✅ 订阅: {topic}")

            # 发布所有设备的初始状态
            for device_id in self.devices:
                self.publish_state(device_id)
        else:
            print(f"❌ 连接失败，错误码: {rc}")

    def on_message(self, client, userdata, msg):
        """MQTT消息回调"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')

        print(f"收到消息: {topic} = {payload}")

        # 解析主题: homepage/{device_id}/set
        parts = topic.split('/')
        if len(parts) == 3 and parts[2] == 'set':
            device_id = parts[1]
            if payload in ['0', '1']:
                self.set_device_state(device_id, payload)

    def shutdown(self, signum=None, frame=None):
        """优雅退出处理"""
        if not self.running:
            return

        signal_name = signal.Signals(signum).name if signum else "INTERRUPT"
        print(f"\n收到 {signal_name} 信号，正在退出...")
        self.running = False

        if self.client:
            self.client.disconnect()
            self.client.loop_stop()

    def run(self):
        """启动服务"""
        # 注册信号处理器
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)

        # 初始化MQTT客户端（使用新API）
        self.client = mqtt.Client(
            client_id=self.mqtt_config['client_id'],
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        self.client.username_pw_set(
            self.mqtt_config['username'],
            self.mqtt_config['password']
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # 连接到Broker
        broker_url = self.mqtt_config['broker']
        if broker_url.startswith('mqtt://'):
            # TCP连接
            parts = broker_url.replace('mqtt://', '').split(':')
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 1883
            print(f"连接到 {host}:{port} (TCP)")
            self.client.connect(host, port, 60)
        elif broker_url.startswith('wss://'):
            # WebSocket连接
            import ssl
            host = broker_url.replace('wss://', '').split('/')[0]
            port = 443
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)
            self.client.ws_set_options(path="/mqtt")
            print(f"连接到 {host}:{port} (WSS)")
            self.client.connect(host, port, 60)
        else:
            print("不支持的协议，仅支持 mqtt:// 或 wss://")
            return

        # 阻塞运行
        print("服务已启动，按Ctrl+C或发送SIGTERM退出")
        try:
            self.client.loop_forever()
        except Exception as e:
            print(f"运行异常: {e}")
        finally:
            print("服务已停止")

if __name__ == '__main__':
    server = MQTTSwitchServer('config.yaml')
    server.run()
