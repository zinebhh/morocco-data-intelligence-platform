"""
Extracteur de liens
"""
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import List
import logging

logger = logging.getLogger(__name__)

class LinkExtractor:
    """Extrait les liens d'une page HTML"""
    
    def __init__(self):
        self.exclude_patterns = [
            r'\.(jpg|jpeg|png|gif|pdf|doc|docx|zip|rar|mp4|avi)$',
            r'^#',
            r'^javascript:',
            r'^mailto:',
            r'^tel:',
        ]
    
    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extraire tous les liens"""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if not href or href.strip() == '':
                continue
            
            absolute_url = urljoin(base_url, href)
            
            if self._is_valid_link(absolute_url):
                links.add(absolute_url)
        
        return list(links)
    
    def _is_valid_link(self, url: str) -> bool:
        """Vérifier si un lien est valide"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        if len(url) > 2000:
            return False
        
        return True
    
    def extract_internal_links(self, html: str, base_url: str) -> List[str]:
        """Extraire les liens internes"""
        all_links = self.extract_links(html, base_url)
        base_domain = urlparse(base_url).netloc
        
        internal_links = []
        for link in all_links:
            parsed = urlparse(link)
            if parsed.netloc == base_domain or not parsed.netloc:
                internal_links.append(link)
        
        return internal_links