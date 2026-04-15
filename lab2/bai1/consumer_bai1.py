"""
Bài 1 - Chương trình 2: Consumer
Lắng nghe queue iot_lab_queue liên tục, in nội dung tin nhắn và thời điểm nhận.
Chạy liên tục cho tới khi dừng bằng Ctrl+C.
"""

import pika
from datetime import datetime


# ===== CẤU HÌNH BROKER =====
BROKER_HOST = "localhost"
BROKER_PORT = 5672
QUEUE_NAME  = "iot_lab_queue"


def callback(ch, method, properties, body):
    """Hàm xử lý khi nhận được tin nhắn."""
    now     = datetime.now().strftime("%H:%M:%S")
    message = body.decode("utf-8")

    print(f"Đã nhận message: {message}")
    print(f"Thời gian nhận: {now}")

    # Xác nhận đã xử lý xong (manual ACK)
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    # Kết nối tới RabbitMQ
    print(f"[Consumer] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=BROKER_HOST, port=BROKER_PORT)
    )
    channel = connection.channel()

    # Khai báo queue (idempotent)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Chỉ nhận 1 tin nhắn tại một thời điểm (fair dispatch)
    channel.basic_qos(prefetch_count=1)

    # Đăng ký callback
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[Consumer] Đang lắng nghe queue: '{QUEUE_NAME}'")
    print("[Consumer] Đang chờ nhận tin nhắn... (Nhấn Ctrl+C để thoát)\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[Consumer] Dừng chương trình theo yêu cầu người dùng.")
        channel.stop_consuming()

    connection.close()
    print("[Consumer] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
