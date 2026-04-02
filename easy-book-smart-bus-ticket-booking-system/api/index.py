import os
import sys
from pathlib import Path

# Add the project directory to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "easybook.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Vercel expects an 'app' variable
app = application