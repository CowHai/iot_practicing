"""
Bài 3 - Chương trình 1: Multi-Device Simulator
Mô phỏng NHIỀU thiết bị IoT (light01, fan01, pump01):
  - Mỗi thiết bị subscribe topic điều khiển riêng: iot/lab/<device>/cmd
  - Mỗi thiết bị publish trạng thái lên topic riêng: iot/lab/<device>/status
  - Sử dụng 1 MQTT client + wildcard topic iot/lab/+/cmd để quản lý tất cả.
  - Xử lý lệnh sai: báo lỗi nếu không phải ON/OFF.
"""

import paho.mqtt.client as mqtt
import json


# ===== CẤU HÌNH =====
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883

# Danh sách thiết bị cần mô phỏng
DEVICES = {
    "light01": {"label": "Đèn",    "icon": "💡"},
    "fan01"  : {"label": "Quạt",   "icon": "🌀"},
    "pump01" : {"label": "Máy bơm","icon": "💧"},
}

# Trạng thái ban đầu của từng thiết bị
device_states: dict[str, str] = {dev_id: "OFF" for dev_id in DEVICES}

# Wildcard: lắng nghe lệnh của tất cả thiết bị
TOPIC_CMD_WILDCARD = "iot/lab/+/cmd"


# ===== HELPERS =====

def topic_cmd(device_id: str) -> str:
    return f"iot/lab/{device_id}/cmd"


def topic_status(device_id: str) -> str:
    return f"iot/lab/{device_id}/status"


def publish_status(client: mqtt.Client, device_id: str, state: str) -> None:
    """Gửi trạng thái của thiết bị lên broker (retain=True để controller nhận ngay khi subscribe)."""
    payload = json.dumps({"device_id": device_id, "state": state})
    client.publish(topic_status(device_id), payload, qos=1, retain=True)
    info = DEVICES[device_id]
    icon = "🟢" if state == "ON" else "⭕"
    print(f"  [{device_id}] {icon} {info['label']} → {state}  (đã publish status)")


# ===== MQTT CALLBACKS =====

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Device] Kết nối thành công tới Broker: {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_CMD_WILDCARD, qos=1)
        print(f"[Device] Đã đăng ký lắng nghe lệnh (wildcard): {TOPIC_CMD_WILDCARD}")

        # Publish trạng thái ban đầu cho tất cả thiết bị
        print("[Device] Gửi trạng thái ban đầu:")
        for dev_id, state in device_states.items():
            publish_status(client, dev_id, state)

        print("\n[Device] Đang chờ lệnh điều khiển...\n")
        print("         Thiết bị được quản lý:")
        for dev_id, info in DEVICES.items():
            print(f"           {info['icon']} {dev_id} ({info['label']}) — CMD: {topic_cmd(dev_id)}")
        print()
    else:
        print(f"[Device] Kết nối thất bại, mã lỗi: {rc}")


def on_message(client, userdata, msg):
    """Xử lý lệnh từ topic iot/lab/<device_id>/cmd."""
    # Trích device_id từ topic: "iot/lab/light01/cmd" → "light01"
    parts = msg.topic.split("/")
    if len(parts) != 4:
        print(f"[Device] Topic không hợp lệ: {msg.topic}")
        return

    device_id = parts[2]
    command   = msg.payload.decode("utf-8").strip().upper()

    if device_id not in DEVICES:
        # Bỏ qua lặng lẽ: có thể là retained message cũ trên broker
        return

    info = DEVICES[device_id]
    print(f"[Device] Nhận lệnh '{command}' cho {info['icon']} {device_id} ({info['label']})")

    if command == "ON":
        device_states[device_id] = "ON"
        print(f"  → {info['label']} đã BẬT!")
        publish_status(client, device_id, "ON")
    elif command == "OFF":
        device_states[device_id] = "OFF"
        print(f"  → {info['label']} đã TẮT!")
        publish_status(client, device_id, "OFF")
    else:
        # Lệnh không hợp lệ — không thay đổi trạng thái, không publish status
        print(f"  ❌ Lệnh không hợp lệ: '{command}'. Chỉ chấp nhận 'ON' hoặc 'OFF'.")
    print()


def on_disconnect(client, userdata, flags, rc, properties=None):
    print("[Device] Đã ngắt kết nối.")


# ===== MAIN =====

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print("[Device] Khởi động bộ mô phỏng thiết bị IoT...")
    print(f"[Device] Thiết bị: {', '.join(DEVICES.keys())}")
    print(f"[Device] Đang kết nối tới {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[Device] Tắt bộ mô phỏng theo yêu cầu người dùng.")
        client.disconnect()


if __name__ == "__main__":
    main()
