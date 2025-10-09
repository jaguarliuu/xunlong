"""TODO: Add docstring."""

def test_imports():
    """TODO: Add docstring."""
    print(" ...")
    
    try:
        import sys
        print(f" Python: {sys.version_info.major}.{sys.version_info.minor}")
        
        import playwright
        try:
            from playwright import __version__ as pw_version
            print(f" Playwright: {pw_version}")
        except ImportError:
            print(" Playwright")
        
        from src.config import DeepSearchConfig
        print(" ")
        
        config = DeepSearchConfig()
        print(f" : {config.search_engine}, topk={config.topk}")
        
        from src.models import SearchResult, PageExtract
        print(" ")
        
        from src.searcher import DuckDuckGoSearcher
        print(" ")
        
        print("\n ")
        return True
        
    except Exception as e:
        print(f" : {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cli_help():
    """CLI"""
    print("\n CLI...")
    try:
        from src.cli import app
        print(" CLI")
        return True
    except Exception as e:
        print(f" CLI: {e}")
        return False


if __name__ == "__main__":
    print(" DeepSearch ")
    print("="*40)
    
    success = test_imports()
    if success:
        test_cli_help()
        print("\n ")
        print("\n :")
        print("python main.py search \"GitHub\" --topk 1 --verbose")
    else:
        print("\n ")