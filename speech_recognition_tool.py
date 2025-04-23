import os
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio

def recognize_speech_from_mic(language="zh-CN"):
    # Download Voice Model Data from https://alphacephei.com/vosk/models
    # And set model path based on language
    model_paths = {
        "zh-CN": r"D:\IdeaWorkSpaces\RogerLYJ\vosk-model-cn-0.22",
        # "zh-CN": r"D:\IdeaWorkSpaces\RogerLYJ\vosk-model-small-cn-10.22",
        "en-US": r"D:\IdeaWorkSpaces\RogerLYJ\vosk-model-small-en-us-0.15"
    }
    model_path = model_paths.get(language)
    if not model_path or not os.path.exists(model_path):
        print(f"Model for {language} not found. Please download and extract the model to:", model_path)
        return

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    # Initialize microphone input
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    print(f"Listening for speech in {language}... Speak into the microphone.")
    exit_phrases = {
        "zh-CN": "确认退出",
        "en-US": "exit"
    }
    exit_phrase = exit_phrases.get(language, "exit")
    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "").replace(" ", "").strip()  # Remove spaces for exact match
                print("You said:", text)
                if text == exit_phrase:
                    print("Exit phrase detected. Exiting...")
                    break
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    print("请选择语言 / Please select a language:")
    print("1. 中文 (Chinese)")
    print("2. English")
    choice = input("输入选项 / Enter your choice (1 or 2): ").strip()

    if choice == "1":
        recognize_speech_from_mic(language="zh-CN")
    elif choice == "2":
        recognize_speech_from_mic(language="en-US")
    else:
        print("无效选项 / Invalid choice. Exiting...")
