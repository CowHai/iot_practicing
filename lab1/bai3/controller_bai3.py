"""
Bài 3 - Chương trình 2: Multi-Device Controller App
Ứng dụng điều khiển NHIỀU thiết bị IoT (light01, fan01, pump01):
  - Subscribe wildcard topic iot/lab/+/status để nhận trạng thái tất cả thiết bị.
  - Nhập lệnh theo định dạng: <device_id> <ON|OFF>
    Ví dụ: "light01 ON", "fan01 OFF", "pump01 ON"
  - Gõ "STATUS" để xem trạng thái tất cả thiết bị.
  - Gõ "EXIT" để thoát chương trình.
  - Lệnh sai sẽ in thông báo lỗi rõ ràng.
"""

import paho.mqtt.client as mqtt
import json
import threading
import time


# ===== CẤU HÌNH =====
BROKER_HOST = "broker.hivemq.com"
BROKER_PORT  = 1883

# Danh sách thiết bị hợp lệ và icon hiển thị
DEVICES = {
    "light01": {"label": "Đèn",     "icon": "💡"},
    "fan01"  : {"label": "Quạt",    "icon": "🌀"},
    "pump01" : {"label": "Máy bơm", "icon": "💧"},
}

# Wildcard: nhận trạng thái từ tất cả thiết bị
TOPIC_STATUS_WILDCARD = "iot/lab/+/status"

connected = False

# Cache trạng thái nhận được từ các thiết bị
known_states: dict[str, str] = {}


# ===== HELPERS =====

def topic_cmd(device_id: str) -> str:
    return f"iot/lab/{device_id}/cmd"


def print_help() -> None:
    print("\n┌─────────────────────────────────────────────────────┐")
    print("│            HƯỚNG DẪN SỬ DỤNG CONTROLLER           │")
    print("├─────────────────────────────────────────────────────┤")
    print("│  Cú pháp: <device_id> <ON|OFF>                     │")
    print("│  Ví dụ  : light01 ON   fan01 OFF   pump01 ON       │")
    print("│                                                     │")
    print("│  Lệnh đặc biệt:                                     │")
    print("│    STATUS  — xem trạng thái hiện tại tất cả TB     │")
    print("│    HELP    — hiển thị hướng dẫn này                │")
    print("│    EXIT    — thoát chương trình                     │")
    print("├─────────────────────────────────────────────────────┤")
    print("│  Thiết bị hợp lệ:                                   │")
    for dev_id, info in DEVICES.items():
        print(f"│    {info['icon']}  {dev_id:<10} ({info['label']})               │")
    print("└─────────────────────────────────────────────────────┘\n")


def print_status_all() -> None:
    print("\n  ╔══════════════════════════════════╗")
    print("  ║     TRẠNG THÁI CÁC THIẾT BỊ     ║")
    print("  ╠══════════════════════════════════╣")
    for dev_id, info in DEVICES.items():
        state = known_states.get(dev_id, "?")
        icon  = "🟢" if state == "ON" else ("⭕" if state == "OFF" else "❓")
        print(f"  ║  {info['icon']} {dev_id:<10} : {icon} {state:<7}          ║")
    print("  ╚══════════════════════════════════╝\n")


# ===== MQTT CALLBACKS =====

def on_connect(client, userdata, flags, rc, properties=None):
    global connected
    if rc == 0:
        connected = True
        print(f"[Controller] Kết nối thành công tới Broker: {BROKER_HOST}:{BROKER_PORT}")
        client.subscribe(TOPIC_STATUS_WILDCARD, qos=1)
        print(f"[Controller] Đã đăng ký nhận trạng thái (wildcard): {TOPIC_STATUS_WILDCARD}")
    else:
        print(f"[Controller] Kết nối thất bại, mã lỗi: {rc}")


def on_message(client, userdata, msg):
    """Nhận trạng thái từ topic iot/lab/<device_id>/status."""
    try:
        data = json.loads(msg.payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return

    device_id = data.get("device_id", "")
    state     = data.get("state", "")

    # Chỉ hiển thị thiết bị trong danh sách quản lý
    if device_id not in DEVICES or not state:
        return

    # Lưu vào cache
    known_states[device_id] = state

    info = DEVICES[device_id]
    icon = "🟢" if state == "ON" else "⭕"
    print(f"\n  ← [Status] {info['icon']} {device_id} ({info['label']}): {icon} {state}")
    print("  Nhập lệnh: ", end="", flush=True)



def on_disconnect(client, userdata, flags, rc, properties=None):
    global connected
    connected = False
    print("[Controller] Đã ngắt kết nối.")


# ===== INPUT LOOP =====

def input_loop(client: mqtt.Client) -> None:
    """Vòng lặp nhận lệnh từ người dùng."""
    print_help()

    while True:
        try:
            raw = input("  Nhập lệnh: ").strip()
        except (EOFError, KeyboardInterrupt):
            raw = "EXIT"

        parts = raw.upper().split()

        # --- Lệnh đặc biệt (1 từ) ---
        if len(parts) == 1:
            cmd = parts[0]

            if cmd == "EXIT":
                print("[Controller] Thoát chương trình.")
                client.disconnect()
                break

            elif cmd == "STATUS":
                print_status_all()

            elif cmd == "HELP":
                print_help()

            elif cmd == "":
                pass  # bỏ qua dòng trống

            else:
                print(f"  ❌ Lệnh không hợp lệ: '{raw}'")
                print("     Cú pháp đúng: <device_id> <ON|OFF>  hoặc  STATUS / HELP / EXIT")

        # --- Lệnh điều khiển thiết bị: <device_id> <ON|OFF> ---
        elif len(parts) == 2:
            device_id, command = parts[0].lower(), parts[1]

            # Kiểm tra device_id
            if device_id not in DEVICES:
                valid = ", ".join(DEVICES.keys())
                print(f"  ❌ Thiết bị không tồn tại: '{device_id}'")
                print(f"     Thiết bị hợp lệ: {valid}")
                continue

            # Kiểm tra lệnh
            if command not in ("ON", "OFF"):
                print(f"  ❌ Lệnh không hợp lệ: '{command}'. Chỉ nhập 'ON' hoặc 'OFF'.")
                continue

            # Gửi lệnh
            topic = topic_cmd(device_id)
            client.publish(topic, command, qos=1)
            info = DEVICES[device_id]
            print(f"  → Đã gửi lệnh [{command}] tới {info['icon']} {device_id} ({info['label']})")

        else:
            print(f"  ❌ Lệnh không hợp lệ: '{raw}'")
            print("     Cú pháp đúng: <device_id> <ON|OFF>   Ví dụ: light01 ON")


# ===== MAIN =====

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    print("[Controller] Khởi động ứng dụng điều khiển IoT...")
    print(f"[Controller] Đang kết nối tới {BROKER_HOST}:{BROKER_PORT} ...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    # Chờ kết nối thành công
    timeout = 10
    while not connected and timeout > 0:
        time.sleep(0.5)
        timeout -= 0.5

    if not connected:
        print("[Controller] Không thể kết nối tới broker. Thoát.")
        client.loop_stop()
        return

    # Chạy vòng nhập lệnh ở thread riêng
    input_thread = threading.Thread(target=input_loop, args=(client,), daemon=True)
    input_thread.start()
    try:
        input_thread.join()
    except KeyboardInterrupt:
        pass 

    try:
        client.loop_stop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
