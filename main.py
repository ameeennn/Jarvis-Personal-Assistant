import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import time
import msvcrt
import difflib
import json
import threading
import pythoncom
import queue
from ai_engine import AIEngine
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Load environment variables
load_dotenv()

# Initialize Colorama
init(autoreset=True)

class Jarvis:
    def __init__(self):
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
        
        self.wake_words = ["jarvis", "hey jarvis", "hi jarvis", "hello jarvis", "service", "travis", "hello", "hi"]
        self.is_listening = False
        self.is_speaking = False
        self.follow_up_active = False
        self.silent_mode = False 
        self.last_ai_response = "" 
        
        # Voice Queue System (Fixes 'run loop already started' error)
        self.voice_queue = queue.Queue()
        threading.Thread(target=self._voice_worker, daemon=True).start()
        
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
        if not self.silent_mode:
            self.voice_queue.put(text)
        print(f"{Fore.CYAN}Jarvis: {Style.BRIGHT}", end="", flush=True)
        for char in str(text):
            print(char, end="", flush=True)
            time.sleep(0.015)
        print() # newline

    def _voice_worker(self):
        """Dedicated thread for speaking from the queue."""
        pythoncom.CoInitialize()
        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = 1 # Slightly faster (default is 0, range -10 to 10)
            speaker.Volume = 100
        except Exception as e:
            print(f"{Fore.RED}SAPI Init Error: {e}")
            speaker = None

        while True:
            text = self.voice_queue.get()
            if text is None: break # Shutdown signal
            
            self.is_speaking = True
            try:
                if speaker:
                    # SAPI Speak is blocking and highly reliable
                    speaker.Speak(text)
                else:
                    # Fallback
                    import pyttsx3
                    engine = pyttsx3.init('sapi5')
                    engine.say(text)
                    engine.runAndWait()
            except Exception as e:
                print(f"{Fore.RED}Speech Engine Error: {e}")
            
            self.is_speaking = False
            self.voice_queue.task_done()
        
        pythoncom.CoUninitialize()

    def listen(self, source, timeout=None, phrase_time_limit=None, show_ui=False):
        # Prevent picking up own voice by pausing the mic while speaking
        while getattr(self, 'is_speaking', False):
            time.sleep(0.1)
            
        try:
            if show_ui: print(f"{Fore.YELLOW}Listening...", end="\r", flush=True)
            audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            if show_ui: print(f"{Fore.YELLOW}Processing...", end="\r", flush=True)
            query = self.recognizer.recognize_google(audio, language='en-in')
            if show_ui: print(" " * 30, end="\r", flush=True) # clear line
            return query.lower().strip()
        except sr.WaitTimeoutError:
            if show_ui: print(" " * 30, end="\r", flush=True)
            return ""
        except sr.UnknownValueError:
            if show_ui: print(" " * 30, end="\r", flush=True)
            return ""
        except Exception as e:
            if show_ui: print(" " * 30, end="\r", flush=True)
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
        if query in ['bye', 'bye jarvis'] or 'go to sleep' in query or 'standby' in query:
            self.speak("Standing by. Call me when you need me.")
            self.follow_up_active = False
            return "standby"

        # 2. SHUTDOWN COMMAND (Exit Script)
        elif query in ['shutdown', 'shutdown jarvis']:
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

        # 6. WEB SEARCH (Open Browser)
        elif 'open search' in query:
            search_query = query.replace("open search", "").strip()
            if search_query:
                self.speak(f"Searching for {search_query} on Google.")
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
            else:
                self.speak("What should I search for?")
            return True
        # 7. AI RESEARCH (Real-time data for Local AI)
        elif 'research' in query or 'latest' in query or 'live' in query:
            topic = query.replace("research", "").replace("latest", "").replace("live", "").strip()
            if topic:
                self.speak(f"Searching the web for live data on {topic}...")
                web_data = self.ai.search_web(topic)
                self.speak("Analyzing the findings...")
                response = self.ai.get_response(topic, context=web_data)
                self.last_ai_response = response # Save for storage
                self.speak(response)
            else:
                self.speak("What topic should I research for you?")
            return True

        # 8. SILENT MODE TOGGLE (Voice Control)
        elif any(cmd in query for cmd in ['mute', 'go silent', 'stop speaking', 'shut up']):
            self.silent_mode = True
            print(f"{Fore.RED}<<< SILENT MODE ENABLED >>>")
            self.speak("Okay, I will be quiet now.")
            return True

        elif any(cmd in query for cmd in ['speak', 'start speaking', 'voice on', 'unmute']):
            self.silent_mode = False
            print(f"{Fore.GREEN}<<< VOICE OUTPUT ENABLED >>>")
            self.speak("I am back. Voice output enabled.")
            return True

        # 9. FILE STORAGE
        elif 'store' in query or 'save' in query:
            filename = f"storage/entry_{int(time.time())}.txt"
            content = self.last_ai_response if self.last_ai_response else query
            try:
                with open(filename, "w") as f:
                    f.write(content)
                self.speak(f"Data saved to {filename}")
            except Exception as e:
                self.speak(f"Failed to save data: {e}")
            return True

        # 10. AI FALLBACK
        else:
            if self.ai_enabled:
                self.speak("Thinking...")
                response = self.ai.get_response(query)
                self.last_ai_response = response # Save for storage command
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
                # Check for manual mode trigger ('m' key) or mute ('s' key)
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
                        elif key == 's':
                            self.silent_mode = not self.silent_mode
                            status = "DISABLED" if self.silent_mode else "ENABLED"
                            color = Fore.RED if self.silent_mode else Fore.GREEN
                            print(f"\n{color}<<< VOICE OUTPUT {status} (Keyboard Shortcut) >>>")
                            if not self.silent_mode:
                                self.speak("Voice output enabled.")
                            continue
                    except: pass

                # Step 1: Wait for wake word (only if not in follow-up)
                if not self.follow_up_active:
                    query = self.listen(source, timeout=None, phrase_time_limit=None, show_ui=False)
                else:
                    query = "" # Proceed directly if in follow-up mode

                if (query and any(wake in query for wake in self.wake_words)) or self.follow_up_active:
                    self.is_listening = True
                    
                    # Log the wake-up
                    if query:
                        print(f"{Fore.WHITE}You: {query}")

                    # Check for "Toggles" or "Immediate Commands" in the wake-up query
                    command_to_process = ""
                    if not self.follow_up_active:
                        # Priority: Check for mode toggles first (e.g., "unmute service")
                        if any(cmd in query for cmd in ['unmute', 'speak', 'start speaking']):
                            self.silent_mode = False
                            print(f"{Fore.GREEN}<<< VOICE OUTPUT ENABLED >>>")
                            self.speak("Voice output enabled.")
                            self.is_listening = False
                            continue
                        elif any(cmd in query for cmd in ['mute', 'go silent', 'shut up']):
                            self.silent_mode = True
                            print(f"{Fore.RED}<<< SILENT MODE ENABLED >>>")
                            self.speak("Okay, going silent.")
                            self.is_listening = False
                            continue

                        # Standard Immediate Command check
                        for wake in self.wake_words:
                            if wake in query:
                                command_part = query.split(wake)[-1].strip()
                                if len(command_part) > 2:
                                    command_to_process = command_part
                                    break
                    
                    if command_to_process:
                        print(f"{Fore.GREEN}Action: Executing Immediate Command -> {command_to_process}")
                        self.process_command(command_to_process)
                        self.follow_up_active = True
                    else:
                        if not self.follow_up_active:
                            self.speak("Yes? I am listening.")
                        
                        # Only show 'Listening...' during explicit command phase
                        command = self.listen(source, timeout=10, show_ui=True)
                        
                        if command:
                            print(f"{Fore.WHITE}You: {command}")
                            result = self.process_command(command)
                            
                            if result == "exit":
                                break
                            elif result == "standby":
                                self.follow_up_active = False
                            else:
                                self.follow_up_active = True
                                print(f"{Fore.MAGENTA}--- Session Mode: Active ---")
                        else:
                            if self.follow_up_active:
                                print(f"{Fore.YELLOW}Session timed out.")
                                self.speak("Going to standby.")
                            self.follow_up_active = False
                    
                    self.is_listening = False
                
                time.sleep(0.1)

if __name__ == "__main__":
    jarvis = Jarvis()
    try:
        jarvis.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Jarvis shutting down...")
