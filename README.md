# 🤖 JARVIS: AI-Powered Personal Assistant

A high-performance, local-first personal assistant with a "Multi-Brain" AI fallback system. Jarvis prioritizes speed for local tasks and uses a sophisticated AI engine for everything else.

![Jarvis Demo](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![AI-Powered](https://img.shields.io/badge/AI-Multi--Provider-orange)

## 🌟 Key Features (v2.0 Update!)

- **🎙️ Advanced Voice Control**: High-sensitivity wake word detection with "No-Flicker" mic technology.
- **🗣️ Robust Speech Engine**: Direct SAPI5 integration using `win32com` prevents freezing and ensures 100% reliable text-to-speech without deadlocks.
- **🔇 Auto-Mute Feedback Prevention**: Jarvis automatically pauses microphone input while speaking to prevent echoing its own voice.
- **✨ ChatGPT-Style UI**: Text output features a smooth typewriter effect, while microphone inputs show dynamic `Listening...` and `Processing...` indicators just like Google Assistant.
- **🔄 Smart AI Fallback**: Automatic switching between **Gemini, Groq, OpenRouter, and HuggingFace**.
- **📦 Universal App Support**: Automatically scans your Windows Start Menu to open any installed app.
- **💬 Conversational Follow-up**: Jarvis stays awake for 10 seconds after a command for natural follow-up questions.
- **🛡️ Local-First Architecture**: App opening, system info, and web searches happen instantly without AI latency.
- **⌨️ Manual Mode**: Press 'M' to type commands if you're in a quiet environment, or 'S' to quickly toggle voice output.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8 or higher.
- A microphone (built-in or USB).
- Windows OS (Required for SAPI5 TTS and Windows App scanning).

### 2. Installation
```bash
git clone https://github.com/yourusername/jarvis-ai.git
cd jarvis-ai
pip install -r requirements.txt
```

### 3. Setup API Keys
1. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and add your keys from:
   - [Google AI Studio (Gemini)](https://aistudio.google.com/)
   - [Groq Cloud](https://console.groq.com/)
   - [OpenRouter](https://openrouter.ai/)
   - [HuggingFace](https://huggingface.co/settings/tokens)

### 4. Microphone Setup
When you first run Jarvis, he will list all available microphones. If he doesn't hear you:
1. Find the index number (e.g., `[2]`) of your real microphone in the console list.
2. Update `MIC_INDEX` in your `.env` file.

### 5. Running Jarvis
```bash
python main.py
```

## 🛠️ Usage Commands

- **Wake Words**: *"Jarvis"*, *"Hey Jarvis"*, *"Hi Jarvis"*
- **Voice Toggles**: *"Mute"*, *"Go silent"*, *"Speak"*, *"Unmute"*
- **Apps**: *"Open Chrome"*, *"Open Calculator"*, *"Close Notepad"*
- **System**: *"What time is it?"*, *"What's today's date?"*
- **Search**: *"Open search [query]"* or *"Research [topic]"*
- **AI**: *"Who is the Prime Minister of India?"*, *"Explain Quantum Physics like I'm five."*
- **Standby**: *"Bye Jarvis"*, *"Bye"*
- **Shutdown**: *"Shutdown Jarvis"*, *"Shutdown"*

## 📂 Project Structure

- `main.py`: Core logic, listener loop, and system actions.
- `ai_engine.py`: The multi-provider AI brain with fallback logic.
- `app_scanner.py`: Utility to update the app database (`apps.json`).
- `apps.json`: Generated list of your installed Windows applications.

## 🤝 Contributing
Feel free to fork this repo and add your own local actions or AI providers!

---
*Developed with ❤️ for the AI Community.*
