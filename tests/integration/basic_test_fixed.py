"""TODO: Add docstring."""

import sys
import os

# Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_core_modules():
    """TODO: Add docstring."""
    print(" ...")
    
    try:
        # 
        from src.config import DeepSearchConfig
        config = DeepSearchConfig()
        print(f" : {config.search_engine}, topk={config.topk}")
        
        # 
        from src.models import SearchResult, PageExtract, SearchLink
        print(" ")
        
        # 
        from src.searcher import DuckDuckGoSearcher
        searcher = DuckDuckGoSearcher(topk=3)
        print(f" : {searcher.name}")
        
        # 
        from src.extractor import ContentExtractor
        extractor = ContentExtractor()
        print(" ")
        
        return True
        
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_basic():
    """CLI"""
    print("\n CLI...")
    
    try:
        from src.cli import app
        print(" CLI")
        
        # 
        from src.config import DeepSearchConfig
        test_config = DeepSearchConfig(
            headless=True,
            topk=1,
            search_engine="duckduckgo"
        )
        print(f" : {test_config.search_engine}")
        
        return True
        
    except Exception as e:
        print(f" CLI: {e}")
        return False


def test_api_basic():
    """API"""
    print("\n API...")
    
    try:
        from src.api import app as api_app
        print(" API")
        return True
        
    except Exception as e:
        print(f" API: {e}")
        return False


if __name__ == "__main__":
    print(" DeepSearch  ()")
    print("="*40)
    
    success = True
    
    # 
    if not test_core_modules():
        success = False
    
    # CLI
    if not test_cli_basic():
        success = False
    
    # API
    if not test_api_basic():
        success = False
    
    if success:
        print("\n ")
    else:
        print("\n ")