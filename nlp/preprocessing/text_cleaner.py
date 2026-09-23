"""
Nettoyage des textes pour le NLP
"""
import re
import logging
from typing import List

logger = logging.getLogger(__name__)


class TextCleaner:
    """Nettoyeur de textes"""
    
    def __init__(self):
        self.url_pattern = re.compile(r'http\S+|www\.\S+')
        self.email_pattern = re.compile(r'\S+@\S+')
        self.special_chars = re.compile(r'[^a-zA-Z0-9\s\-]')
        self.multiple_spaces = re.compile(r'\s+')
        self.numbers = re.compile(r'\b\d+\b')
    
    def clean(self, text: str, lowercase: bool = True) -> str:
        """Nettoyer un texte"""
        if not text or not isinstance(text, str):
            return ""
        
        # URLs
        text = self.url_pattern.sub(' ', text)
        
        # Emails
        text = self.email_pattern.sub(' ', text)
        
        # Caractères spéciaux
        text = self.special_chars.sub(' ', text)
        
        # Nombres
        text = self.numbers.sub(' ', text)
        
        # Espaces multiples
        text = self.multiple_spaces.sub(' ', text)
        
        if lowercase:
            text = text.lower()
        
        return text.strip()
    
    def remove_stopwords(self, text: str, stopwords: set) -> str:
        """Supprimer les stopwords"""
        words = text.split()
        filtered = [w for w in words if w not in stopwords and len(w) > 2]
        return ' '.join(filtered)
    
    def lemmatize(self, text: str, nlp) -> str:
        """Lemmatiser avec spaCy"""
        doc = nlp(text)
        lemmas = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(lemmas)


if __name__ == "__main__":
    cleaner = TextCleaner()
    
    test = "Impact of ChatGPT (2024) on Academic Writing! Visit https://example.com"
    cleaned = cleaner.clean(test)
    print(f"Original: {test}")
    print(f"Cleaned:  {cleaned}")