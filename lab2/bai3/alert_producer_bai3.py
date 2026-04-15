"""
Bài 3 - Chương trình 1: Alert Producer
Tạo một direct exchange tên 'iot_alert_exchange' và gửi cảnh báo
với các routing key tương ứng: info, warning, critical.

Khi producer gửi 3 message:
  - info    : không consumer nào nhận (không ai bind routing key 'info')
  - warning : chỉ warning_queue nhận
  - critical: chỉ critical_queue nhận
"""

import pika
import time


# ===== CẤU HÌNH =====
BROKER_HOST   = "localhost"
BROKER_PORT   = 5672
EXCHANGE_NAME = "iot_alert_exchange"
EXCHANGE_TYPE = "direct"   # Direct exchange — định tuyến theo routing key

# Danh sách cảnh báo mẫu (routing_key, nội dung)
ALERTS = [
    ("info",     "Hệ thống khởi động thành công mức info"),
    ("warning",  "Nhiệt độ phòng máy vượt mức warning"),
    ("critical", "Cảm biến kho lạnh mất kết nối critical"),
]


def main():
    print(f"[AlertProducer] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=BROKER_HOST, port=BROKER_PORT)
    )
    channel = connection.channel()

    # Khai báo Direct Exchange (idempotent)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type=EXCHANGE_TYPE,
        durable=True,
    )
    print(f"[AlertProducer] Exchange '{EXCHANGE_NAME}' (type: {EXCHANGE_TYPE}) đã sẵn sàng.\n")

    # Gửi từng cảnh báo với routing key tương ứng
    for routing_key, message in ALERTS:
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2),
        )
        print(f"[AlertProducer] Đã gửi → routing_key='{routing_key}' | message: '{message}'")
        time.sleep(1)

    connection.close()
    print("\n[AlertProducer] Hoàn tất. Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
