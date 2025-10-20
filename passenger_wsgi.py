

import sys
import os

# تنظیم مسیر پروژه
sys.path.insert(0, '/home/mykamani/fastfood-demo.mykaman.ir/Seketala_Kitchen_Flow')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_management.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
