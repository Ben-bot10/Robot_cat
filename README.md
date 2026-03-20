Project Mechano 🐱
An Edge-AI Powered Robot Companion

Project Mechano is an autonomous, fully offline robot inspired by the classic 1950s Tom & Jerry robot cat. It combines LLMs, computer vision, and voice recognition to create a robot that can see, hear, speak, and move—all without an internet connection.

The system uses a Raspberry Pi 4 as the "brain" for heavy AI processing, and an ESP32 as the "nervous system" for real-time motor and servo control.

Features
100% Offline AI: Privacy-first architecture running entirely on the edge.
Wake Word Detection: Always-listening capabilities using Porcupine (Trigger: "Wheels").
Local STT & TTS: Transcribes audio using Faster-Whisper and speaks natively using Piper TTS.
Computer Vision: Captures images and describes its environment using the moondream vision model via Ollama.
Conversational AI: Engages in fast, short-form chat using the qwen:0.5b local model.
Animatronic Ears: Reactive SG90 servos that twitch, droop, and go "alert" based on the robot's current state and idle behavior.
Oled display: To display the status of the robot.

Things I have used,
<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/321bef11-c908-4153-9996-454fb42dd01a" />
<img width="775" height="1024" alt="image" src="https://github.com/user-attachments/assets/d6ee7a47-fdb8-4e2b-9c7f-4a3bc50e4bac" />

https://github.com/user-attachments/assets/e37eb65b-6d02-4702-95b4-9ca1620c0eaa




Hardware Interfacing: Robust UART communication between the Pi and ESP32 with deterministic motor control via a TB6612FNG driver.


Hardware Bill of Materials (BOM)
Brain: Raspberry Pi 4 Model B (Running DietPi)
Sub-controller: ESP32 Development Board
Motor Driver: TB6612FNG
Actuators: 2x DC Gear Motors, 2x Tower Pro SG90 Micro Servos
Audio: USB Microphone, 3.5mm Speaker
Power: 6x AA Battery Pack (Motors/Servos), separate power supply for the RPi.
Software Stack
OS: DietPi (Aarch64)
Backend: Python 3, Flask, PyAudio
AI/Models: Ollama(ahmadwaqar/smolvlm), Whisper (tiny.en), Piper
Firmware: C++ (Arduino Framework for ESP32)

Installation & Setup
1. Raspberry Pi Setup (The Brain)
Install the required system packages:

sudo apt update
sudo apt install fswebcam alsa-utils
sudo usermod -a -G video dietpi

Install and configure Ollama, then pull the required models:
Set up the Python environment:
python3 -m venv .venv
source .venv/bin/activate
pip install flask faster-whisper pvporcupine pyaudio pyserial luma.oled luma.core requests

Use the wiring accordingly to the code.
Flash the Arduino codeto esp.

Usage
run the ollama model in a terminal.
Start the Flask backend server:
python backend.py
In a new terminal, start the main interaction loop:
python main.py

Commands to try:

"Wheels... move forward." (Robot moves, ears go alert).

"Wheels... take a picture." (Camera clicks, robot describes the scene).

"Wheels... what is quantum physics?" (Robot responds using the local text LLM).
