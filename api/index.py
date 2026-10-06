import os
import sys

# Add project root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app

# Export app as both `app` and `handler` for maximum Vercel compatibility
handler = app
