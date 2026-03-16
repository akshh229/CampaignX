#!/usr/bin/env python3
"""Test SqliteSaver import paths"""

print("Testing SqliteSaver imports...\n")

# Test 1: Original import
try:
    from langgraph.checkpoint.sqlite import SqliteSaver
    print("✓ langgraph.checkpoint.sqlite.SqliteSaver works")
except ImportError as e:
    print(f"✗ langgraph.checkpoint.sqlite: {e}")

# Test 2: Alternative: langgraph_checkpoint
try:
    from langgraph_checkpoint.sqlite import SqliteSaver
    print("✓ langgraph_checkpoint.sqlite.SqliteSaver works")
except ImportError as e:
    print(f"✗ langgraph_checkpoint.sqlite: {e}")

# Test 3: Check what's in langgraph
try:
    import langgraph
    print(f"\n✓ langgraph version: {langgraph.__version__ if hasattr(langgraph, '__version__') else 'unknown'}")
    if hasattr(langgraph, 'checkpoint'):
        print("  → Has checkpoint module")
    else:
        print("  → NO checkpoint module")
except Exception as e:
    print(f"✗ langgraph: {e}")

# Test 4: Check what's in langgraph_checkpoint
try:
    import langgraph_checkpoint
    print(f"\n✓ langgraph_checkpoint found")
    print(f"  → Dir: {[x for x in dir(langgraph_checkpoint) if not x.startswith('_')][:5]}")
except Exception as e:
    print(f"✗ langgraph_checkpoint: {e}")

# Test 5: List available checkpoint implementations
print("\n--- Available checkpoint implementations ---")
try:
    import langgraph.checkpoint as cp
    print(f"✓ From langgraph.checkpoint: {[x for x in dir(cp) if not x.startswith('_')]}")
except:
    try:
        import langgraph_checkpoint as cp
        print(f"✓ From langgraph_checkpoint: {[x for x in dir(cp) if not x.startswith('_')]}")
    except Exception as e:
        print(f"✗ Could not find checkpoint module: {e}")

print("\nConclusion: See above for working import path")
