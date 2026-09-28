"""
Service LLM - abstraction pour Ollama ou API externe
"""
import logging
import requests
import os
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class LLMService:
    """Wrapper pour interroger un LLM (Ollama par défaut)"""
    
    def __init__(self, provider: str = "ollama", model: str = None):
        self.provider = provider
        self.model = model or self._default_model()
        
        if provider == "ollama":
            self.base_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
            self._check_ollama()
        elif provider == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("❌ OPENAI_API_KEY manquante")
        else:
            raise ValueError(f"Provider inconnu: {provider}")
        
        logger.info(f"✅ LLM prêt ({provider} / {self.model})")
    
    def _default_model(self) -> str:
        return {
            "ollama": "llama3.2:3b",
            "openai": "gpt-4o-mini"
        }.get(self.provider, "llama3.2:3b")
    
    def _check_ollama(self):
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            models = [m['name'] for m in r.json().get('models', [])]
            logger.info(f"📦 Modèles Ollama disponibles: {models}")
            if not any(self.model in m for m in models):
                logger.warning(f"⚠️ Modèle {self.model} non trouvé. Faites: ollama pull {self.model}")
        except Exception as e:
            raise ConnectionError(f"❌ Ollama inaccessible ({self.base_url}): {e}")
    
    def generate(self, prompt: str, system: str = None, 
                 temperature: float = 0.3, max_tokens: int = 800) -> str:
        """Générer une réponse"""
        if self.provider == "ollama":
            return self._generate_ollama(prompt, system, temperature, max_tokens)
        elif self.provider == "openai":
            return self._generate_openai(prompt, system, temperature, max_tokens)
    
    def _generate_ollama(self, prompt, system, temperature, max_tokens) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system:
            payload["system"] = system
        
        r = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=600)
        r.raise_for_status()
        return r.json().get('response', '').strip()
    
    def _generate_openai(self, prompt, system, temperature, max_tokens) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        r = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return r.choices[0].message.content.strip()


if __name__ == "__main__":
    llm = LLMService()
    print(llm.generate("Dis bonjour en une phrase.", max_tokens=50))