import argparse
import serial
import time
import joblib
import numpy as np
import pandas as pd
import requests
from collections import deque
import os

buffer     = deque(maxlen=10)
PORT       = "COM7"
FLASK_URL  = "http://127.0.0.1:5000/hardware_ingest"
BAUD       = 9600

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join("ml", "gesture_model.pkl")

FEATURE_COLS = [
    "flex_index", "flex_middle", "flex_ring",
    "accel_x", "accel_y", "accel_z",
    "gyro_x", "gyro_y"
]

def parse_line(raw):
    try:
        parts = raw.split(",")
        data  = {}
        for p in parts:
            key, val = p.split(":")
            data[key.strip()] = int(val.strip())

        index  = data["F4"]
        middle = data["F3"]
        ring   = data["F2"]

        feature_values = [
            index, middle, ring,
            data["AX"], data["AY"], data["AZ"],
            data["GX"], data["GY"]
        ]
        return pd.DataFrame([feature_values], columns=FEATURE_COLS), data
    except Exception:
        return None, None

def run(port, language, user_id):
    print(f" Connecting to ESP32 on {port}...")
    ser = serial.Serial(port, BAUD, timeout=2)
    time.sleep(2)

    print(" Loading model...")
    model = joblib.load(MODEL_PATH)

    print(f"\n STARTED REAL-TIME PREDICTION  (user_id={user_id})\n")

    while True:
        raw = ser.readline().decode(errors="ignore").strip()
        if not raw:
            continue

        features, raw_data = parse_line(raw)
        if features is None:
            continue

        probs      = model.predict_proba(features)[0]
        pred       = model.classes_[np.argmax(probs)]
        confidence = float(np.max(probs))

        buffer.append(pred)
        final_pred = max(set(buffer), key=buffer.count)

        print(f"\r🖐️  Gesture: {final_pred} | Confidence: {confidence:.2f}   ", end="")

        try:
            payload = {
                "F1": 4095,
                "F2": int(features["flex_ring"][0]),
                "F3": int(features["flex_middle"][0]),
                "F4": int(features["flex_index"][0]),
                "AX": int(features["accel_x"][0]),
                "AY": int(features["accel_y"][0]),
                "AZ": int(features["accel_z"][0]),
                "GX": int(features["gyro_x"][0]),
                "GY": int(features["gyro_y"][0]),
                "GZ": 0,
                "language": language,
                "user_id": user_id,   # ← FIX: send user_id so Flask can save history
            }
            requests.post(FLASK_URL, json=payload, timeout=0.2)
        except Exception:
            pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ESP32 serial → Flask bridge")
    parser.add_argument("--port",     default="COM7",    help="Serial port (e.g. COM7 or /dev/ttyUSB0)")
    parser.add_argument("--language", default="English", choices=["English", "Hindi", "Marathi"])
    parser.add_argument("--user_id",  type=int, default=1, help="Your SignGlove user ID (shown in profile)")
    args = parser.parse_args()
    run(args.port, args.language, args.user_id)
