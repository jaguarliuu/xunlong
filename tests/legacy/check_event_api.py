#!/usr/bin/env python3
"""create_event"""

import inspect
from dotenv import load_dotenv
load_dotenv()

try:
    from langfuse import Langfuse
    
    # create_event
    print("create_event:")
    print(inspect.signature(Langfuse.create_event))
    
    # start_observation
    print("\nstart_observation:")
    print(inspect.signature(Langfuse.start_observation))
    
    # start_generation
    print("\nstart_generation:")
    print(inspect.signature(Langfuse.start_generation))
    
    # start_span
    print("\nstart_span:")
    print(inspect.signature(Langfuse.start_span))
    
except Exception as e:
    print(f": {e}")
    import traceback
    traceback.print_exc()