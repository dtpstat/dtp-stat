import os
import sys
from pathlib import Path
import django
from django.core.management import call_command

# Путь к файлу-флагу в volume
FLAG_FILE = Path("/var/lib/postgresql/data/.migrations_done")

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dtpstat.settings")
django.setup()

# Проверяем, был ли уже первый запуск
if not FLAG_FILE.exists():
    print("Первый запуск контейнера: выполняем миграции...")
    try:
        call_command("migrate", interactive=False)
        print("Миграции применены.")
        FLAG_FILE.touch()  # создаём флаг
    except Exception as e:
        print("Ошибка при применении миграций:", e)
        sys.exit(1)
else:
    print("Миграции уже применены, пропускаем.")