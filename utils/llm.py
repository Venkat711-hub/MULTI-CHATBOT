import os
from groq import Groq

# Model configurations
MODELS = {
    "Llama 3.3 70B (High Quality)": "llama-3.3-70b-specdec",
    "Llama 3.1 8B (Super Fast)": "llama-3.1-8b-instant",
    "Gemma 2 9B (Google)": "gemma2-9b-it",
    "Mixtral 8x7B (Large Context)": "mixtral-8x7b-32768"
}

def get_available_models():
    """Returns a list of model display names."""
    return list(MODELS.keys())

def get_model_id(display_name):
    """Maps display name to actual API model ID."""
    return MODELS.get(display_name, "llama-3.3-70b-specdec")

class GroqClientWrapper:
    def __init__(self, api_key=None):
        # Prefer provided key, fallback to env variable
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        
        if self.api_key:
            self.client = Groq(api_key=self.api_key)

    def is_configured(self):
        return self.client is not None

    def get_chat_completion(self, messages, model_name, temperature=0.7, max_tokens=1024, stream=True):
        """
        Sends chat history to Groq and returns a response.
        If stream=True, returns a generator that yields chunks.
        """
        if not self.client:
            raise ValueError("Groq API Key is not configured. Please set it in .env or the sidebar.")

        model_id = get_model_id(model_name)
        
        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model_id,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            return response
        except Exception as e:
            raise RuntimeError(f"Groq API Error: {str(e)}")
