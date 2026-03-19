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
![download](https://github.com/user-attachments/assets/b6c66f45-2397-4a52-a603-5f98ede0289f)
![download (1)](https://github.com/user-attachments/assets/36137162-52c8-4e04-8e1b-9a380449e1ea)
![download (2)](https://github.com/user-attachments/assets/9d97f862-6994-4bca-9090-921ccb3f2471)
![download (3)](https://github.com/user-attachments/assets/ac284b0f-e57e-4ad2-80a5-a32986e728c3)
![download (4)](https://github.com/user-attachments/assets/19fd02d4-bc17-4976-b567-8b00e29fe90e)
![download (5)](https://github.com/user-attachments/assets/e4eef0ed-01ea-4034-af87-a04b8fd8858a)
![download (6)](https://github.com/user-attachments/assets/32f80ae8-4375-4f78-8790-074c95e91e7a)
![download (7)](https://github.com/user-attachments/assets/a0425910-f452-42b0-85f6-1dc8878338f8)
![download (8)](https://github.com/user-attachments/assets/569f47e3-0c90-4454-8f7b-63ac13d600bf)

Hardware Interfacing: Robust UART communication between the Pi and ESP32 with deterministic motor control via a TB6612FNG driver.
![IMG-20260219-WA0002](https://github.com/user-attachments/assets/0a5ca344-cbc9-4fcb-893b-2f8fec2f86dc)

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
