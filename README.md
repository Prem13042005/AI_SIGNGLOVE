# SignGlove – AI-Based Indian Sign Language to Speech Translation

## Overview

SignGlove is an AI-powered wearable communication system designed to help bridge communication gaps for hearing and speech-impaired individuals.

The system captures hand gestures using sensors mounted on a smart glove, processes them using Machine Learning, and converts them into real-time text and speech through a web application.

This project combines Artificial Intelligence, Internet of Things (IoT), and Web Technologies into a complete assistive communication platform.

---

## Features

* Real-Time Gesture Recognition
* Sign-to-Text Translation
* Text-to-Speech Conversion
* Sentence Builder
* User Authentication
* Translation History
* Analytics Dashboard
* Multilingual Support
* Bluetooth-Based Communication
* Smart Wearable Integration

---

## System Architecture

Smart Glove
(Flex Sensors + MPU6050)

↓

ESP32 Microcontroller

↓

Bluetooth Communication

↓

Machine Learning Prediction Engine

↓

Flask Backend

↓

SQLite Database

↓

Web Dashboard

↓

Text + Speech Output

---

## Technology Stack

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Flask

### Database

* SQLite

### Machine Learning

* Python
* Scikit-Learn
* Random Forest

### Hardware

* ESP32
* Flex Sensors
* MPU6050

### Communication

* Bluetooth Serial

---

## Machine Learning Details

Model:
Random Forest Classifier

Dataset:
Custom dataset collected using sensor readings.

Training:
Approximately 300 samples collected per gesture.

Accuracy:
95.5%

---

## Project Structure

```plaintext
SIGNGLOVE/
│
├── app.py
├── predictor.py
├── serial_bridge.py
├── requirements.txt
├── Procfile
├── templates/
├── static/
├── ml/
├── gesture_model.pkl
└── README.md
```

---

## Installation

Clone repository:

```bash
git clone YOUR_GITHUB_REPO
cd SIGNGLOVE
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
python app.py
```

Open:

```plaintext
http://127.0.0.1:5000
```

---

## Future Scope

* Cloud Deployment
* Mobile Application
* Expanded Gesture Vocabulary
* Regional Language Support
* Continuous Learning AI
* Real-Time Remote Communication

---

## Team

Prem Rajput
Omkar Mane
Diksha Mohite

Project Guide:
Prof. Dipali Ghatge

---

## License

Academic and portfolio use.
