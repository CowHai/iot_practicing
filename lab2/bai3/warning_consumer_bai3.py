"""
Bài 3 - Chương trình 2: Warning Consumer
Tạo queue 'warning_queue', bind với exchange 'iot_alert_exchange'
bằng routing key 'warning'.
Chỉ nhận các cảnh báo mức warning.

Ví dụ đầu ra:
  [warning_queue] Da nhan: Nhiet do phong may chuot muc warning
"""

import pika


# ===== CẤU HÌNH =====
BROKER_HOST   = "localhost"
BROKER_PORT   = 5672
EXCHANGE_NAME = "iot_alert_exchange"
QUEUE_NAME    = "warning_queue"
ROUTING_KEY   = "warning"


def callback(ch, method, properties, body):
    message = body.decode("utf-8")
    print(f"[{QUEUE_NAME}] Đã nhận: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    print(f"[WarningConsumer] Đang kết nối tới RabbitMQ: {BROKER_HOST}:{BROKER_PORT} ...")
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

    # Bind queue vào exchange với routing key 'warning'
    channel.queue_bind(
        exchange=EXCHANGE_NAME,
        queue=QUEUE_NAME,
        routing_key=ROUTING_KEY,
    )

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

    print(f"[WarningConsumer] Exchange : '{EXCHANGE_NAME}' (direct)")
    print(f"[WarningConsumer] Queue    : '{QUEUE_NAME}'")
    print(f"[WarningConsumer] Routing  : '{ROUTING_KEY}'")
    print("[WarningConsumer] Chỉ nhận cảnh báo mức WARNING. (Ctrl+C để thoát)\n")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[WarningConsumer] Dừng chương trình theo yêu cầu người dùng.")
        channel.stop_consuming()

    connection.close()
    print("[WarningConsumer] Đã ngắt kết nối.")


if __name__ == "__main__":
    main()
