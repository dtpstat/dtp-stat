import os
import sys
from pathlib import Path
import django
from django.core.management import call_command

#№Путь к файлу-флагу (можно переопределить через MIGRATIONS_FLAG_PATH)
# По умолчанию используем каталог состояния приложения внутри контейнера
FLAG_FILE = Path(os.environ.get("MIGRATIONS_FLAG_PATH"))

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dtpstat.settings")
django.setup()

# Проверяем, был ли уже первый запуск
if not FLAG_FILE.exists():
    print("Первый запуск контейнера: выполняем миграции...")
    try:
        call_command("migrate", interactive=False)
        print("Миграции применены.")
        FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)  # гарантируем каталог
        FLAG_FILE.touch()  # создаём флаг
    except Exception as e:
        print("Ошибка при применении миграций:", e)
        sys.exit(1)
else:
    print("Миграции уже применены, пропускаем.")