import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easybook.settings')
django.setup()

from apps.accounts.models import User

print("="*50)
print("🚀 IMPORTING USERS...")
print("="*50)

try:
    # Read the JSON file
    with open('users.json', 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    for user_data in users:
        username = user_data.get('username')
        password = user_data.get('password')
        email = user_data.get('email')
        phone = user_data.get('phone')
        is_superuser = user_data.get('is_superuser', False)
        user_type = user_data.get('user_type', 'customer')
        
        # Check if user exists and delete
        if User.objects.filter(username=username).exists():
            User.objects.filter(username=username).delete()
            print(f"✓ Existing user '{username}' deleted")
        
        # Create user based on type
        if is_superuser:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                phone=phone
            )
            print(f"✅ Superuser created: {username} / {password}")
        else:
            User.objects.create_user(
                username=username,
                email=email,
                password=password,
                phone=phone,
                user_type=user_type
            )
            print(f"✅ User created: {username} / {password}")

    print("\n" + "="*50)
    print("✅ ALL USERS IMPORTED SUCCESSFULLY!")
    print("="*50)
    print("\n📋 USER CREDENTIALS:")
    print("-"*40)
    print("Admin   : admin / admin123")
    print("Customer: customer / customer123")
    print("Owner   : owner / owner123")
    print("="*50)

except FileNotFoundError:
    print("❌ Error: users.json file not found!")
except json.JSONDecodeError as e:
    print(f"❌ Error: Invalid JSON format - {e}")
except Exception as e:
    print(f"❌ Error: {e}")