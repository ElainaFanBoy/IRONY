import json
import hashlib
from pathlib import Path


dir_path = Path(__file__).parent


def update():
    resource_list = []
    for file in (dir_path / "images").rglob("*"):
        if not file.is_file():
            continue
        resource_list.append(
            {
                "path": str(file.relative_to(dir_path).as_posix()),
                "hash": hashlib.md5(file.read_bytes()).hexdigest(),
            }
        )
    resource_list.sort(key=lambda i: i["path"])
    with open(dir_path / "resource_list.json", "w", encoding="utf-8") as f:
        json.dump(resource_list, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    update()
