"""conftest.py — automatically adds project root to sys.path for pytest."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
