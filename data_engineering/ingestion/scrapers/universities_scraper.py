"""
Scraper pour les universités marocaines
"""
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, Any, Optional
import json

from .base_scraper import BaseScraper
from .link_extractor import LinkExtractor

logger = logging.getLogger(__name__)

class UniversityScraper(BaseScraper):
    """Scraper pour les universités"""
    
    def __init__(self, university_name: str, base_url: str):
        super().__init__()
        self.university_name = university_name
        self.base_url = base_url
        self.link_extractor = LinkExtractor()
        self.visited_urls = set()
        
    def scrape(self, max_pages: int = 10, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Scraper l'université"""
        logger.info(f"🚀 Scraping de {self.university_name}")
        
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"/opt/airflow/data_engineering/ingestion/raw/universities/{self.university_name.lower().replace(' ', '_')}/{timestamp}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = datetime.now()
        pages_scraped = 0
        errors = 0
        
        # Scraper la page d'accueil
        logger.info(f"📄 Scraping: {self.base_url}")
        html = self.fetch_page(self.base_url)
        
        if html:
            page_file = output_dir / "page_001.html"
            self.save_html(html, page_file)
            pages_scraped += 1
            logger.info(f"✅ Page 1 sauvegardée")
        else:
            errors += 1
            logger.error(f"❌ Impossible de scraper {self.base_url}")
        
        # Scraper les pages supplémentaires
        to_visit = [self.base_url]
        page_num = 1
        
        while to_visit and pages_scraped < max_pages:
            url = to_visit.pop(0)
            if url in self.visited_urls:
                continue
            
            html = self.fetch_page(url)
            if html:
                page_num += 1
                page_file = output_dir / f"page_{page_num:03d}.html"
                self.save_html(html, page_file)
                pages_scraped += 1
                logger.info(f"✅ Page {page_num} sauvegardée")
                
                # Extraire les liens
                new_links = self.link_extractor.extract_internal_links(html, self.base_url)
                for link in new_links:
                    if link not in self.visited_urls and link not in to_visit:
                        to_visit.append(link)
            else:
                errors += 1
            
            self.visited_urls.add(url)
        
        # Métadonnées
        metadata = {
            "university": self.university_name,
            "base_url": self.base_url,
            "pages_scraped": pages_scraped,
            "errors": errors,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "output_dir": str(output_dir),
            "status": "success" if pages_scraped > 0 else "failed"
        }
        
        metadata_file = output_dir / "metadata.json"
        self.save_metadata(metadata, metadata_file)
        
        logger.info(f"✅ Scraping terminé: {pages_scraped} pages")
        return metadata


def scrape_university(university_name: str, url: str, max_pages: int = 10) -> Dict[str, Any]:
    """Fonction utilitaire"""
    scraper = UniversityScraper(university_name, url)
    return scraper.scrape(max_pages=max_pages)