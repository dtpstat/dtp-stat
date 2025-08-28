import os
import sys
from pathlib import Path
import django
import fcntl
from django.core.management import call_command

# Путь к файлу-флагу (можно переопределить через MIGRATIONS_FLAG_PATH)
# По умолчанию используем каталог состояния приложения внутри контейнера
MIGRATIONS_FLAG_PATH = os.environ.get(
    "MIGRATIONS_FLAG_PATH",
    "/var/run/dtpstat/.migrations_done",
)
MIGRATIONS_LOCK_PATH = os.environ.get(
    "MIGRATIONS_LOCK_PATH",
    f"{MIGRATIONS_FLAG_PATH}.lock",
)
FLAG_FILE = Path(MIGRATIONS_FLAG_PATH)
LOCK_FILE = Path(MIGRATIONS_LOCK_PATH)

# Настройка Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dtpstat.settings")
django.setup()

# Проверяем, был ли уже первый запуск
if not FLAG_FILE.exists():
    print("Первый запуск контейнера: выполняем миграции...")
    # Гарантируем наличие каталога для флага/лока заранее
    FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(LOCK_FILE, "w") as lock_fp:
            fcntl.flock(lock_fp, fcntl.LOCK_EX)
            # Повторная проверка под эксклюзивной блокировкой
            if FLAG_FILE.exists():
                print("Миграции уже применены другим процессом, пропускаем.")
            else:
                call_command("migrate", interactive=False)
                print("Миграции применены.")
                FLAG_FILE.touch()  # создаём флаг
    except Exception as e:
        import traceback
        print("Ошибка при применении миграций:", e)
        traceback.print_exc()
        sys.exit(1)
else:
    print("Миграции уже применены, пропускаем.")
