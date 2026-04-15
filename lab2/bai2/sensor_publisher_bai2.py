"""
Bài 2 - Chương trình 1: Sensor Producer (AMQP)
Mô phỏng cảm biến gửi dữ liệu nhiệt độ và độ ẩm dưới dạng JSON
vào queue sensor_data_queue mỗi 3 giây.

JSON payload (yêu cầu):
  { "device_id": "sensor01", "temperature": 29.5, "humidity": 62.1 }

Mở rộng: bổ sung trường timestamp + mô phỏng 2 cảm biến.
"""

import pika
import json
import time
import random
from datetime import datetime


# ===== CẤU HÌNH =====
BROKER_HOST = "localhost"
BROKER_PORT = 5672
QUEUE_NAME  = "sensor_data_queue"
INTERVAL    = 3  # giây (theo yêu cầu)

# Mở rộng: mô phỏng 2 cảm biến khác nhau
DEVICE_IDS = ["sensor01", "sensor02"]


def create_payload(device_id: str) -> dict:
    """
    Tạo payload JSON theo đúng yêu cầu bài:
      device_id, temperature, humidity
    Mở rộng thêm: timestamp
    """
    return {
        "device_id"  : device_id,
        "temperature": round(random.uniform(20, 42), 1),
        "humidity"   : round(random.uniform(30, 90), 1),
        "timestamp"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    print(f"[Sensor] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=BROKER_HOST, port=BROKER_PORT)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    print(f"[Sensor] Queue: '{QUEUE_NAME}' | Chu kỳ: {INTERVAL} giây")
    print(f"[Sensor] Thiết bị: {', '.join(DEVICE_IDS)}")
    print("[Sensor] Nhấn Ctrl+C để dừng\n")

    try:
        while True:
            for device_id in DEVICE_IDS:
                payload = create_payload(device_id)
                message = json.dumps(payload)

                channel.basic_publish(
                    exchange="",
                    routing_key=QUEUE_NAME,
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2),
                )

                print(f"[{device_id}] Đã gửi → '{QUEUE_NAME}'")
                print(f"  device_id  : {payload['device_id']}")
                print(f"  temperature: {payload['temperature']}")
                print(f"  humidity   : {payload['humidity']}")
                print(f"  timestamp  : {payload['timestamp']}")
                print()

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\n[Sensor] Dừng gửi dữ liệu theo yêu cầu người dùng.")
    finally:
        connection.close()
        print("[Sensor] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
