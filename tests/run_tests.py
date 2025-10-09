#!/usr/bin/env python3
"""
 - 

"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """"""
    print(f"\n{'='*60}")
    print(f" {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f" {description} - ")
            if result.stdout:
                print(result.stdout)
        else:
            print(f" {description} - ")
            if result.stderr:
                print(f": {result.stderr}")
            if result.stdout:
                print(f": {result.stdout}")
        return result.returncode == 0
    except Exception as e:
        print(f" {description} - : {str(e)}")
        return False

def main():
    """"""
    print("  - ")
    print("=" * 60)
    
    # 
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Python
    sys.path.insert(0, str(project_root))
    
    success_count = 0
    total_count = 0
    
    # 
    print("\n ...")
    unit_tests = [
        ("python tests/unit/minimal_test.py", ""),
        ("python tests/unit/simple_test.py", ""),
        ("python tests/unit/test_agents.py", ""),
        ("python tests/unit/test_simple_search.py", ""),
    ]
    
    for cmd, desc in unit_tests:
        total_count += 1
        if run_command(cmd, desc):
            success_count += 1
    
    # 
    print("\n ...")
    integration_tests = [
        ("python tests/integration/basic_test.py", ""),
        ("python tests/integration/basic_test_fixed.py", ""),
        ("python tests/integration/debug_search.py", ""),
        ("python tests/integration/test_deepsearch.py", ""),
        ("python tests/integration/test_fixed_search.py", ""),
        ("python tests/integration/test_headless_issue.py", ""),
        ("python tests/integration/test_system_integration.py", ""),
    ]
    
    for cmd, desc in integration_tests:
        total_count += 1
        if run_command(cmd, desc):
            success_count += 1
    
    # 
    print(f"\n{'='*60}")
    print(" ")
    print(f"{'='*60}")
    print(f": {total_count}")
    print(f": {success_count}")
    print(f": {total_count - success_count}")
    print(f": {success_count/total_count*100:.1f}%")
    
    if success_count == total_count:
        print(" ")
        return 0
    else:
        print("  ")
        return 1

if __name__ == "__main__":
    sys.exit(main())