import argparse
import sys
import GigaChat_API
import Vk_Post_Get
import Vk_Publish_Post
from config import settings


def run_all(skip_get=False, skip_giga=False, auto_publish=False) -> bool:
    if not skip_get:
        print("\n" + "🟦 ЭТАП 1/3: Сбор постов из VK".center(60, "─"))
        if not Vk_Post_Get.run():
            return False
    else:
        print("⏭️  Пропускаем этап 1 (Vk_Post_Get)")

    if not skip_giga:
        print("\n" + "🟩 ЭТАП 2/3: GigaChat".center(60, "─"))
        if not GigaChat_API.run():
            return False
    else:
        print("⏭️  Пропускаем этап 2 (GigaChat_API)")

    print("\n" + "🟨 ЭТАП 3/3: Публикация в VK".center(60, "─"))
    return Vk_Publish_Post.run(confirm=not auto_publish)


def main():
    parser = argparse.ArgumentParser(description="Пайплайн: VK → GigaChat → VK")
    sub = parser.add_subparsers(dest="cmd")

    p_all = sub.add_parser("all", help="Полный пайплайн")
    p_all.add_argument("--skip-get", action="store_true")
    p_all.add_argument("--skip-giga", action="store_true")
    p_all.add_argument("--auto-publish", action="store_true",
                       help="Публиковать без подтверждения")

    sub.add_parser("get", help="Только Vk_Post_Get")
    sub.add_parser("giga", help="Только GigaChat_API")
    sub.add_parser("publish", help="Только Vk_Publish_Post")

    args = parser.parse_args()

    if args.cmd == "get":
        ok = Vk_Post_Get.run()
    elif args.cmd == "giga":
        ok = GigaChat_API.run()
    elif args.cmd == "publish":
        ok = Vk_Publish_Post.run()
    elif args.cmd in (None, "all"):
        ok = run_all(
            skip_get=getattr(args, "skip_get", False),
            skip_giga=getattr(args, "skip_giga", False),
            auto_publish=getattr(args, "auto_publish", False),
        )
    else:
        parser.print_help()
        sys.exit(1)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()