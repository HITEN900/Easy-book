import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybook.settings')
django.setup()

from apps.accounts.models import User

if not User.objects.filter(username='hiten').exists():
    User.objects.create_superuser(
        username='hiten',
        email='mohantyhiten579@gmail.com',
        password='admin123'  # Change this to your desired password
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists.")