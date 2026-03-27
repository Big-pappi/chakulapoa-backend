"""
WSGI config for Chakula Poa project.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chakula_poa.settings')
application = get_wsgi_application()
