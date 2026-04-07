"""
Bài 2 - Chương trình 1: Sensor Publisher
Mô phỏng NHIỀU cảm biến gửi dữ liệu nhiệt độ và độ ẩm định kỳ mỗi 3 giây.
Dải giá trị mở rộng để đôi khi vượt ngưỡng cảnh báo:
  - Nhiệt độ: 20–40 °C  (ngưỡng cảnh báo: > 35)
  - Độ ẩm: 30–90 %   (ngưỡng cảnh báo: < 40)
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from datetime import datetime


# ===== CẤU HÌNH =====
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
INTERVAL = 3  # giây

# Danh sách các cảm biến cần mô phỏng
SENSORS = [
    {"sensor_id": "sensor01", "topic": "iot/lab/sensor01/data"},
    {"sensor_id": "sensor02", "topic": "iot/lab/sensor02/data"},
]


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Sensor] Kết nối thành công tới Broker: {BROKER_HOST}:{BROKER_PORT}")
    else:
        print(f"[Sensor] Kết nối thất bại, mã lỗi: {rc}")


def on_publish(client, userdata, mid, reason_code=None, properties=None):
    pass  # im lặng khi publish thành công


def create_payload(sensor_id: str) -> dict:
    """
    Tạo payload JSON cho cảm biến.
    Dải nhiệt độ 20-40 và độ ẩm 30-90 để đôi khi vượt ngưỡng cảnh báo
    (> 35 °C hoặc < 40 %).
    """
    return {
        "sensor_id": sensor_id,
        "temperature": round(random.uniform(20, 40), 1),  # có thể vượt 35 °C
        "humidity": round(random.uniform(30, 90), 1),     # có thể xuống dưới 40 %
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_publish = on_publish

    print(f"[Sensor] Đang kết nối tới Broker: {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    # Chờ kết nối
    time.sleep(2)

    sensor_list = ", ".join(s["sensor_id"] for s in SENSORS)
    print(f"[Sensor] Bắt đầu gửi dữ liệu cho: {sensor_list}")
    print(f"[Sensor] Chu kỳ gửi mỗi thiết bị: {INTERVAL} giây (Nhấn Ctrl+C để dừng)\n")

    try:
        while True:
            # Gửi dữ liệu lần lượt từng thiết bị
            for sensor in SENSORS:
                payload = create_payload(sensor["sensor_id"])
                message = json.dumps(payload)

                result = client.publish(sensor["topic"], message, qos=1)
                result.wait_for_publish()

                print(f"[{sensor['sensor_id']}] Đã gửi → {sensor['topic']}")
                print(f"           Temp = {payload['temperature']} °C")
                print(f"           Humid = {payload['humidity']} %")
                print(f"           Time = {payload['timestamp']}")

            print()
            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\n[Sensor] Dừng gửi dữ liệu theo yêu cầu người dùng.")
    finally:
        try:
            client.loop_stop()  # có thể bị interrupt lần 2, bắt luôn
        except KeyboardInterrupt:
            pass
        client.disconnect()
        print("[Sensor] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
