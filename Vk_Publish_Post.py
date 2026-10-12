import requests

from config import settings


def read_from_file(filename):
    path = settings.path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def publish_post(owner_id, message, token):
    """Публикует пост от имени сообщества."""
    url = "https://api.vk.com/method/wall.post"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "owner_id": owner_id,
        "from_group": 1,
        "message": message,
        "v": settings.vk_api_version,
    }

    response = requests.get(url, headers=headers, params=params, timeout=15).json()

    if "error" in response:
        error = response["error"]
        print(f"❌ Ошибка VK API: {error['error_code']} — {error['error_msg']}")
        return None

    return response["response"]["post_id"]


# --- ОСНОВНАЯ ЛОГИКА (вызывается из main.py) ---
def run(confirm: bool | None = None) -> bool:
    """
    confirm=None  → берём из settings.publish_require_confirm
    confirm=True  → спросить y/n
    confirm=False → публиковать сразу
    """
    print(f"📖 Читаем сводку из файла: {settings.result_file}")

    try:
        summary = read_from_file(settings.result_file)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Сначала запустите GigaChat_API.py, чтобы создать этот файл.")
        return False

    print(f"✅ Сводка загружена: {len(summary)} символов\n")
    print("📄 Предпросмотр:\n")
    print(summary[:500] + "..." if len(summary) > 500 else summary)
    print("\n" + "=" * 60)

    need_confirm = settings.publish_require_confirm if confirm is None else confirm
    if need_confirm:
        answer = input("📤 Опубликовать этот пост? (y/n): ").strip().lower()
        if answer != "y":
            print("❌ Публикация отменена.")
            return False

    print("\n📤 Публикуем...\n")
    post_id = publish_post(settings.vk_group_id, summary, settings.vk_community_token)

    if post_id:
        print("=" * 60)
        print("✅ Пост опубликован!")
        print(f"🔗 https://vk.com/wall{settings.vk_group_id}_{post_id}")
        return True
    else:
        print("❌ Не удалось опубликовать пост.")
        return False


# --- ЗАПУСК НАПРЯМУЮ ---
if __name__ == "__main__":
    run()