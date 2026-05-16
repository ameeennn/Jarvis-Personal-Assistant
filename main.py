import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import time
import msvcrt
import difflib
import json
from ai_engine import AIEngine
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Load environment variables
load_dotenv()

# Initialize Colorama
init(autoreset=True)

class Jarvis:
    def __init__(self):
        self.engine = pyttsx3.init('sapi5')
        voices = self.engine.getProperty('voices')
        # Set voice (usually 0 is male, 1 is female)
        self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 180)  # Speed of speech
        
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 100 # Even lower for maximum sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        
        # Diagnostics: List microphones
        print(f"{Fore.YELLOW}Checking microphones...")
        mic_list = sr.Microphone.list_microphone_names()
        for i, mic in enumerate(mic_list):
            print(f"  [{i}] {mic}")
        
        # Use MIC_INDEX from .env or default to 2 (Realtek High Definition)
        self.mic_index = int(os.getenv("MIC_INDEX", 2))
        current_mic = mic_list[self.mic_index] if self.mic_index < len(mic_list) else "Unknown"
        print(f"{Fore.CYAN}Using microphone index [{self.mic_index}]: {current_mic}")
        
        self.wake_words = ["jarvis", "hi jarvis", "hey jarvis", "service", "travis", "hello", "hi"]
        self.is_listening = False
        self.follow_up_active = False # New: Tracks if we are in a conversation
        
        # Load external apps database
        try:
            with open("apps.json", "r") as f:
                self.apps = json.load(f)
            print(f"{Fore.GREEN}Loaded {len(self.apps)} apps from database.")
        except:
            self.apps = {}
            print(f"{Fore.RED}Warning: apps.json not found. App opening limited.")

        # AI Engine Setup (Multi-Provider Fallback)
        self.ai = AIEngine()
        if self.ai.providers:
            self.ai_enabled = True
            names = ", ".join([p['name'] for p in self.ai.providers])
            print(f"{Fore.GREEN}AI System Active with providers: {names}")
        else:
            self.ai_enabled = False
            print(f"{Fore.RED}Warning: No AI API keys found. AI features disabled.")

    def speak(self, text):
        print(f"{Fore.CYAN}Jarvis: {Style.BRIGHT}{text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, source, timeout=None, phrase_time_limit=None):
        try:
            # We removed adjust_for_ambient_noise from here to prevent "dead zones"
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            query = self.recognizer.recognize_google(audio, language='en-in')
            return query.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            if self.is_listening:
                print(f"{Fore.RED}Listener Error: {e}")
            return ""

    def wish_me(self):
        hour = int(datetime.datetime.now().hour)
        if 0 <= hour < 12:
            self.speak("Good Morning!")
        elif 12 <= hour < 18:
            self.speak("Good Afternoon!")
        else:
            self.speak("Good Evening!")
        self.speak("How can I help you today?")


    def process_command(self, query):
        query = query.lower().strip()
        
        # 1. STANDBY COMMAND
        if 'bye' in query or 'go to sleep' in query or 'standby' in query:
            self.speak("Standing by. Call me when you need me.")
            self.follow_up_active = False
            return "standby"

        # 2. SHUTDOWN COMMAND (Exit Script)
        elif 'shutdown' in query and 'jarvis' in query:
            self.speak("Shutting down the system. Goodbye!")
            return "exit"

        # 3. APP OPENING
        elif 'open' in query:
            app_name = query.replace("open", "").strip()
            # Find closest match in the extensive apps database
            matches = difflib.get_close_matches(app_name, self.apps.keys(), n=1, cutoff=0.5)
            
            if matches:
                target = matches[0]
                action = self.apps[target]
                self.speak(f"Opening {target.capitalize()}.")
                if action.startswith("http"):
                    webbrowser.open(action)
                else:
                    os.system(action)
                return True
            else:
                self.speak(f"I couldn't find {app_name} in your installed apps.")
                return True

        # 4. APP CLOSING
        elif 'close' in query:
            app_name = query.replace("close", "").strip()
            self.speak(f"Attempting to close {app_name}.")
            # Using taskkill to close applications by name
            os.system(f"taskkill /f /im {app_name}.exe")
            return True

        # 5. TIME/DATE
        elif 'time' in query:
            time_now = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {time_now}")
            return True

        elif 'date' in query:
            date_now = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {date_now}")
            return True

        # 6. WEB SEARCH
        elif 'search' in query:
            search_query = query.replace("search", "").strip()
            if search_query:
                self.speak(f"Searching for {search_query} on Google.")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
            else:
                self.speak("What should I search for?")
            return True

        # 7. AI FALLBACK
        else:
            if self.ai_enabled:
                self.speak("Thinking...")
                response = self.ai.get_response(query)
                self.speak(response)
            else:
                self.speak(f"I heard you say '{query}', but I don't have a specific action for that yet.")
            return True

    def start(self):
        self.wish_me()
        print(f"{Fore.MAGENTA}{'='*40}")
        print(f"{Fore.MAGENTA}      JARVIS IS ACTIVE")
        print(f"{Fore.MAGENTA}  (Press 'M' for Manual Text Mode)")
        print(f"{Fore.MAGENTA}{'='*40}")
        
        # Keep mic open to stop taskbar icon flickering
        with sr.Microphone(device_index=self.mic_index) as source:
            print(f"{Fore.YELLOW}Calibrating microphone for ambient noise... (Please stay quiet)")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.recognizer.pause_threshold = 1.0 # Give more time to speak without cutting
            print(f"{Fore.GREEN}Ready! Waiting for wake word...")

            while True:
                # Check for manual mode trigger ('m' key)
                if msvcrt.kbhit():
                    try:
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'm':
                            self.is_listening = True
                            print(f"\n{Fore.GREEN}--- MANUAL MODE ---")
                            text_command = input(f"{Fore.CYAN}Enter your command: ").lower()
                            if text_command:
                                result = self.process_command(text_command)
                                if result == "exit": break
                            self.is_listening = False
                            continue
                    except: pass

                # Step 1: Wait for wake word (only if not in follow-up)
                if not self.follow_up_active:
                    query = self.listen(source, timeout=1, phrase_time_limit=3)
                else:
                    query = "" # Proceed directly if in follow-up mode

                if (query and any(wake in query for wake in self.wake_words)) or self.follow_up_active:
                    self.is_listening = True
                    if not self.follow_up_active:
                        self.speak("Yes? I am listening.")
                    
                    # Listen for command (Wait longer for actual speech)
                    command = self.listen(source, timeout=5, phrase_time_limit=10)
                    if command:
                        print(f"{Fore.WHITE}Command: {command}")
                        result = self.process_command(command)
                        if result == "exit":
                            break
                        elif result == "standby":
                            self.follow_up_active = False
                        else:
                            self.follow_up_active = True
                            print(f"{Fore.MAGENTA}--- Follow-up Mode Active ---")
                    else:
                        if self.follow_up_active:
                            print(f"{Fore.YELLOW}Follow-up timed out. Returning to standby.")
                        self.follow_up_active = False
                    self.is_listening = False
                
                time.sleep(0.1)

if __name__ == "__main__":
    jarvis = Jarvis()
    try:
        jarvis.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Jarvis shutting down...")
