"""
Bài 1 - Chương trình 1: Publisher
Kết nối tới MQTT broker và gửi thông điệp lên topic iot/lab/message
"""

import paho.mqtt.client as mqtt
import time

# ===== CẤU HÌNH BROKER =====
BROKER_HOST = "broker.hivemq.com"   # MQTT broker công cộng
BROKER_PORT = 1883
TOPIC = "iot/lab/message"

# ===== THÔNG TIN SINH VIÊN =====
HO_TEN = "Cao Duy Hải"
MA_SINH_VIEN = "B20DCCN218"
NOI_DUNG = "Xin chào từ client Python MQTT"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Publisher] Kết nối thành công tới Broker: {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[Publisher] Kết nối thất bại, mã lỗi: {rc}")


def on_publish(client, userdata, mid, reason_code=None, properties=None):
    print(f"[Publisher] Đã gửi tin nhắn thành công (mid={mid})")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"[Publisher] Đang kết nối tới Broker: {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    # Chờ kết nối
    time.sleep(2)

    # Tạo payload
    payload = f"{NOI_DUNG} - {MA_SINH_VIEN} - {HO_TEN}"

    # Gửi nhiều thông điệp liên tiếp
    for i in range(1, 4):
        print(f"\n[Publisher] Đang gửi tin nhắn lần {i}...")
        result = client.publish(TOPIC, payload, qos=1)
        result.wait_for_publish()
        print(f"[Publisher] Topic: {TOPIC}")
        print(f"[Publisher] Payload: {payload}")
        time.sleep(2)

    client.loop_stop()
    client.disconnect()
    print("\n[Publisher] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
