import csv
import time
import serial as pyserial
import threading
import os

PORT = "COM7"
BAUD = 9600
OUTPUT_FILE = "gesture_dataset.csv"

TARGET_SAMPLES = 300
stop_flag = False


# 🔹 READ DATA FROM ESP32 (YOUR FORMAT)
def read_valid_line(ser):
    while True:
        raw = ser.readline().decode(errors="ignore").strip()

        if not raw:
            continue

        try:
            parts = raw.split(",")

            data = {}
            for p in parts:
                key, val = p.split(":")
                data[key.strip()] = int(val.strip())

            return {
                "flex": [data["F1"], data["F2"], data["F3"], data["F4"]],
                "acc": [data["AX"], data["AY"], data["AZ"]],
                "gyro": [data["GX"], data["GY"], data["GZ"]],
            }

        except:
            continue


# 🔹 LISTEN FOR STOP COMMAND
def listen_stop():
    global stop_flag
    while True:
        cmd = input().lower()
        if cmd == "e":
            stop_flag = True
            break


def main():
    global stop_flag

    print(" Connecting to ESP32...")
    ser = pyserial.Serial(PORT, BAUD, timeout=2)
    time.sleep(2)

    # 🔹 GET LABEL
    LABEL = input("\n Enter gesture label: ").strip().lower()

    print("\n CONTROL:")
    print("Type 's' + ENTER → START")
    print("Type 'e' + ENTER → STOP anytime\n")

    cmd = input(" Enter command: ").lower()

    if cmd != "s":
        print(" Not started")
        return

    print("\n Recording started...")
    print(" Perform the gesture and keep it steady")
    print(" Type 'e' anytime to stop\n")

    # start stop listener thread
    threading.Thread(target=listen_stop, daemon=True).start()

    file_exists = os.path.exists(OUTPUT_FILE)

    with open(OUTPUT_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        # write header only once
        if not file_exists:
            writer.writerow([
                "flex_index",
                "flex_middle",
                "flex_ring",
                "accel_x",
                "accel_y",
                "accel_z",
                "gyro_x",
                "gyro_y",
                "label"
            ])

        count = 0

        while count < TARGET_SAMPLES and not stop_flag:
            data = read_valid_line(ser)

            flex = data["flex"]
            acc = data["acc"]
            gyro = data["gyro"]

            #  ignore broken flex1
            index = flex[3]
            middle = flex[2]
            ring = flex[1]

            row = [
                index,
                middle,
                ring,
                acc[0],
                acc[1],
                acc[2],
                gyro[0],
                gyro[1],
                LABEL
            ]

            writer.writerow(row)
            count += 1

            #  LIVE DASHBOARD
            print(
                f"\r {LABEL.upper()} → {count}/{TARGET_SAMPLES} | "
                f"Index:{index} Mid:{middle} Ring:{ring}",
                end=""
            )

    ser.close()

    print("\n\n🎉 DONE! Data saved in gesture_dataset.csv")


if __name__ == "__main__":
    main()