# 🤖 JARVIS: AI-Powered Personal Assistant

A high-performance, local-first personal assistant with a "Multi-Brain" AI fallback system. Jarvis prioritizes speed for local tasks and uses a sophisticated AI engine for everything else.

![Jarvis Demo](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![AI-Powered](https://img.shields.io/badge/AI-Multi--Provider-orange)

## 🌟 Key Features

- **🎙️ Advanced Voice Control**: High-sensitivity wake word detection with "No-Flicker" mic technology.
- **🔄 Smart AI Fallback**: Automatic switching between **Gemini, Groq, OpenRouter, and HuggingFace**. If one hits a limit, Jarvis hops to the next brain!
- **📦 Universal App Support**: Automatically scans your Windows Start Menu to open any installed app.
- **💬 Conversational Follow-up**: Jarvis stays awake for 8 seconds after a command for natural follow-up questions.
- **🛡️ Local-First Architecture**: App opening, system info, and web searches happen instantly without AI latency.
- **⌨️ Manual Mode**: Press 'M' to type commands if you're in a quiet environment.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8 or higher.
- A microphone (built-in or USB).

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

- **Wake Words**: *"Jarvis"*, *"Hi Jarvis"*, *"Hello"*
- **Apps**: *"Open Chrome"*, *"Open Calculator"*, *"Close Notepad"*
- **System**: *"What time is it?"*, *"What's today's date?"*
- **Search**: *"Search for best Python libraries on Google"*
- **AI**: *"Who is the Prime Minister of India?"*, *"Explain Quantum Physics like I'm five."*
- **Standby**: *"Bye Jarvis"*, *"Go to sleep"*
- **Shutdown**: *"Shutdown Jarvis"*

## 📂 Project Structure

- `main.py`: Core logic, listener loop, and system actions.
- `ai_engine.py`: The multi-provider AI brain with fallback logic.
- `app_scanner.py`: Utility to update the app database (`apps.json`).
- `apps.json`: Generated list of your installed Windows applications.

## 🤝 Contributing
Feel free to fork this repo and add your own local actions or AI providers!

---
*Developed with ❤️ for the AI Community.*
