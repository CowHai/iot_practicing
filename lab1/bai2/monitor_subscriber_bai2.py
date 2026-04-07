"""
Bài 2 - Chương trình 2: Monitoring Subscriber
Lắng nghe dữ liệu từ cảm biến và hiển thị kèm cảnh báo ngưỡng
"""

import paho.mqtt.client as mqtt
import json


# ===== CẤU HÌNH =====
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT = 1883
TOPIC = "iot/lab/+/data"  # Wildcard: lắng nghe tất cả cảm biến

# Ngưỡng cảnh báo
TEMP_HIGH_THRESHOLD = 35
HUMID_LOW_THRESHOLD = 40


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[Monitor] Kết nối thành công tới Broker: {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC, qos=1)
        print(f"[Monitor] Đã đăng ký lắng nghe topic (wildcard): {TOPIC}")
        print("[Monitor] Sẽ nhận dữ liệu từ: sensor01, sensor02, ...")
        print("[Monitor] Đang chờ dữ liệu từ cảm biến... (Nhấn Ctrl+C để thoát)\n")
    else:
        print(f"[Monitor] Kết nối thất bại, mã lỗi: {rc}")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))

        sensor_id   = data.get("sensor_id", "N/A")
        temperature = data.get("temperature", 0)
        humidity    = data.get("humidity", 0)
        timestamp   = data.get("timestamp", "N/A")

        # Hiển thị thông tin
        print("--- Receiving Sensor Data ---")
        print(f"  Topic : {msg.topic}")
        print(f"  ID    : {sensor_id}")
        print(f"  Temp  : {temperature} °C")
        print(f"  Humid : {humidity} %")
        print(f"  Time  : {timestamp}")

        # Kiểm tra ngưỡng cảnh báo
        if temperature > TEMP_HIGH_THRESHOLD:
            print("  ⚠  CẢNH BÁO: Nhiệt độ cao!")
        if humidity < HUMID_LOW_THRESHOLD:
            print("  ⚠  CẢNH BÁO: Độ ẩm thấp!")

        print("---------------------------\n")

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Monitor] Lỗi khi phân tích payload: {e}")
        print(f"[Monitor] Nội dung nhận được: {msg.payload}")


def on_disconnect(client, userdata, flags, rc, properties=None):
    print("[Monitor] Đã ngắt kết nối.")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print(f"[Monitor] Đang kết nối tới {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[Monitor] Dừng chương trình theo yêu cầu người dùng.")
        client.disconnect()


if __name__ == "__main__":
    main()
