import argparse
import json
import time
import requests
from collections import deque

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("pyserial not found. Run: pip install pyserial")
    raise

FLASK_URL  = "http://127.0.0.1:5000/hardware_ingest"
BAUD_RATE  = 9600

FLEX_MIN   = [1200, 1200, 1200, 1200]
FLEX_MAX   = [3000, 3000, 3000, 3000]
ACC_SCALE  = 16384.0
GYRO_SCALE = 131.0

recent_preds = deque(maxlen=3)

def list_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No serial ports found.")
    else:
        print("Available ports:")
        for p in ports:
            print(f"  {p.device} - {p.description}")

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def normalize_flex(raw, min_v, max_v):
    if max_v == min_v:
        return 0.0
    x = (raw - min_v) / (max_v - min_v)
    return round(clamp(x, 0.0, 1.0), 4)

def parse_json_line(line: str):
    try:
        obj  = json.loads(line.strip())
        flex = obj.get("flex", [])
        acc  = obj.get("acc", [])
        gyro = obj.get("gyro", [])

        if len(flex) != 4 or len(acc) != 3 or len(gyro) != 3:
            return None

        return {
            "flex_thumb":      normalize_flex(flex[0], FLEX_MIN[0], FLEX_MAX[0]),
            "flex_index":      normalize_flex(flex[1], FLEX_MIN[1], FLEX_MAX[1]),
            "flex_middle":     normalize_flex(flex[2], FLEX_MIN[2], FLEX_MAX[2]),
            "flex_ring_pinky": normalize_flex(flex[3], FLEX_MIN[3], FLEX_MAX[3]),
            "accel_x":         round(acc[0]  / ACC_SCALE,  4),
            "accel_y":         round(acc[1]  / ACC_SCALE,  4),
            "accel_z":         round(acc[2]  / ACC_SCALE,  4),
            "gyro_x":          round(gyro[0] / GYRO_SCALE, 4),
            "gyro_y":          round(gyro[1] / GYRO_SCALE, 4),
        }
    except Exception:
        return None

def run(port: str, language: str, user_id: int):
    print(f"Connecting to {port} @ {BAUD_RATE} baud...")
    ser = serial.Serial(port, BAUD_RATE, timeout=2)
    time.sleep(2)
    print(f"Connected. Listening for glove data... (user_id={user_id})\n")

    while True:
        try:
            raw = ser.readline().decode("utf-8", errors="ignore").strip()
            if not raw:
                continue

            payload = parse_json_line(raw)
            if payload is None:
                print(f"[skip] {raw}")
                continue

            payload["language"] = language
            payload["user_id"]  = user_id   # ← FIX: send so Flask can save history

            resp = requests.post(FLASK_URL, json=payload, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("duplicate"):
                    continue
                recent_preds.append(data["text"])
                stable_text = max(set(recent_preds), key=recent_preds.count)
                print(
                    f"[{time.strftime('%H:%M:%S')}] "
                    f"text={stable_text} "
                    f"conf={data['confidence']:.2f} "
                    f"rt={data['response_time']*1000:.1f}ms"
                )
            else:
                print(f"[error] HTTP {resp.status_code}: {resp.text[:150]}")

        except serial.SerialException as e:
            print(f"[serial error] {e}")
            break
        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"[runtime error] {e}")

    ser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HC-05 sign glove bridge")
    parser.add_argument("--port",     default="COM7",    help="Bluetooth COM port")
    parser.add_argument("--language", default="English", choices=["English", "Hindi", "Marathi"])
    parser.add_argument("--user_id",  type=int, required=True,
                        help="Your SignGlove user ID (find it in your profile page)")
    parser.add_argument("--list",     action="store_true", help="List available serial ports")
    args = parser.parse_args()

    if args.list:
        list_ports()
    else:
        run(args.port, args.language, args.user_id)
