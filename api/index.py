import sys
import os

# Add parent directory to sys.path so app.py is importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel WSGI entry point
app = app
