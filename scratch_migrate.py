import os
import django
from django.core.management import call_command

os.environ["DATABASE_URL"] = "postgresql://postgres:YarnByMansi@db.duyliqgieyqqrtvhevzc.supabase.co:5432/postgres"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yarned_with_love.settings")
django.setup()

print("Running migrations...")
call_command("migrate")
print("Migrations complete!")
