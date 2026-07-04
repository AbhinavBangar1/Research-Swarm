import os
from langchain_ollama import ChatOllama

class LLMFactory:
    @staticmethod
    def get_llm(temperature=0.0):
        """
        Dynamically returns the configured LLM based on environment variables.
        Defaults to local Qwen 7B via Ollama.
        """
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider == "ollama":
            # Connect to local Ollama instance running qwen2.5:7b
            return ChatOllama(model="qwen2.5:7b", temperature=temperature)
        else:
            raise ValueError(f"Unsupported LLM Provider: {provider}")
