import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print(f"📁 Project root: {PROJECT_ROOT}")

try:
    from data_engineering.ingestion.api_collectors.openalex_collector import OpenAlexCollector
    from data_engineering.ingestion.api_collectors.openalex_mapper import map_openalex_work
    print("✅ Imports réussis!")
except ImportError as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)

print("\n🧪 Test du collecteur...")
collector = OpenAlexCollector()
works = collector.search_works("Morocco", per_page=5)
print(f"✅ Trouvé {len(works)} publications")

if works:
    print(f"\n📝 Première: {works[0].get('display_name', 'Sans titre')[:80]}...")
    
    print("\n🧪 Test du mapper...")
    pub = map_openalex_work(works[0])
    print(f"✅ Mappé: {pub.title[:60]}...")
    print(f"   Année: {pub.publication_year}")
    print(f"   Journal: {pub.journal}")

print("\n🧪 Test du pipeline...")
from data_engineering.ingestion.api_collectors.openalex_pipeline import run_pipeline
results = run_pipeline(search_query="Morocco university", per_page=10)
print(f"✅ Pipeline terminé: {len(results)} publications")

print("\n✅ TOUS LES TESTS TERMINÉS")
