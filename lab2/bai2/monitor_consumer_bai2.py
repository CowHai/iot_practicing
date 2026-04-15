"""
Bài 2 - Chương trình 2: Monitoring Consumer (AMQP)
Nhận dữ liệu từ queue sensor_data_queue, phân tích và in ra:
  - mã thiết bị (device_id)
  - nhiệt độ (temperature)
  - độ ẩm (humidity)
Cảnh báo:
  - nhiệt độ > 35  → "CANH BAO: Nhiet do cao"
  - độ ẩm   < 40  → "CANH BAO: Do am thap"

Format đầu ra (theo yêu cầu):
  Device: sensor01
  Temperature: 36.4
  Humidity: 38.9
  CANH BAO: Nhiet do cao
  CANH BAO: Do am thap
"""

import pika
import json


# ===== CẤU HÌNH =====
BROKER_HOST = "localhost"
BROKER_PORT = 5672
QUEUE_NAME  = "sensor_data_queue"

# Ngưỡng cảnh báo (theo yêu cầu bài)
TEMP_HIGH_THRESHOLD = 35   # °C
HUMID_LOW_THRESHOLD = 40   # %


def callback(ch, method, properties, body):
    """Xử lý từng tin nhắn cảm biến nhận được."""
    try:
        data = json.loads(body.decode("utf-8"))

        device_id   = data.get("device_id",   "N/A")
        temperature = data.get("temperature",  0)
        humidity    = data.get("humidity",     0)

        # In đúng format theo yêu cầu đầu ra
        print(f"Device: {device_id}")
        print(f"Temperature: {temperature}")
        print(f"Humidity: {humidity}")

        if temperature > TEMP_HIGH_THRESHOLD:
            print("CẢNH BÁO: Nhiệt độ cao")
        if humidity < HUMID_LOW_THRESHOLD:
            print("CẢNH BÁO: Độ ẩm thấp")

        print()  # dòng trống phân cách giữa các lần nhận

    except (json.JSONDecodeError, KeyError) as e:
        print(f"[Monitor] Lỗi khi phân tích payload: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    print(f"[Monitor] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=BROKER_HOST, port=BROKER_PORT)
    )
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[Monitor] Đang lắng nghe queue: '{QUEUE_NAME}'")
    print(f"[Monitor] Cảnh báo nhiệt độ: > {TEMP_HIGH_THRESHOLD} °C")
    print(f"[Monitor] Cảnh báo độ ẩm  : < {HUMID_LOW_THRESHOLD} %")
    print("[Monitor] Đang chờ dữ liệu... (Nhấn Ctrl+C để thoát)\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[Monitor] Dừng chương trình theo yêu cầu người dùng.")
        channel.stop_consuming()

    connection.close()
    print("[Monitor] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
