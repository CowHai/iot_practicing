"""
Bài 3 - Chương trình 3: Critical Consumer
Tạo queue 'critical_queue', bind với exchange 'iot_alert_exchange'
bằng routing key 'critical'.
Chỉ nhận các cảnh báo mức critical.

Ví dụ đầu ra:
  [critical_queue] Da nhan: Cam bien kho lang mat ket noi critical
"""

import pika


# ===== CẤU HÌNH =====
BROKER_HOST   = "localhost"
BROKER_PORT   = 5672
EXCHANGE_NAME = "iot_alert_exchange"
QUEUE_NAME    = "critical_queue"
ROUTING_KEY   = "critical"


def callback(ch, method, properties, body):
    message = body.decode("utf-8")
    print(f"[{QUEUE_NAME}] Đã nhận: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    print(f"[CriticalConsumer] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=BROKER_HOST, port=BROKER_PORT)
    )
    channel = connection.channel()

    # Khai báo Direct Exchange (phải khớp với Producer)
    channel.exchange_declare(
        exchange=EXCHANGE_NAME,
        exchange_type="direct",
        durable=True,
    )

    # Khai báo queue có tên cố định (durable)
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Bind queue vào exchange với routing key 'critical'
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY,
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[CriticalConsumer] Exchange : '{EXCHANGE_NAME}' (direct)")
    print(f"[CriticalConsumer] Queue    : '{QUEUE_NAME}'")
    print(f"[CriticalConsumer] Routing  : '{ROUTING_KEY}'")
    print("[CriticalConsumer] Chỉ nhận cảnh báo mức CRITICAL. (Ctrl+C để thoát)\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[CriticalConsumer] Dừng chương trình theo yêu cầu người dùng.")
        channel.stop_consuming()

    connection.close()
    print("[CriticalConsumer] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
