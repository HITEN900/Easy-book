import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybook.settings')
django.setup()

from apps.accounts.models import User

def create_superuser():
    # Delete existing admin if exists
    User.objects.filter(username='admin').delete()
    print("✓ Existing admin deleted")
    
    # Create new superuser
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        phone='9999999999',
        first_name='Admin',
        last_name='User'
    )
    
    print("\n" + "="*50)
    print("✅ SUPERUSER CREATED SUCCESSFULLY!")
    print("="*50)
    print(f"Username: admin")
    print(f"Password: admin123")
    print(f"Email: admin@example.com")
    print(f"Phone: 9999999999")
    print("="*50)
    
    return admin

if __name__ == '__main__':
    create_superuser()