import re
import time
from datetime import datetime, timedelta

import requests

from config import settings


# --- ЗАПРОС К VK API ---
def vk_request(url, params, token):
    headers = {"Authorization": f"Bearer {token}"}
    for attempt in range(1, 4):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15).json()
        except requests.RequestException as e:
            print(f"⚠️ Сетевая ошибка: {e}. Повтор через 5 сек...")
            time.sleep(5)
            continue

        if "error" not in response:
            return response

        error = response["error"]
        code, msg = error["error_code"], error["error_msg"]

        if code == 9:  # Flood control
            wait = 60 * attempt
            print(f"⏳ Flood control. Попытка {attempt}/3. Ждём {wait} сек...")
            time.sleep(wait)
            continue
        if code == 6:  # Too many requests per second
            print("⏳ Слишком часто. Пауза 3 сек...")
            time.sleep(3)
            continue

        print(f"❌ Ошибка VK API: {code} — {msg}")
        return None

    print("❌ Не удалось выполнить запрос после всех попыток.")
    return None


# --- СБОР ПОСТОВ ЗА НЕДЕЛЮ ---
def get_posts_for_week(owner_id, token, days):
    url = "https://api.vk.com/method/wall.get"
    week_ago = datetime.now() - timedelta(days=days)

    all_posts = []
    offset = 0
    count = 100

    while True:
        params = {
            "owner_id": owner_id,
            "count": count,
            "offset": offset,
            "v": settings.vk_api_version,
        }
        response = vk_request(url, params, token)
        if response is None:
            break

        items = response["response"]["items"]
        if not items:
            break

        stop = False
        for post in items:
            if post.get("is_pinned"):
                continue

            post_date = datetime.fromtimestamp(post["date"])
            if post_date >= week_ago:
                all_posts.append({
                    "date": post_date,
                    "text": post.get("text", ""),
                    "id": post["id"],
                })
            else:
                stop = True
                break

        if stop or len(items) < count:
            break

        offset += count
        time.sleep(1)

    return all_posts


# --- ОЧИСТКА ТЕКСТА ---
def clean_post_text(text):
    """Убирает ссылки, хештеги, лишние пробелы и пустые строки."""
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'\[.*?\|.*?\]', '', text)
    text = re.sub(r'\n\s*\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def load_prompt_template() -> str:
    """Читает шаблон промпта из файла."""
    path = settings.path(settings.prompt_template_file)
    if not path.exists():
        raise FileNotFoundError(
            f"Шаблон промпта не найден: {path}\n"
            f"Создайте файл {settings.prompt_template_file} с плейсхолдером {{posts_block}}"
        )
    return path.read_text(encoding="utf-8")


def build_prompt(cleaned_posts) -> str:
    """Подставляет посты в шаблон."""
    template = load_prompt_template()
    posts_block = "\n\n---\n\n".join(cleaned_posts)

    if "{posts_block}" not in template:
        raise ValueError(
            f"В шаблоне {settings.prompt_template_file} нет плейсхолдера {{posts_block}}"
        )

    # replace, а не format — чтобы не спотыкаться о другие {} в тексте
    return template.replace("{posts_block}", posts_block)

# --- СОХРАНЕНИЕ В ФАЙЛ ---
def save_prompt_to_file(prompt, filename):
    path = settings.path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(prompt)
    return path


# --- ОСНОВНАЯ ЛОГИКА (вызывается из main.py) ---
def run() -> bool:
    print(f"📥 Собираем посты из группы {settings.vk_owner_id} "
          f"за последние {settings.vk_days_back} дней...\n")

    posts = get_posts_for_week(
        settings.vk_owner_id, settings.vk_token, settings.vk_days_back
    )

    if not posts:
        print("❌ Постов за неделю не найдено или произошла ошибка.")
        return False

    posts.sort(key=lambda p: p["date"])

    cleaned_posts = []
    for p in posts:
        cleaned = clean_post_text(p["text"])
        if cleaned:
            cleaned_posts.append(cleaned)

    print(f"✅ Найдено постов: {len(posts)}, после очистки: {len(cleaned_posts)}\n")
    print("=" * 60)
    for p in posts:
        print(f"\n📅 {p['date'].strftime('%d.%m.%Y %H:%M')}")
        print(f"🔗 https://vk.com/wall{settings.vk_owner_id}_{p['id']}")
        preview = p["text"][:150]
        print(f"📝 {preview}{'...' if len(p['text']) > 150 else ''}")

    prompt = build_prompt(cleaned_posts)
    saved_path = save_prompt_to_file(prompt, settings.prompt_file)

    print("\n" + "=" * 60)
    print(f"💾 Промпт сохранён в файл: {saved_path}")
    print(f"📊 Размер промпта: {len(prompt)} символов")
    print("=" * 60)
    print("\n📄 Первые 500 символов:\n")
    print(prompt[:500] + "...")
    return True


# --- ЗАПУСК НАПРЯМУЮ ---
if __name__ == "__main__":
    run()