import keyboard
import google.generativeai as genai
import os
from dotenv import load_dotenv
import threading
import pyperclip
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL

load_dotenv()

# Konfiguracja modelu Gemini
genai.configure(api_key=os.getenv("API_KEY"))

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

# Ustawienia audio
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Status
is_proccessing = False
print("Server started. Press Ctrl+Shift+A to process clipboard text. Press Ctrl+Alt+H to exit.")

def read_prompt_template():
    with open('prompt2.txt', 'r', encoding='utf-8') as file:
        return file.read().strip()

def on_hotkey_clipboard():
    global is_proccessing
    try:
        if is_proccessing:
            print("Processing is already in progress.")
            return
        is_proccessing = True

        text = pyperclip.paste()
        if not text.strip():
            print("Clipboard is empty.")
            is_proccessing = False
            return

        # Wycisz dźwięk
        volume.SetMute(1, None)

        # Wczytaj szablon i wyślij prompt
        prompt_template = read_prompt_template()
        prompt = text + prompt_template
        response = chat_session.send_message(prompt)
        generated_text = response.text.strip()

        # Skopiuj do schowka i przywróć głośność
        pyperclip.copy(generated_text.replace("```c", "").replace("```", ""))
        volume.SetMute(0, None)
        #volume.SetMasterVolumeLevelScalar(0.01, None)

        print("Response copied to clipboard.")

    except Exception as e:
        print(f"Error: {str(e)}")
        volume.SetMute(0, None)  # Odblokuj dźwięk w razie błędu
    finally:
        is_proccessing = False

def listen_keys():
    keyboard.wait('esc')

def exit_program():
    keyboard.unhook_all()
    os._exit(0)

if __name__ == "__main__":
    listener_thread = threading.Thread(target=listen_keys, daemon=True)
    listener_thread.start()
    keyboard.add_hotkey('ctrl+shift+a', on_hotkey_clipboard)
    keyboard.add_hotkey('ctrl+alt+h', exit_program)
    keyboard.wait()
