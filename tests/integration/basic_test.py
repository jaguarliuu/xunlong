""" - playwright"""

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


def show_next_steps():
    """TODO: Add docstring."""
    print("\n :")
    print("="*40)
    
    print("1. CLI:")
    print("   python main.py --help")
    
    print("\n2. :")
    print("   python main.py search \"GitHub\" --topk 1 --verbose")
    
    print("\n3. API:")
    print("   python run_api.py")
    
    print("\n4. :")
    print("   python examples/basic_usage.py")
    
    print("\n :")
    print("- ")
    print("- ")
    print("- ")


if __name__ == "__main__":
    print(" DeepSearch ")
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
        show_next_steps()
    else:
        print("\n ")
        print("\n :")
        print("1. : pip install -r requirements.txt")
        print("2. : python -m playwright install chromium")
        print("3. Python: python --version (3.10+)")