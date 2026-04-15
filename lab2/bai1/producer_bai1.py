"""
Bài 1 - Chương trình 1: Producer
Kết nối tới RabbitMQ và gửi tin nhắn vào queue iot_lab_queue.
"""

import pika

# ===== CẤU HÌNH BROKER =====
BROKER_HOST = "localhost"
BROKER_PORT = 5672
QUEUE_NAME  = "iot_lab_queue"

# ===== THÔNG TIN SINH VIÊN =====
HO_TEN      = "Cao Duy Hải"
MA_SINH_VIEN = "B20DCCN218"
NOI_DUNG    = "Xin chào từ ứng dụng Python AMQP"


def main():
    # Kết nối tới RabbitMQ
    print(f"[Producer] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=BROKER_HOST, port=BROKER_PORT)
    )
    channel = connection.channel()

    # Khai báo queue (idempotent — an toàn khi queue đã tồn tại)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)
    print(f"[Producer] Đã khai báo queue: '{QUEUE_NAME}'")

    # Tạo payload
    payload = f"{NOI_DUNG} - {MA_SINH_VIEN} - {HO_TEN}"

    # Gửi nhiều thông điệp liên tiếp
    for i in range(1, 4):
        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=2,  # persistent — tin nhắn không mất khi RabbitMQ restart
            ),
        )
        print(f"\n[Producer] Đã gửi tin nhắn lần {i}:")
        print(f"  Queue  : {QUEUE_NAME}")
        print(f"  Payload: {payload}")

    connection.close()
    print("\n[Producer] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
