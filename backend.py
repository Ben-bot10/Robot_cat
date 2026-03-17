import os
import subprocess
import uuid
import requests
import base64  # <--- REQUIRED for Vision
from flask import Flask, request, jsonify, send_file
from faster_whisper import WhisperModel

app = Flask(__name__)

ASR_MODEL_SIZE = "tiny.en"
PIPER_BINARY = "/home/dietpi/piper/piper/piper"
VOICE_MODEL = "/home/dietpi/piper/voice.onnx"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Keep your custom vision model
MODEL_NAME = "smolbot"

print("Loading Whisper...")
asr_model = WhisperModel(ASR_MODEL_SIZE, device="cpu", compute_type="int8")
print("Whisper Ready")

# ---------------- TRANSCRIBE ----------------
@app.route('/transcribe', methods=['POST'])
def transcribe():
    temp_file = f"/tmp/asr_{uuid.uuid4()}.wav"
    request.files['file'].save(temp_file)
    try:
        segments, _ = asr_model.transcribe(temp_file, beam_size=1)
        text = " ".join([s.text for s in segments]).strip()
        return jsonify({"text": text})
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

# ---------------- TTS ----------------
@app.route('/tts', methods=['POST'])
def tts():
    text = request.json.get("text", "")
    if not text: return "Empty", 400
    output_file = f"/tmp/tts_{uuid.uuid4()}.wav"
    cmd = (f'echo "{text}" | {PIPER_BINARY} '
           f'--model {VOICE_MODEL} --length_scale 0.9 --noise_scale 0.6 '
           f'--output_file {output_file}')
    subprocess.run(cmd, shell=True)
    return send_file(output_file, mimetype="audio/wav")

# ---------------- CHAT ----------------
@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json.get("text", "").lower()

    # Deterministic Movement Guardrails
    if "forward" in user_text: return jsonify({"response": "MOTOR:forward"})
    if "back" in user_text:    return jsonify({"response": "MOTOR:back"})
    if "left" in user_text:    return jsonify({"response": "MOTOR:left"})
    if "right" in user_text:   return jsonify({"response": "MOTOR:right"})
    if "stop" in user_text:    return jsonify({"response": "MOTOR:stop"})

    # Standard Chat
    system_prompt = "You are a robot assistant. Keep answers short (max 10 words)."
    payload = {
        "model": MODEL_NAME,
        "prompt": system_prompt + f"\nUser: {user_text}\nAssistant:",
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 30}
    }
    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=60)
        return jsonify({"response": res.json().get("response", "").strip()})
    except:
        return jsonify({"response": "I am offline."})

# ---------------- VISION (FIXED) ----------------
@app.route('/vision', methods=['POST'])
def vision():
    question = request.json.get("question", "")
    image_path = "/tmp/capture.jpg"

    # 1. Capture Image
    os.system(f"fswebcam -r 320x240 --no-banner {image_path}")

    # 2. Encode Image to Base64 (Crucial Fix)
    try:
        with open(image_path, "rb") as img:
            # Ollama requires Base64 strings, NOT Hex
            image_b64 = base64.b64encode(img.read()).decode('utf-8')
    except FileNotFoundError:
        return jsonify({"response": "Camera error."})

    # 3. Handle Keywords
    prompt = question
    short_triggers = ["photo", "picture", "image", "see", "look", "capture"]
    if any(t in question.lower() for t in short_triggers):
        prompt = "Describe this image."

    # 4. Send to Ollama
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "images": [image_b64], # <--- Sending corrected Base64
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 40}
    }

    try:
        res = requests.post(OLLAMA_URL, json=payload, timeout=120)
        reply = res.json().get("response", "").strip()
        if not reply: reply = "I see it, but I have no words."
        return jsonify({"response": reply})
    except Exception as e:
        print(f"Vision Error: {e}")
        return jsonify({"response": "Vision error."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
