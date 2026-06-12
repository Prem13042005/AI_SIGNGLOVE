import os
import joblib
import pandas as pd

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join("ml", "gesture_model.pkl")

CONFIDENCE_THRESHOLD = 0.50   

FEATURE_COLS = [
    "flex_index",
    "flex_middle",
    "flex_ring",
    "accel_x",
    "accel_y",
    "accel_z",
    "gyro_x",
    "gyro_y"
]

class GesturePredictor:
    def __init__(self):
        self.model = joblib.load(MODEL_PATH)

    def predict(self, features, language="English"):
        df   = pd.DataFrame([features], columns=FEATURE_COLS)
        pred = self.model.predict(df)[0]
        conf = float(max(self.model.predict_proba(df)[0]))

        if conf < CONFIDENCE_THRESHOLD:
            return "Unknown", conf

        return pred, conf
