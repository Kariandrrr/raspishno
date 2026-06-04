import os
import subprocess
import sys

from dotenv import load_dotenv

load_dotenv(
    'sync_config.env'
    )

CLOUD_DB = os.getenv(
    'CLOUD_DB'
    )
LOCAL_DB = os.getenv(
    'LOCAL_DB'
    )

if not CLOUD_DB:
    print(
        "❌ Ошибка: CLOUD_DB не найдена в sync_config.env"
        )
    sys.exit(
        1
        )

print(
    "✅ Настройки загружены"
    )


def sync_to_cloud():
    print(
        "\n📤 Отправка данных из Docker в Aiven..."
        )

    print(
        "  → Экспорт данных из Docker..."
        )
    result = subprocess.run(
        "docker exec postgres pg_dump -U rapishno_user -d rapishno_db --data-only --inserts",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"❌ Ошибка экспорта: {result.stderr}"
            )
        return

    sql_data = result.stdout

    if not sql_data.strip():
        print(
            "⚠️ Нет данных для экспорта"
            )
        return

    with open(
            "_temp_sync.sql",
            "w",
            encoding="utf-8"
            ) as f:
        f.write(
            sql_data
            )

    print(
        "  → Импорт в Aiven..."
        )
    result = subprocess.run(
        f'psql "{CLOUD_DB}" -f _temp_sync.sql',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"❌ Ошибка импорта: {result.stderr}"
            )
    else:
        print(
            "✅ Данные успешно отправлены в Aiven!"
            )

    os.remove(
        "_temp_sync.sql"
        )


def sync_from_cloud():
    print(
        "\n📥 Загрузка данных из Aiven в Docker..."
        )

    print(
        "  → Экспорт из Aiven..."
        )
    result = subprocess.run(
        f'pg_dump "{CLOUD_DB}" --data-only --inserts',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"❌ Ошибка экспорта: {result.stderr}"
            )
        return

    sql_data = result.stdout

    if not sql_data.strip():
        print(
            "⚠️ Нет данных в облаке"
            )
        return

    with open(
            "_temp_sync.sql",
            "w",
            encoding="utf-8"
            ) as f:
        f.write(
            sql_data
            )

    print(
        "  → Импорт в Docker..."
        )
    result = subprocess.run(
        "docker exec -i postgres psql -U rapishno_user -d rapishno_db < _temp_sync.sql",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"❌ Ошибка импорта: {result.stderr}"
            )
    else:
        print(
            "✅ Данные успешно загружены в Docker!"
            )

    os.remove(
        "_temp_sync.sql"
        )


def sync_full_to_cloud():
    print(
        "\n📦 Полная копия Docker → Aiven..."
        )

    print(
        "  → Экспорт полной БД из Docker..."
        )
    result = subprocess.run(
        "docker exec postgres pg_dump -U rapishno_user -d rapishno_db --clean --if-exists",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"❌ Ошибка экспорта: {result.stderr}"
            )
        return

    sql_data = result.stdout

    if not sql_data.strip():
        print(
            "⚠️ Нет данных"
            )
        return

    with open(
            "_temp_full.sql",
            "w",
            encoding="utf-8"
            ) as f:
        f.write(
            sql_data
            )

    print(
        "  → Импорт в Aiven (с перезаписью)..."
        )
    result = subprocess.run(
        f'psql "{CLOUD_DB}" -f _temp_full.sql',
        shell=True,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(
            f"❌ Ошибка импорта: {result.stderr}"
            )
    else:
        print(
            "✅ Полная копия завершена!"
            )

    os.remove(
        "_temp_full.sql"
        )


if __name__ == "__main__":
    print(
        "\n" + "=" * 50
        )
    print(
        "СИНХРОНИЗАЦИЯ БАЗЫ ДАННЫХ"
        )
    print(
        "=" * 50
        )
    print(
        "1. Отправить ТОЛЬКО ДАННЫЕ из Docker в Aiven"
        )
    print(
        "2. Забрать ТОЛЬКО ДАННЫЕ из Aiven в Docker"
        )
    print(
        "3. Полная копия (структура + данные) из Docker в Aiven"
        )
    print(
        "4. Выйти"
        )

    choice = input(
        "\nВыбери действие (1-4): "
        )

    if choice == "1":
        sync_to_cloud()
    elif choice == "2":
        sync_from_cloud()
    elif choice == "3":
        confirm = input(
            "⚠️ Это перезапишет облачную БД! Продолжить? (y/n): "
            )
        if confirm.lower() == 'y':
            sync_full_to_cloud()
    else:
        print(
            "Пока!"
            )