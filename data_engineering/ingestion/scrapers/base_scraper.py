"""
Base scraper
"""
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class BaseScraper:
    """Classe de base pour les scrapers"""
    
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def fetch_page(self, url: str) -> Optional[str]:
        """Télécharger une page HTML"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout {url}, tentative {attempt + 1}")
            except Exception as e:
                logger.warning(f"Erreur {url}: {e}, tentative {attempt + 1}")
        
        logger.error(f"Échec après {self.max_retries} tentatives: {url}")
        return None
    
    def save_html(self, content: str, output_path: Path) -> bool:
        """Sauvegarder le HTML"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde: {e}")
            return False
    
    def save_metadata(self, metadata: Dict[str, Any], output_path: Path) -> bool:
        """Sauvegarder les métadonnées"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            logger.error(f"Erreur metadata: {e}")
            return False