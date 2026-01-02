# EVA: Windows AI Assistant – Capabilities Overview
**works only partially**

## What is EVA?
**EVA** is a powerful AI assistant for Windows, built with PyQt5. It combines voice recognition, natural language processing, and system automation to deliver a seamless desktop assistant experience. EVA understands both voice and text commands, automates system tasks, and interacts with multiple AI language models.

---

## Key Features

### 🤖 AI Conversation & Language Models
- **Supports Multiple LLMs:** Cohere (main), ChatGPT (GPT-4.1-nano), Claude (Claude-3-5-Haiku), DeepSeek (formatting)
- **Streaming Responses:** Real-time, token-by-token
- **Contextual Conversations:** Maintains chat history
- **18 Languages Supported:** Including English, Russian, Japanese, German, Spanish, and more

### 🎤 Voice & Speech
- **Speech-to-Text:** Real-time via Google Web Speech API
- **Wake Word:** "EVA" for hands-free use
- **Text-to-Speech:** ElevenLabs and Edge TTS integration
- **Continuous Listening:** Background microphone monitoring
- **Audible Feedback:** Spoken confirmations and responses

### 🕒 Time & Reminders
- **Time & Date:** Commands like `say time` and `say date`
- **Alarms & Reminders:** Set alarms (e.g., "set alarm 15:30") and custom reminders
- **Task Scheduling:** Background operations for timed tasks

### 🌐 Web & Browser Control
- **Open Websites:** "open google.com"
- **Launch Browsers:** "open chrome"
- **Web Search:** "search for Elon Musk"
- **URL Handling:** Automatic formatting and validation

### 🔊 Audio & Music
- **Volume Control:** `volume increase`, `volume decrease`, `mute`, `unmute`
- **Music Playback:** Play and manage music files, add directories, organize tracks
- **Audio Formats:** MP3, WAV, and more

### 🖥️ System & File Management
- **Launch Apps:** Notepad, Paint, CMD, Calculator, Explorer, and custom apps
- **File Operations:** Open, read, scan, search, and reorganize files
- **Directory Management:** Navigate and manage folders

### 🎛️ System Automation
- **Screen Brightness:** Adjust display levels
- **Process Management:** Monitor and control running apps
- **System Monitoring:** Track resources in real time
- **Power Controls:** Basic system power management

### 🧮 Math & Calculator
- **Calculator:** Solve expressions and advanced calculations
- **Instant Results:** Real-time computation

### 📱 User Interface
- **Modern PyQt5 UI:** Clean, responsive, multi-page design
- **Settings & Themes:** Customizable preferences and visual styles
- **Sidebar & Chat:** Quick navigation and modern chat interface

### 🔧 Advanced
- **NLP:** Smart command parsing and fuzzy matching
- **Multi-threading:** Non-blocking background tasks
- **Error Handling:** Robust feedback and logging
- **Config Management:** Persistent user settings
- **Plugin System:** Easily extend EVA's capabilities

### 🌍 Internationalization
- **18 Languages:** Localized responses and region-specific formatting
- **Translation:** Real-time text translation

### 🔒 Security & Privacy
- **Local Processing:** Voice and basic tasks run locally
- **API Key Security:** Safe handling of credentials
- **User Data:** Preferences stored locally, privacy controls available

---

## System Requirements
- **OS:** Windows 10/11
- **Python:** 3.10+
- **RAM:** 4GB minimum (8GB recommended)
- **Storage:** 500MB free
- **Microphone:** Required for voice features
- **Internet:** Needed for AI and web features

## Core Dependencies
- PyQt5, SpeechRecognition, PyAudio, pycaw, Cohere/OpenAI/Anthropic, Edge TTS, psutil, screen_brightness_control

## Architecture
- Modular, thread-safe, event-driven, and plugin-ready

---

## Use Cases
- **Productivity:** Quick system tasks, file management, scheduling, web research
- **Accessibility:** Voice control, hands-free operation, audio feedback, multi-language
- **Entertainment:** Music playback, AI chat, web browsing, media management
- **Technical:** System monitoring, automation, math, workflow assistance

---

## Looking Ahead
Planned features include:
- Improved voice recognition
- More AI integrations
- Advanced automation
- Cloud sync
- Mobile companion app
- Smart home integration
- Enhanced scheduling and calendar

---

**EVA** is your all-in-one, voice-powered AI assistant for Windows—bridging natural language and system control for productivity, accessibility, and entertainment.
