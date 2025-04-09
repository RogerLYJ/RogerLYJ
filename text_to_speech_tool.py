import pyttsx3

def text_to_speech(text, language="zh-CN", rate=200, pitch=50):
    engine = pyttsx3.init()
    
    # Set language-specific voice
    voices = engine.getProperty('voices')
    if language == "zh-CN":
        voice = next((v for v in voices if "zh" in v.languages or "Chinese" in v.name), None)
    elif language == "en-US":
        voice = next((v for v in voices if "en" in v.languages or "English" in v.name), None)
    else:
        voice = None

    if voice:
        engine.setProperty('voice', voice.id)
    else:
        print(f"No suitable voice found for language: {language}. Using default voice.")

    # Set speech rate
    engine.setProperty('rate', rate)

    # Set pitch (if supported by the TTS engine)
    try:
        engine.setProperty('pitch', pitch)
    except Exception:
        print("Pitch adjustment is not supported on this system.")

    # Speak the text
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    print("请选择语言 / Please select a language:")
    print("1. 中文 (Chinese)")
    print("2. English")
    choice = input("输入选项 / Enter your choice (1 or 2): ").strip()

    if choice == "1":
        language = "zh-CN"
    elif choice == "2":
        language = "en-US"
    else:
        print("无效选项 / Invalid choice. Exiting...")
        exit()

    text = input("请输入要转换为语音的文字 / Enter the text to convert to speech: ").strip()
    rate = int(input("请输入语速 (默认 200) / Enter speech rate (default 200): ").strip() or 200)
    pitch = int(input("请输入音色 (默认 50) / Enter pitch (default 50): ").strip() or 50)
    text_to_speech(text, language, rate, pitch)
