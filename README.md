# 🗣️ Expressive Marathi Text-to-Speech with Smart Prosody Conversion

A smart speech synthesis system that converts **Marathi text to expressive speech**, supporting **regional dialects**, **emotions**, and **punctuation-based prosody** for natural-sounding output.

---

## 📸 Frontend Screenshot

<img width="1366" height="727" alt="frontend" src="https://github.com/user-attachments/assets/70712c39-56f1-42ac-99f8-278d24d0aff0" />


---

## 🧠 Project Description

This project aims to build an intelligent Marathi TTS (Text-to-Speech) system that not only reads text but adds human-like **prosody, emotions, and dialect-specific features**. It improves intelligibility and expressiveness for better real-life applicability such as:

- Assistive speech for visually impaired users
- Regional speech interfaces
- Emotional response systems
- Voice assistants and storytelling bots

---

## ✨ Key Features

- ✅ **Multiple Marathi Dialects** (Standard, Varhadi, Ahirani, Malwani, Nagpuri, Konkani)
- 😊 **Emotions** (Neutral, Happy, Angry, Sad, Punctuation-based)
- 🎤 **Punctuation-aware Speech Modulation**
- 📦 Save audio output as `.wav`
- 🎧 Real-time speech playback
- 💡 Clean, dark-mode GUI in Marathi

---

## 🔧 Tech Stack

- `Python`
- [`gTTS`](https://pypi.org/project/gTTS/) (Google Text-to-Speech)
- `Pydub`, `scipy`, `sounddevice`, `soundfile`, `numpy`
- `pygame` for audio playback
- `customtkinter` for GUI

---

## 📥 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShivamDagade/MarathiTextToSpeech.git
   cd marathi-tts-prosody
   ```

2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python your_main_script_name.py
   ```

---

## 🚀 How to Use

1. Enter **Marathi text** in the textbox.
2. Select a **dialect** (e.g., Varhadi, Ahirani).
3. Choose an **emotion** (e.g., Happy, Sad, Angry).
4. Click on **"बोलणे सुरू करा"** to play the synthesized speech.
5. Use **"ऑडिओ सेव्ह करा"** to save the output as a WAV file.
6. Click **"थांबवा"** to stop playback and **"मजकूर साफ करा"** to clear the input.

---

## 📁 File Structure

```
📦 marathi-tts-prosody
 ┣ 📜 main.py
 ┣ 📷 frontend.png
 ┣ 📜 README.md
 ┗ 📜 requirements.txt
```

---

## 🙏 Credits

- **Text-to-Speech API:** Google Text-to-Speech (gTTS)
- **GUI:** CustomTkinter
- **Audio Processing:** Pydub, Scipy, Soundfile
