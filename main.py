import os
import re
import time
import struct
import serial
import requests
import subprocess
import pvporcupine
import pyaudio
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont

# ---------------- CONFIG ----------------
ACCESS_KEY = "SsDZFHCVqlZSbaPcycaj/ig+gAqtnt2kyPGpCeX0kYYr8Efn7ncd2w=="
SERVER_URL = "http://localhost:5000"
WAKE_WORD_PATH = "/home/dietpi/downloads/wheels.ppn"

# Only for TTS playback
AUDIO_OUTPUT_DEVICE = "plughw:0,0" 

# ESP32 Settings
ESP_PORT = "/dev/serial0"
ESP_BAUD = 115200

# Keywords
vision_keywords = ["see", "picture", "photo", "camera", "look", "what is this"]
movement_keywords = ["move", "forward", "back", "left", "right", "stop"]

# ---------------- HARDWARE SETUP ----------------
try:
    esp = serial.Serial(ESP_PORT, ESP_BAUD, timeout=1)
    print(f"[INIT] ESP32 Connected on {ESP_PORT}")
except:
    esp = None
    print("[INIT] ESP32 NOT Connected")

try:
    serial_i2c = i2c(port=1, address=0x3C)
    device = ssd1306(serial_i2c)
    font = ImageFont.load_default()
    print("[INIT] OLED Connected")
except:
    device = None
    print("[INIT] OLED Error (Running without display)")

def draw_ui(header, text):
    if device is None: return
    with canvas(device) as draw:
        draw.rectangle((0, 0, 128, 12), fill="white")
        draw.text((2, 0), header.upper(), fill="black", font=font)
        draw.text((0, 14), text[:80], fill="white", font=font)

def speak(text):
    if not text: return
    try:
        r = requests.post(f"{SERVER_URL}/tts", json={"text": text})
        with open("resp.wav", "wb") as f: f.write(r.content)
        subprocess.run(["aplay", "-D", AUDIO_OUTPUT_DEVICE, "-q", "resp.wav"])
    except Exception as e:
        print(f"[TTS] Error: {e}")

# ---------------- HELPER: FIND MIC ----------------
def find_microphone_index(pa):
    """
    Scans for a device with input channels. 
    Prioritizes 'USB' devices if multiple exist.
    """
    count = pa.get_device_count()
    print(f"\n[AUDIO] Scanning {count} devices...")
    
    usb_index = None
    first_input_index = None

    for i in range(count):
        try:
            info = pa.get_device_info_by_index(i)
            name = info.get('name', 'Unknown')
            channels = info.get('maxInputChannels', 0)
            
            if channels > 0:
                print(f"  - Found Input: [{i}] {name}")
                if first_input_index is None:
                    first_input_index = i
                if "usb" in name.lower():
                    usb_index = i
        except:
            continue

    # Prefer USB mic, otherwise fallback to first input found
    best_index = usb_index if usb_index is not None else first_input_index
    
    if best_index is None:
        print("[AUDIO] CRITICAL: No microphone found!")
        return 0
        
    print(f"[AUDIO] Selected Device Index: {best_index}")
    return best_index

# ---------------- MAIN ----------------
def main():
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keyword_paths=[WAKE_WORD_PATH])
    pa = pyaudio.PyAudio()

    # AUTO-DETECT MICROPHONE
    mic_index = find_microphone_index(pa)

    try:
        stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=mic_index,
            frames_per_buffer=porcupine.frame_length
        )
    except OSError as e:
        print(f"\n[ERROR] Failed to open mic at index {mic_index}: {e}")
        print("Try running: python3 check_audio.py to see valid devices.")
        return

    draw_ui("READY", "Say Wheels")
    print("\n[SYSTEM] Listening for Wake Word...")

    while True:
        try:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            if porcupine.process(pcm) >= 0:
                print("\n[WAKE WORD DETECTED]")
                stream.stop_stream()
                stream.close()
                
                # --- RECORDING PHASE ---
                draw_ui("LISTENING", "Speak...")
                
                # NOTE: We use plughw:1,0 here. If your mic is not Card 1, 
                # this might need adjustment. But usually USB mics are Card 1.
                subprocess.run([
                    "arecord", "-D", "plughw:1,0", 
                    "-f", "cd", "-d", "4", "-r", "44100", 
                    "command.wav"
                ])
                
                # --- PROCESSING PHASE ---
                draw_ui("THINKING", "Processing...")
                
                user_text = ""
                try:
                    with open("command.wav", "rb") as f:
                        resp = requests.post(f"{SERVER_URL}/transcribe", files={"file": f})
                        user_text = resp.json().get("text", "")
                except Exception as e:
                    print(f"[STT] Error: {e}")

                print(f"[USER] {user_text}")
                draw_ui("YOU", user_text)

                # --- INTENT LOGIC ---
                ai_text = ""
                u_low = user_text.lower()
                
                if any(k in u_low for k in vision_keywords):
                    # Vision Path
                    draw_ui("VISION", "Looking...")
                    try:
                        resp = requests.post(f"{SERVER_URL}/vision", json={"question": user_text})
                        ai_text = resp.json().get("response", "")
                    except: 
                        ai_text = "Vision error."
                
                else:
                    # Chat/Move Path
                    try:
                        resp = requests.post(f"{SERVER_URL}/chat", json={"text": user_text})
                        ai_text = resp.json().get("response", "")
                    except: 
                        ai_text = "Chat error."

                # --- MOTOR CONTROL ---
                if "MOTOR:" in ai_text:
                    cmd = ai_text.split(":")[1].strip()
                    print(f"[MOTOR] Command: {cmd}")
                    if esp: 
                        esp.write((cmd + "\n").encode())
                    ai_text = "Moving."

                print(f"[AI] {ai_text}")
                draw_ui("AI", ai_text)
                speak(ai_text)
                
                # --- RESTART LISTENING ---
                stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    input_device_index=mic_index,
                    frames_per_buffer=porcupine.frame_length
                )
                draw_ui("READY", "Say Wheels")

        except KeyboardInterrupt:
            print("\nStopping...")
            break

if __name__ == "__main__":
    main()
