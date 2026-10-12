import re

from gigachat import GigaChat

from config import settings


def read_from_file(filename):
    path = settings.path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def save_to_file(text, filename):
    path = settings.path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def strip_markdown(text):
    """Убирает Markdown-разметку: #, ##, **, *, `_, > и т.д."""
    text = re.sub(r'^\s*#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    text = re.sub(r'^\s*>\s?', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[-*+]\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def ask_gigachat(prompt, credentials, model, base_url, verify_ssl):
    giga = GigaChat(
        base_url=base_url,
        credentials=credentials,
        model=model,
        verify_ssl_certs=verify_ssl,
    )
    response = giga.chat(prompt)
    return response.choices[0].message.content


# --- ОСНОВНАЯ ЛОГИКА (вызывается из main.py) ---
def run() -> bool:
    print(f"📖 Читаем промпт из файла: {settings.prompt_file}")

    try:
        prompt = read_from_file(settings.prompt_file)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        print("💡 Сначала запустите Vk_Post_Get.py, чтобы создать этот файл.")
        return False

    print(f"✅ Промпт загружен: {len(prompt)} символов")
    print("📤 Отправляем в GigaChat...\n")

    try:
        answer = ask_gigachat(
            prompt,
            credentials=settings.giga_credentials,
            model=settings.giga_model,
            base_url=settings.giga_base_url,
            verify_ssl=settings.giga_verify_ssl,
        )
    except Exception as e:
        print(f"❌ Ошибка GigaChat: {e}")
        return False

    answer_clean = strip_markdown(answer)
    result_path = save_to_file(answer_clean, settings.result_file)

    print("=" * 60)
    print(f"✅ Сводка сохранена: {result_path}")
    print(f"📊 Размер ответа: {len(answer_clean)} символов")
    print("=" * 60)
    print("\n📄 Сводка:\n")
    print(answer_clean)
    return True


# --- ЗАПУСК НАПРЯМУЮ ---
if __name__ == "__main__":
    run()