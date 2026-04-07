"""
Bài 1 - Chương trình 2: Subscriber
Kết nối tới MQTT broker và lắng nghe topic iot/lab/message
"""

import paho.mqtt.client as mqtt
from datetime import datetime


# ===== CẤU HÌNH BROKER =====
BROKER_HOST = "broker.hivemq.com"   # MQTT broker công cộng
BROKER_PORT = 1883
TOPIC = "iot/lab/message"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Subscriber] Kết nối thành công tới Broker: {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC, qos=1)
        print(f"[Subscriber] Đã đăng ký lắng nghe topic: {TOPIC}")
        print("[Subscriber] Đang chờ nhận tin nhắn... (Nhấn Ctrl+C để thoát)\n")
    else:
        print(f"[Subscriber] Kết nối thất bại, mã lỗi: {rc}")


def on_message(client, userdata, msg):
    now = datetime.now().strftime("%H:%M:%S")
    payload = msg.payload.decode("utf-8")

    print("=" * 45)
    print("Nhận được message:")
    print(f"  Topic  : {msg.topic}")
    print(f"  Payload: {payload}")
    print(f"  Time   : {now}")
    print("=" * 45)


def on_disconnect(client, userdata, flags, rc, properties=None):
    print("[Subscriber] Đã ngắt kết nối.")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print(f"[Subscriber] Đang kết nối tới Broker: {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[Subscriber] Dừng chương trình theo yêu cầu người dùng.")
        client.disconnect()


if __name__ == "__main__":
    main()
