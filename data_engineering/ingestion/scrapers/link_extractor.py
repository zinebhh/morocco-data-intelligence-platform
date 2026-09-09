"""
Extracteur de liens - Découvre les URLs à scraper
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List, Set, Optional
import logging

logger = logging.getLogger(__name__)

class LinkExtractor:
    """Extrait et filtre les liens d'une page HTML"""
    
    def __init__(self):
        self.exclude_patterns = [
            r'\.(jpg|jpeg|png|gif|pdf|doc|docx|zip|rar|mp4|avi)$',
            r'^#',
            r'^javascript:',
            r'^mailto:',
            r'^tel:'
        ]
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """
        Extraire tous les liens d'une page HTML
        
        Args:
            html: Contenu HTML
            base_url: URL de base pour les liens relatifs
            
        Returns:
            List[str]: Liste des URLs absolues
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Ignorer les liens vides
            if not href or href.strip() == '':
                continue
            
            # Convertir en URL absolue
            absolute_url = urljoin(base_url, href)
            
            # Filtrer les liens
            if self._is_valid_link(absolute_url):
                links.add(absolute_url)
        
        return list(links)
    
    def _is_valid_link(self, url: str) -> bool:
        """Vérifier si un lien est valide à scraper"""
        # Ignorer les liens externes
        for pattern in self.exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Ignorer les liens trop longs
        if len(url) > 2000:
            return False
        
        return True
    
    def extract_internal_links(self, html: str, base_url: str) -> List[str]:
        """Extraire uniquement les liens internes"""
        all_links = self.extract_links(html, base_url)
        base_domain = urlparse(base_url).netloc
        
        internal_links = []
        for link in all_links:
            parsed = urlparse(link)
            if parsed.netloc == base_domain or not parsed.netloc:
                internal_links.append(link)
        
        return internal_links
    
    def extract_links_by_selector(self, html: str, base_url: str, selector: str) -> List[str]:
        """Extraire les liens correspondant à un sélecteur CSS"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for element in soup.select(selector):
            if element.get('href'):
                url = urljoin(base_url, element['href'])
                if self._is_valid_link(url):
                    links.append(url)
        
        return links