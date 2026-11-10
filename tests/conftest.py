import os
import sys

# app.py loads models/ with relative paths, so run from the repo root.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
