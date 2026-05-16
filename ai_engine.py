import os
import requests
from google import genai
from groq import Groq
from dotenv import load_dotenv
from colorama import Fore

load_dotenv()

class AIEngine:
    def __init__(self):
        self.providers = []
        self.current_provider_index = 0
        
        # 1. Initialize Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                client = genai.Client(api_key=gemini_key)
                
                # Dynamic Model Discovery
                available_gemini_models = []
                for m in client.models.list():
                    if 'generate_content' in m.supported_actions or 'generateContent' in m.supported_actions:
                        available_gemini_models.append(m.name.replace('models/', ''))
                
                if available_gemini_models:
                    self.providers.append({
                        "name": "Gemini",
                        "client": client,
                        "models": available_gemini_models, # Use exactly what the key supports
                        "type": "gemini"
                    })
            except Exception as e:
                print(f"Gemini Discovery failed: {e}")

        # 2. Initialize Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                client = Groq(api_key=groq_key)
                self.providers.append({
                    "name": "Groq",
                    "client": client,
                    "models": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
                    "type": "groq"
                })
            except: pass

        # 3. Initialize OpenRouter
        or_key = os.getenv("OPEN_ROUTER_API_KEY")
        if or_key:
            self.providers.append({
                "name": "OpenRouter",
                "key": or_key,
                "models": ["google/gemini-2.0-flash-001", "anthropic/claude-3-haiku", "meta-llama/llama-3.1-8b-instruct"],
                "type": "openrouter"
            })

        # 4. Initialize HuggingFace
        hf_key = os.getenv("HF_API_KEY")
        if hf_key:
            self.providers.append({
                "name": "HuggingFace",
                "key": hf_key,
                "models": ["mistralai/Mistral-7B-Instruct-v0.3", "meta-llama/Llama-3.2-1B-Instruct", "microsoft/Phi-3-mini-4k-instruct"],
                "type": "hf"
            })

    def get_response(self, prompt):
        if not self.providers:
            return "No AI providers configured. Please check your .env file."

        # Outer loop: Try different providers
        for p_attempt in range(len(self.providers)):
            provider = self.providers[self.current_provider_index]
            
            # Inner loop: Try different models within the provider
            for model_name in provider["models"]:
                try:
                    print(f"{Fore.CYAN}Trying {provider['name']} with model {model_name}...")
                    response = self._call_provider(provider, model_name, prompt)
                    if response:
                        return response
                except Exception as e:
                    print(f"{Fore.RED}{provider['name']} model {model_name} failed: {e}")
                    continue # Try next model in same provider
            
            # If all models in this provider failed, move to next provider
            print(f"{Fore.YELLOW}All models in {provider['name']} failed. Switching provider...")
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        
        return "All AI providers and models failed. Please check your internet or API keys."

    def _call_provider(self, provider, model, prompt):
        if provider["type"] == "gemini":
            response = provider["client"].models.generate_content(model=model, contents=prompt)
            return response.text

        elif provider["type"] == "groq":
            chat_completion = provider["client"].chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
            )
            return chat_completion.choices[0].message.content

        elif provider["type"] == "openrouter":
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": prompt}]}
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            raise Exception(f"Error {response.status_code}: {response.text}")

        elif provider["type"] == "hf":
            API_URL = f"https://api-inference.huggingface.co/models/{model}"
            headers = {"Authorization": f"Bearer {provider['key']}"}
            response = requests.post(API_URL, headers=headers, json={"inputs": f"<s>[INST] {prompt} [/INST]", "parameters": {"max_new_tokens": 500}})
            result = response.json()
            if isinstance(result, list) and 'generated_text' in result[0]:
                text = result[0]['generated_text']
                # Clean up Mistral instruction tags if they appear in output
                return text.split("[/INST]")[-1].strip()
            raise Exception(f"HF Error: {result}")

        return None
